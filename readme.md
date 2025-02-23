### Team Members:
- Yufan Du  
- Yong Wu  
- Ziwei Liu  

### Project Links:  
- **Video:** https://drive.google.com/file/d/1JWWri-UmtBEDAd0vrF3xiGw3h5f8Lkmu/view?usp=share_link 
- **Slides:** https://docs.google.com/presentation/d/108hxYhI5OZYWqKG6CjXafHfvUmXHKBv88aUsDPe3Xvc/edit?usp=sharing

---

### File Structure Overview:  

#### **Approximate Folder:**  
This folder contains Python implementations for simulating the behavior of exact and approximate multipliers. The script `Find_best_approximate.py` utilizes theTPE algorithm  to explore the best approximation methods. Additionally, the `core` subfolder and `approximate_logic.py` simulate the multiplier environment.  

#### **Csv_generator Folder:**  
This folder generates CSV files based on the implemented approximate multipliers. These CSV files are then used in subsequent applications for computation.  

#### **Image_classification Folder:**  
This section explores the impact of different approximation algorithms on image classification. Various datasets and neural network models are used to evaluate the classification accuracy under approximate computations.  

#### **Image_processing Folder:**  
This folder examines how different approximation algorithms affect image processing tasks, including **sharpening, edge detection, and image blending**. The goal is to assess the trade-offs between computational efficiency and image quality when using approximate arithmetic.

#### **Atomic_config Folder:**

This folder is dedicated to analyzing the **energy consumption** of the proposed approximate multipliers, providing insights into their power efficiency compared to exact multipliers.