import csv
import numpy as np
import matplotlib.pyplot as plt
from skimage import data, color
from skimage.transform import resize
from tqdm import tqdm

from PIL import Image
class LUTImageProcessor:
    """
    A class that demonstrates how to perform image processing operations
    (sharpening, edge detection, blending) by using a LUT-based multiplication
    approach for integer arithmetic in the range [-128, 127].
    """

    def __init__(self, lut_file="exact_multiplication_LUT.csv"):
        """
        Initialize the LUTImageProcessor with a path to the CSV file
        containing the multiplication LUT (look-up table).

        :param lut_file: The CSV file path containing the LUT data.
        """
        self.lut_file = lut_file
        self.lut_dict = self.load_lut(lut_file)

    def load_lut(self, csv_file):
        """
        Load the integer multiplication LUT from a CSV file.

        The CSV is expected to have 3 columns: a, b, product.
        where -128 <= a, b <= 127 and product = a*b, also in the range [-128, 127].

        :param csv_file: The path to the LUT CSV file.
        :return: A dictionary mapping (a, b) -> product.
        """
        lut_dict = {}
        with open(csv_file, 'r') as f:
            # Skip header if any
            next(f)
            for line in f:
                a_str, b_str, product_str = line.strip().split(',')
                a, b, product = int(a_str), int(b_str), int(product_str)
                lut_dict[(a, b)] = product
        return lut_dict

    def lut_multiply(self, a, b):
        """
        Multiply two integers using the loaded LUT dictionary.
        Assumes a and b are already clipped to [-128, 127].

        :param a: An integer in the range [-128, 127].
        :param b: An integer in the range [-128, 127].
        :return: The product as specified by the LUT dictionary (also in [-128, 127]).
        """
        return self.lut_dict[(a, b)]

    def scale_to_int8(self, image):
        """
        Scale an image from [0, 255] into the range [-128, 127].
        Internally uses int16 to reduce overflow risk, but values
        should remain within [-128, 127].

        :param image: A numpy array with values in [0, 255].
                      Can be grayscale or RGB.
        :return: A numpy array of dtype int16, with values mapped to [-128, 127].
        """
        img = np.array(image, dtype=np.float32)
        img_norm = img / 255.0  # Scale to [0, 1]
        img_scaled = img_norm * 255 - 128  # Shift to [-128, 127]
        return img_scaled.astype(np.int16)

    def convolve_2d_lut(self, image_int8, kernel):
        """
        Perform 2D convolution on a single-channel image using the LUT-based multiplication.
        Zero-padding is used. The multiplication is looked up from the LUT, and additions
        are done in regular integer arithmetic.

        :param image_int8: A 2D numpy array (H, W) in the range [-128, 127] (dtype int16).
        :param kernel: A 2D numpy array (kh, kw) (the convolution kernel).
        :return: The convolution result as a numpy array, same shape as image_int8 (H, W).
        """
        h, w = image_int8.shape
        kh, kw = kernel.shape

        # Determine padding needed to keep the output size same
        pad_h = kh // 2
        pad_w = kw // 2

        # Zero-padding
        padded = np.zeros((h + 2 * pad_h, w + 2 * pad_w), dtype=np.int16)
        padded[pad_h:pad_h + h, pad_w:pad_w + w] = image_int8

        out = np.zeros((h, w), dtype=np.int16)

        for i in range(h):
            for j in range(w):
                val = 0
                # Convolution sum
                for ki in range(kh):
                    for kj in range(kw):
                        k_val = kernel[ki, kj]
                        px_val = padded[i + ki, j + kj]

                        # Clip both kernel value and pixel value to [-128, 127]
                        px_val = max(min(px_val, 127), -128)
                        k_val = max(min(k_val, 127), -128)

                        # LUT multiplication
                        prod = self.lut_multiply(px_val, k_val)
                        val += prod

                # Clip final sum to [-128, 127]
                val = max(min(val, 127), -128)
                out[i, j] = val

        return out

    def sharpen_color_image(self, image, kernel):
        """
        Apply a sharpening (or any other filter) to an RGB image
        by convolving each channel separately using the LUT-based multiplication.

        :param image: A numpy array of shape (H, W, 3) in [-128, 127], dtype int16.
        :param kernel: A 2D numpy array for the convolution kernel, e.g. a sharpen kernel.
        :return: The filtered image with the same shape (H, W, 3), dtype int16.
        """
        # Split into R, G, B channels
        r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]

        # Convolve each channel with the kernel
        r_sharpened = self.convolve_2d_lut(r, kernel)
        g_sharpened = self.convolve_2d_lut(g, kernel)
        b_sharpened = self.convolve_2d_lut(b, kernel)

        # Stack channels back into an RGB image
        sharpened_image = np.stack([r_sharpened, g_sharpened, b_sharpened], axis=-1)
        return sharpened_image

    def blend_images_lut(self, img1_int8, img2_int8, alpha):
        """
        Blend two RGB images by computing alpha * img1 + (1 - alpha) * img2
        using the LUT-based multiplication approach.

        :param img1_int8: First image, shape (H, W, 3), values in [-128, 127].
        :param img2_int8: Second image, shape (H, W, 3), values in [-128, 127].
        :param alpha: A float in [0,1] controlling the blend ratio.
        :return: The blended image (H, W, 3), dtype int16, still in [-128, 127].
        """
        # Convert alpha to integer in the range [0, 127]
        alpha_int = int(alpha * 127)
        inv_alpha_int = 127 - alpha_int  # for (1 - alpha)

        h, w, c = img1_int8.shape
        out = np.zeros_like(img1_int8, dtype=np.int16)

        for i in range(h):
            for j in range(w):
                for ch in range(c):
                    val1 = img1_int8[i, j, ch]
                    val2 = img2_int8[i, j, ch]

                    # Clip image values to [-128, 127]
                    val1 = max(min(val1, 127), -128)
                    val2 = max(min(val2, 127), -128)

                    # LUT-based multiplication
                    part1 = self.lut_multiply(val1, alpha_int)
                    part2 = self.lut_multiply(val2, inv_alpha_int)

                    # Sum up the weighted channels, then integer division by 127
                    temp_sum = part1 + part2
                    blended_val = temp_sum // 127  # approximate division by 127

                    # Clip result
                    blended_val = max(min(blended_val, 127), -128)
                    out[i, j, ch] = blended_val

        return out

    def sharpening(self):
        """
        Demonstrates sharpening on sample images (astronaut and rocket) from skimage.
        Shows original vs. sharpened results.
        """
        # Load sample images from skimage
        img_astronaut = data.astronaut()
        img_rocket = data.rocket()
        img_coffee = data.coffee()

        # Scale to [-128, 127]
        img_astronaut_scaled = self.scale_to_int8(img_astronaut)
        img_rocket_scaled = self.scale_to_int8(img_rocket)
        img_coffee_scaled = self.scale_to_int8(img_coffee)

        # Define a basic sharpening kernel
        sharpen_kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ], dtype=np.int16)

        # Apply sharpening via LUT-based convolution
        astronaut_sharpened = self.sharpen_color_image(img_astronaut_scaled, sharpen_kernel)
        rocket_sharpened = self.sharpen_color_image(img_rocket_scaled, sharpen_kernel)
        coffee_sharpened = self.sharpen_color_image(img_coffee_scaled, sharpen_kernel)

        # Convert back to [0, 255] for display
        astronaut_sharpened_disp = (astronaut_sharpened + 128).clip(0, 255).astype(np.uint8)
        rocket_sharpened_disp = (rocket_sharpened + 128).clip(0, 255).astype(np.uint8)
        coffee_sharpened_disp = (coffee_sharpened + 128).clip(0, 255).astype(np.uint8)

        # Visualization
        fig, axes = plt.subplots(3, 2, figsize=(10, 10))
        ax = axes.ravel()

        ax[0].set_title("Original Astronaut")
        ax[0].imshow(img_astronaut.clip(0, 255).astype(np.uint8))

        ax[1].set_title("Sharpened Astronaut")
        ax[1].imshow(astronaut_sharpened_disp)

        ax[2].set_title("Original Rocket")
        ax[2].imshow(img_rocket.clip(0, 255).astype(np.uint8))

        ax[3].set_title("Sharpened Rocket")
        ax[3].imshow(rocket_sharpened_disp)

        ax[4].set_title("Original Coffee")
        ax[4].imshow(img_coffee.clip(0, 255).astype(np.uint8))

        ax[5].set_title("Sharpened Coffee")
        ax[5].imshow(coffee_sharpened_disp)



        # 保存单独的图像
        Image.fromarray(astronaut_sharpened_disp).save(f"img_res/{self.lut_file}sharpened_astronaut.png")
        Image.fromarray(rocket_sharpened_disp).save(f"img_res/{self.lut_file}sharpened_rocket.png")
        Image.fromarray(coffee_sharpened_disp).save(f"img_res/{self.lut_file}sharpened_coffee.png")

        for a in ax:
            a.axis('off')
        plt.tight_layout()
        plt.show()

    def edge_detection(self):
        """
        Demonstrates edge detection on sample images (astronaut and rocket) by using
        a Sobel-like kernel and LUT-based convolution.
        Shows original vs. edge-detected results.
        """
        # Load sample images from skimage
        img_astronaut = data.astronaut()
        img_rocket = data.rocket()
        img_coffee = data.coffee()

        # Scale to [-128, 127]
        img_astronaut_scaled = self.scale_to_int8(img_astronaut)
        img_rocket_scaled = self.scale_to_int8(img_rocket)
        img_coffee_scaled = self.scale_to_int8(img_coffee)

        # Define a vertical Sobel-like kernel
        edge_kernel = np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ], dtype=np.int16)

        # Apply edge detection using LUT-based convolution
        astronaut_edges = self.sharpen_color_image(img_astronaut_scaled, edge_kernel)
        rocket_edges = self.sharpen_color_image(img_rocket_scaled, edge_kernel)
        coffee_sharpened = self.sharpen_color_image(img_coffee_scaled, edge_kernel)

        # Convert back to [0, 255] for display
        astronaut_edges_disp = (astronaut_edges + 128).clip(0, 255).astype(np.uint8)
        rocket_edges_disp = (rocket_edges + 128).clip(0, 255).astype(np.uint8)
        coffee_sharpened_disp = (coffee_sharpened + 128).clip(0, 255).astype(np.uint8)

        # Visualization
        fig, axes = plt.subplots(3, 2, figsize=(10, 10))
        ax = axes.ravel()

        ax[0].set_title("Original Astronaut")
        ax[0].imshow(img_astronaut.clip(0, 255).astype(np.uint8))

        ax[1].set_title("Edge Detection Astronaut")
        ax[1].imshow(astronaut_edges_disp)

        ax[2].set_title("Original Rocket")
        ax[2].imshow(img_rocket.clip(0, 255).astype(np.uint8))

        ax[3].set_title("Edge Detection Rocket")
        ax[3].imshow(rocket_edges_disp)

        ax[4].set_title("Original Coffee")
        ax[4].imshow(img_coffee.clip(0, 255).astype(np.uint8))

        ax[5].set_title("Sharpened Coffee")
        ax[5].imshow(coffee_sharpened_disp)

        Image.fromarray(astronaut_edges_disp).save(f"img_res/{self.lut_file}edge_detection_astronaut.png")
        Image.fromarray(rocket_edges_disp).save(f"img_res/{self.lut_file}edge_detection_rocket.png")
        Image.fromarray(coffee_sharpened_disp).save(f"img_res/{self.lut_file}edge_detection_coffee.png")

        for a in ax:
            a.axis('off')
        plt.tight_layout()
        plt.show()

    def blend_images(self, alpha=0.5):
        """
        Demonstrates blending of sample images using alpha blend (alpha in [0,1]).
        Uses LUT-based multiplication to compute alpha*img1 + (1 - alpha)*img2.

        :param alpha: Blend ratio (float in [0,1]). Default is 0.5.
        """
        # 1) Load sample images
        img_astronaut = data.astronaut()
        img_retina = data.retina()

        # Scale the astronaut image to [-128, 127]
        img_astronaut_scaled = self.scale_to_int8(img_astronaut)

        # Resize the retina image to a common size, e.g., 512x512
        img_retina_resized = resize(img_retina, (512, 512), anti_aliasing=True)
        # Convert [0,1] to [0,255]
        img_retina_resized = (img_retina_resized * 255).astype(np.uint8)
        # Scale to [-128, 127]
        img_retina_scaled = self.scale_to_int8(img_retina_resized)

        # Blend them
        blended_image1 = self.blend_images_lut(img_astronaut_scaled, img_retina_scaled, alpha)
        blended_image1_disp = (blended_image1 + 128).clip(0, 255).astype(np.uint8)

        # 2) Load rocket and coffee
        img_rocket = data.rocket()
        img_coffee = data.coffee()

        # 3) Resize both to the same shape (512, 512)
        rocket_resized = resize(img_rocket, (512, 512), anti_aliasing=True)
        coffee_resized = resize(img_coffee, (512, 512), anti_aliasing=True)

        # Convert back to [0,255] and scale to [-128,127]
        rocket_resized = (rocket_resized * 255).astype(np.uint8)
        coffee_resized = (coffee_resized * 255).astype(np.uint8)

        rocket_scaled = self.scale_to_int8(rocket_resized)
        coffee_scaled = self.scale_to_int8(coffee_resized)

        # 4) Blend them
        blended_image2 = self.blend_images_lut(rocket_scaled, coffee_scaled, alpha)
        blended_image2_disp = (blended_image2 + 128).clip(0, 255).astype(np.uint8)

        blended_image3 = self.blend_images_lut(img_astronaut_scaled, coffee_scaled, alpha)
        blended_image3_disp = (blended_image3 + 128).clip(0, 255).astype(np.uint8)

        # Visualization
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))  # 2 rows, 3 cols
        ax = axes.ravel()

        ax[0].set_title("Original Astronaut")
        ax[0].imshow(img_astronaut.clip(0, 255).astype(np.uint8))

        ax[1].set_title("Original Retina")
        ax[1].imshow(img_retina.clip(0, 255).astype(np.uint8))

        ax[2].set_title("Original Coffee")
        ax[2].imshow(img_coffee.clip(0, 255).astype(np.uint8))

        ax[3].set_title(f"Blended Image 1 (alpha={alpha})")
        ax[3].imshow(blended_image1_disp)

        ax[4].set_title(f"Blended Image 2 (alpha={alpha})")
        ax[4].imshow(blended_image2_disp)

        ax[5].set_title(f"Blended Image 3 (alpha={alpha})")
        ax[5].imshow(blended_image3_disp)

        Image.fromarray(blended_image1_disp).save(f"img_res/{self.lut_file}blend1.png")
        Image.fromarray(blended_image2_disp).save(f"img_res/{self.lut_file}blend2.png")
        Image.fromarray(blended_image3_disp).save(f"img_res/{self.lut_file}blend3.png")

        for a in ax:
            a.axis('off')
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":

    # Example usage
    processor = LUTImageProcessor("LUT/appro1_multiplication_LUT.csv")

    # Demonstrate sharpening
    processor.sharpening()

    # Demonstrate edge detection
    processor.edge_detection()

    # Demonstrate blending with alpha=0.5
    processor.blend_images(alpha=0.5)





