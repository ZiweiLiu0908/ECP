import csv

import numpy as np


class LogicGates:
    """
    Implements basic logic gates using only NAND.
    Each static method returns 0 or 1 given two input bits (0 or 1).
    """

    @staticmethod
    def nand_gate(a, b):
        """
        Returns the NAND of two bits a and b.
        NAND = NOT(a AND b)
        :param a: bit 0 or 1
        :param b: bit 0 or 1
        :return: 0 or 1
        """
        return 1 if not (a and b) else 0

    @staticmethod
    def xor_gate(a, b):
        """
        Returns the XOR of two bits a and b, implemented using NAND gates.
        XOR = a ^ b
        :param a: bit 0 or 1
        :param b: bit 0 or 1
        :return: 0 or 1
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(a, LogicGates.nand_gate(a, b)),
            LogicGates.nand_gate(b, LogicGates.nand_gate(a, b))
        )

    @staticmethod
    def and_gate(a, b):
        """
        Returns the AND of two bits a and b, implemented using NAND gates.
        AND = a & b
        :param a: bit 0 or 1
        :param b: bit 0 or 1
        :return: 0 or 1
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(a, b),
            LogicGates.nand_gate(a, b)
        )

    @staticmethod
    def or_gate(a, b):
        """
        Returns the OR of two bits a and b, implemented using NAND gates.
        OR = a | b
        :param a: bit 0 or 1
        :param b: bit 0 or 1
        :return: 0 or 1
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(a, a),
            LogicGates.nand_gate(b, b)
        )


class Adder:
    """
    Implements half-adder and full-adder using basic logic gates.
    A half-adder adds two bits and produces a sum bit and a carry bit.
    A full-adder adds three bits (including a carry-in) and produces a sum bit and a carry-out.
    """

    @staticmethod
    def half_adder(a, b, ignore=0):
        """
        Half-Adder using XOR for the sum and AND for the carry.
        :param a: bit 0 or 1
        :param b: bit 0 or 1
        :return: (sum_bit, carry_bit)
        """
        sum_bit = LogicGates.xor_gate(a, b)
        carry = LogicGates.and_gate(a, b)

        return sum_bit, carry

    @staticmethod
    def full_adder(a, b, cin, ignore=0):
        """
        Full-Adder constructed from two half-adders and an OR gate.
        sum = (a ^ b) ^ cin
        carry_out = (a & b) | ( (a ^ b) & cin )
        :param ignore:
        :param a: bit 0 or 1
        :param b: bit 0 or 1
        :param cin: carry-in bit 0 or 1
        :return: (sum_bit, carry_out_bit)
        """
        sum1, carry1 = Adder.half_adder(a, b)
        sum_bit, carry2 = Adder.half_adder(sum1, cin)
        carry_out = LogicGates.or_gate(carry1, carry2)

        return sum_bit, carry_out


class Compressor:
    """
    Implements a 4:2 Compressor using only NAND-based logic gates.
    A 4:2 compressor compresses four input bits plus a carry-in bit
    into two output bits (sum and carry), plus an additional carry-out.
    """

    @staticmethod
    def full_adder_sum(g4, x3):
        """
        Part of the full-adder sum logic used in the compressor.
        :param g4: intermediate XOR result
        :param x3: one of the bits to be added
        :return: sum bit
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(LogicGates.nand_gate(g4, x3), g4),
            LogicGates.nand_gate(LogicGates.nand_gate(g4, x3), x3)
        )

    @staticmethod
    def full_adder_cout(x1, x2, g4, x3):
        """
        Part of the full-adder carry-out logic used in the compressor.
        :param x1: bit to add
        :param x2: bit to add
        :param g4: intermediate XOR result
        :param x3: bit to add
        :return: carry-out bit
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(x1, x2),
            LogicGates.nand_gate(g4, x3)
        )

    @staticmethod
    def carry_output(s, x4, cin):
        """
        Computes the carry output in the 4:2 compressor.
        :param s: sum bit from the first stage
        :param x4: bit to add
        :param cin: carry-in bit
        :return: carry bit
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(LogicGates.xor_gate(s, x4), cin),
            LogicGates.nand_gate(s, x4)
        )

    @staticmethod
    def sum_output(s, x4, cin):
        """
        Computes the final sum output in the 4:2 compressor.
        :param s: sum bit from the first stage
        :param x4: bit to add
        :param cin: carry-in bit
        :return: sum bit
        """
        return LogicGates.nand_gate(
            LogicGates.nand_gate(
                LogicGates.nand_gate(LogicGates.xor_gate(s, x4), cin),
                LogicGates.xor_gate(s, x4)
            ),
            LogicGates.nand_gate(
                LogicGates.nand_gate(LogicGates.xor_gate(s, x4), cin),
                cin
            )
        )

    @staticmethod
    def compressor_4_to_2(x1, x2, x3, x4, cin, ignore=0):
        """
        4:2 compressor that takes in four bits (x1, x2, x3, x4) and a carry-in (cin),
        and returns (cout, carry, sum_bit).
        :param ignore:
        :param x1: bit
        :param x2: bit
        :param x3: bit
        :param x4: bit
        :param cin: carry-in bit
        :return: (cout, carry, sum_bit)
        """
        # g4 is the XOR of x1 and x2
        g4 = LogicGates.xor_gate(x1, x2)
        # s is the sum from a partial full-adder
        s = Compressor.full_adder_sum(g4, x3)
        # cout is the carry-out from the partial full-adder
        cout = Compressor.full_adder_cout(x1, x2, g4, x3)
        # carry is an intermediate carry output
        carry = Compressor.carry_output(s, x4, cin)
        # sum_bit is the final sum output
        sum_bit = Compressor.sum_output(s, x4, cin)
        if ignore == 1:
            cout = 0
        if ignore == 2:
            carry = 0
        if ignore == 3:
            cout = 0
            carry = 0
        if ignore == 4:
            LUT_4_2 = {
                (0, 0, 0, 0, 0): (0, 0, 1),
                (0, 0, 0, 0, 1): (0, 1, 0),
                (0, 0, 0, 1, 0): (0, 1, 0),
                (0, 0, 0, 1, 1): (0, 1, 0),
                (0, 0, 1, 0, 0): (0, 0, 1),
                (0, 0, 1, 0, 1): (0, 1, 0),
                (0, 0, 1, 1, 0): (0, 1, 0),
                (0, 0, 1, 1, 1): (0, 1, 0),
                (0, 1, 0, 0, 0): (0, 0, 1),
                (0, 1, 0, 0, 1): (0, 1, 0),
                (0, 1, 0, 1, 0): (0, 1, 0),
                (0, 1, 0, 1, 1): (0, 1, 0),
                (0, 1, 1, 0, 0): (1, 0, 1),
                (0, 1, 1, 0, 1): (1, 1, 0),
                (0, 1, 1, 1, 0): (1, 0, 1),
                (0, 1, 1, 1, 1): (1, 1, 0),
                (1, 0, 0, 0, 0): (0, 0, 1),
                (1, 0, 0, 0, 1): (0, 1, 0),
                (1, 0, 0, 1, 0): (0, 1, 0),
                (1, 0, 0, 1, 1): (0, 1, 0),
                (1, 0, 1, 0, 0): (1, 0, 1),
                (1, 0, 1, 0, 1): (1, 1, 0),
                (1, 0, 1, 1, 0): (1, 0, 1),
                (1, 0, 1, 1, 1): (1, 1, 0),
                (1, 1, 0, 0, 0): (1, 0, 1),
                (1, 1, 0, 0, 1): (1, 1, 0),
                (1, 1, 0, 1, 0): (1, 0, 1),
                (1, 1, 0, 1, 1): (1, 1, 0),
                (1, 1, 1, 0, 0): (1, 0, 1),
                (1, 1, 1, 0, 1): (1, 1, 0),
                (1, 1, 1, 1, 0): (1, 1, 0),
                (1, 1, 1, 1, 1): (1, 1, 1),
            }

            cout, carry, sum_bit = LUT_4_2[(x1, x2, x3, x4, cin)]
        return cout, carry, sum_bit


class Multiplier:
    """
    Implements an 8-bit binary multiplier for both signed and unsigned integers.
    It uses logic gates, adders, and 4:2 compressors to compute partial products
    and sum them up. The final result is 16 bits.
    """

    def unsign_binary_multiply(self, a, b):
        """
        Performs unsigned 8-bit binary multiplication of integers a and b,
        returning a list of 16 bits representing the product.
        :param a: integer (0 to 255)
        :param b: integer (0 to 255)
        :return: list of 16 bits (MSB to LSB in the list)
        """
        # Convert inputs to 8-bit binary strings
        a_bin = f"{a:08b}"
        b_bin = f"{b:08b}"

        # partial_result holds the individual product bits
        partial_result = {}
        for bb in range(7, -1, -1):
            for aa in range(8):
                # e.g., a0_b0, a1_b0, etc.
                partial_result[f'a{7 - aa}_b{7 - bb}'] = int(a_bin[aa]) & int(b_bin[bb])

        # Initialize a 16-bit result array (index 0 is the MSB, index 15 is the LSB)
        result = [0] * 16
        result[-1] = partial_result['a0_b0']  # LSB

        # Step 1: Half-Adder for partial bits
        ha1_sum, ha1_carry = Adder.half_adder(partial_result['a1_b0'], partial_result['a0_b1'])
        result[-2] = ha1_sum

        # Step 2: Full-Adder for partial bits
        fa2_sum, fa2_carry = Adder.full_adder(
            partial_result['a2_b0'],
            partial_result['a1_b1'],
            partial_result['a0_b2'],
        )

        # Step 3: 4:2 Compressor
        comp3_cout, comp3_carry, comp3_csum = Compressor.compressor_4_to_2(
            partial_result['a3_b0'],
            partial_result['a2_b1'],
            partial_result['a1_b2'],
            partial_result['a0_b3'],
            fa2_carry,
            ignore=1
        )

        # Step 4
        comp4_cout, comp4_carry, comp4_csum = Compressor.compressor_4_to_2(
            partial_result['a4_b0'],
            partial_result['a3_b1'],
            partial_result['a2_b2'],
            partial_result['a1_b3'],
            partial_result['a0_b4'],
            ignore=4
        )

        # Step 5
        comp5_cout, comp5_carry, comp5_csum = Compressor.compressor_4_to_2(
            partial_result['a5_b0'],
            partial_result['a4_b1'],
            partial_result['a3_b2'],
            partial_result['a2_b3'],
            partial_result['a1_b4'],
            ignore=2
        )

        # Step 6
        comp6_cout, comp6_carry, comp6_csum = Compressor.compressor_4_to_2(
            partial_result['a6_b0'],
            partial_result['a5_b1'],
            partial_result['a4_b2'],
            partial_result['a3_b3'],
            partial_result['a2_b4'],
            ignore=3
        )

        # Step 7
        comp7_cout, comp7_carry, comp7_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b0'],
            partial_result['a6_b1'],
            partial_result['a5_b2'],
            partial_result['a4_b3'],
            partial_result['a3_b4'],
            ignore=1
        )

        # Step 8
        comp8_cout, comp8_carry, comp8_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b1'],
            partial_result['a6_b2'],
            partial_result['a5_b3'],
            partial_result['a4_b4'],
            partial_result['a3_b5'],
            ignore=0
        )

        # Step 9
        comp9_cout, comp9_carry, comp9_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b2'],
            partial_result['a6_b3'],
            partial_result['a5_b4'],
            partial_result['a4_b5'],
            partial_result['a3_b6'],
            ignore=1
        )

        # Step 10
        comp10_cout, comp10_carry, comp10_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b3'],
            partial_result['a6_b4'],
            partial_result['a5_b5'],
            partial_result['a4_b6'],
            partial_result['a3_b7'],
            ignore=2
        )

        # Step 11
        comp11_cout, comp11_carry, comp11_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b4'],
            partial_result['a6_b5'],
            partial_result['a5_b6'],
            partial_result['a4_b7'],
            comp10_cout,
            ignore=1
        )

        # Step 12
        comp12_cout, comp12_carry, comp12_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b5'],
            partial_result['a6_b6'],
            partial_result['a5_b7'],
            comp11_cout,
            comp11_carry,
            ignore=3
        )

        # Step 13: Half-Adder for fa2_sum and ha1_carry
        ha13_sum, ha13_carry = Adder.half_adder(fa2_sum, ha1_carry)
        result[-3] = ha13_sum

        # Step 14: Half-Adder for comp3_csum and ha13_carry
        ha14_sum, ha14_carry = Adder.half_adder(comp3_csum, ha13_carry)
        result[-4] = ha14_sum

        # Step 15: Full-Adder for comp4_csum, comp3_cout, comp3_carry
        fa15_sum, fa15_carry = Adder.full_adder(comp4_csum, comp3_cout, comp3_carry)

        # Step 16: Half-Adder for fa15_sum and ha14_carry
        ha16_sum, ha16_carry = Adder.half_adder(fa15_sum, ha14_carry)
        result[-5] = ha16_sum

        # Step 17: 4:2 Compressor for partial bits
        comp17_cout, comp17_carry, comp17_csum = Compressor.compressor_4_to_2(
            partial_result['a0_b5'],
            comp5_csum,
            comp4_cout,
            comp4_carry,
            fa15_carry,
            ignore=3
        )

        # Step 18: Half-Adder for comp17_csum and ha16_carry
        ha18_sum, ha18_carry = Adder.half_adder(comp17_csum, ha16_carry)
        result[-6] = ha18_sum

        # Step 19
        comp19_cout, comp19_carry, comp19_csum = Compressor.compressor_4_to_2(
            partial_result['a1_b5'],
            partial_result['a0_b6'],
            comp6_csum,
            comp5_carry,
            comp5_cout,
            ignore=2
        )

        # Step 20
        fa20_sum, fa20_carry = Adder.full_adder(comp19_csum, comp17_carry, comp17_cout)

        # Step 21: Half-Adder for fa20_sum and ha18_carry
        ha21_sum, ha21_carry = Adder.half_adder(fa20_sum, ha18_carry)
        result[-7] = ha21_sum

        # Step 22
        comp22_cout, comp22_carry, comp22_csum = Compressor.compressor_4_to_2(
            partial_result['a2_b5'],
            partial_result['a1_b6'],
            partial_result['a0_b7'],
            comp7_csum,
            comp6_cout,
            ignore=3
        )

        # Step 23
        comp23_cout, comp23_carry, comp23_csum = Compressor.compressor_4_to_2(
            comp22_csum,
            comp6_carry,
            comp19_cout,
            comp19_carry,
            fa20_carry,
            ignore=3
        )

        # Step 24: Half-Adder for comp23_csum and ha21_carry
        ha24_sum, ha24_carry = Adder.half_adder(comp23_csum, ha21_carry)
        result[-8] = ha24_sum

        # Step 25
        comp25_cout, comp25_carry, comp25_csum = Compressor.compressor_4_to_2(
            partial_result['a2_b6'],
            partial_result['a1_b7'],
            comp8_csum,
            comp7_carry,
            comp7_cout,
            ignore=3
        )

        # Step 26
        comp26_cout, comp26_carry, comp26_csum = Compressor.compressor_4_to_2(
            comp25_csum,
            comp22_carry,
            comp22_cout,
            comp23_carry,
            comp23_cout,
            ignore=2
        )

        # Step 27: Half-Adder for comp26_csum and ha24_carry
        ha27_sum, ha27_carry = Adder.half_adder(comp26_csum, ha24_carry)
        result[-9] = ha27_sum

        # Step 28
        comp28_cout, comp28_carry, comp28_csum = Compressor.compressor_4_to_2(
            partial_result['a2_b7'],
            comp9_csum,
            comp8_cout,
            comp8_carry,
            comp25_cout,
            ignore=2
        )

        # Step 29
        comp29_cout, comp29_carry, comp29_csum = Compressor.compressor_4_to_2(
            comp28_csum,
            comp25_carry,
            comp26_cout,
            comp26_carry,
            ha27_carry,
            ignore=3
        )
        result[-10] = comp29_csum

        # Step 30
        comp30_cout, comp30_carry, comp30_csum = Compressor.compressor_4_to_2(
            comp10_csum,
            comp9_carry,
            comp9_cout,
            comp28_carry,
            comp28_cout,
            ignore=1
        )

        # Step 31
        fa31_sum, fa31_carry = Adder.full_adder(comp30_csum, comp29_cout, comp29_carry)
        result[-11] = fa31_sum

        # Step 32
        comp32_cout, comp32_carry, comp32_csum = Compressor.compressor_4_to_2(
            comp11_csum,
            comp10_carry,
            comp30_cout,
            comp30_carry,
            fa31_carry,
            ignore=1
        )
        result[-12] = comp32_csum

        # Step 33
        fa33_sum, fa33_carry = Adder.full_adder(comp12_csum, comp32_carry, comp32_cout)
        result[-13] = fa33_sum

        # Step 34
        comp34_cout, comp34_carry, comp34_csum = Compressor.compressor_4_to_2(
            partial_result['a7_b6'],
            partial_result['a6_b7'],
            comp12_cout,
            comp12_carry,
            fa33_carry,
            ignore=1
        )
        result[-14] = comp34_csum

        # Step 35
        fa35_sum, fa35_carry = Adder.full_adder(partial_result['a7_b7'], comp34_carry, comp34_cout)
        result[-15] = fa35_sum

        # The most significant bit of the product
        result[-16] = fa35_carry

        return result

    @staticmethod
    def to_twos_complement(value, bits=8):
        """
        Converts a decimal integer 'value' to its two's complement binary representation (as a list of bits).
        :param value: integer in the range [-128, 127] for 8-bit
        :param bits: number of bits (default=8)
        :return: list of bits representing two's complement
        """
        if value < 0:
            value = (1 << bits) + value
        return [int(bit) for bit in f"{value:0{bits}b}"]

    @staticmethod
    def twos_complement_to_sign_magnitude(binary):
        """
        Converts a two's complement binary list to its decimal magnitude.
        If the sign bit is 0, the number is non-negative.
        If the sign bit is 1, interpret the number as negative.
        :param binary: list of bits
        :return: integer value
        """
        sign = binary[0]
        if sign == 0:
            # Non-negative number, directly convert to decimal
            return int(''.join(map(str, binary)), 2)
        else:
            # Negative number, find the magnitude by inverting and adding 1
            inverted = [1 - bit for bit in binary]
            incremented = int(''.join(map(str, inverted)), 2) + 1
            twos_complement_value = incremented & ((1 << len(binary)) - 1)
            return twos_complement_value

    def sign_binary_multiply(self, a: int, b: int):
        """
        Performs signed 8-bit multiplication of integers a and b.
        Uses two's complement to handle negative numbers, then calls the unsigned multiplier.
        :param a: integer in the range [-128, 127]
        :param b: integer in the range [-128, 127]
        :return: integer product in decimal
        """
        # Convert to two's complement
        a_tc = Multiplier.to_twos_complement(a)
        b_tc = Multiplier.to_twos_complement(b)

        # Determine overall sign (1 if negative, 0 if positive)
        sign = 0 if a_tc[0] == b_tc[0] else 1

        # Convert two's complement to magnitude
        a_val = Multiplier.twos_complement_to_sign_magnitude(a_tc)
        b_val = Multiplier.twos_complement_to_sign_magnitude(b_tc)

        # Perform unsigned multiplication on the magnitudes
        raw_result = self.unsign_binary_multiply(a_val, b_val)

        # Convert the 16-bit result array (raw_result) to decimal
        # result[0] is the MSB, result[15] is the LSB
        magnitude = 0
        for i in range(1, 16):
            # The bit at index i contributes 2^(15 - i)
            magnitude += raw_result[i] * (2 ** (15 - i))

        # Apply the sign bit
        return -magnitude if sign == 1 else magnitude


def generate_multiplication_lut_csv(output_file="appro3_multiplication_LUT.csv"):
    """
    Generates a CSV file containing the multiplication results (product) for all pairs of
    signed 8-bit integers in the range [-128, 127], except the corner case (a, b) = (-128, -128).
    Calculates MAE, MSE, and MRED for the multiplication results.
    :param output_file: name of the output CSV file
    """
    multiplier = Multiplier()

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write CSV header
        writer.writerow(["A", "B", "Product"])

        total = 0
        errors = []
        relative_errors = []

        # Loop over all pairs (a, b)
        for a in range(-128, 128):
            for b in range(-128, 128):
                # Skip corner case for demonstration purposes
                if a == b == -128:
                    continue
                total += 1
                exact_product = a * b
                approx_product = multiplier.sign_binary_multiply(a, b)

                # Calculate absolute error and relative error
                error = abs(approx_product - exact_product)
                relative_error = error / abs(exact_product) if exact_product != 0 else 0

                errors.append(error)
                relative_errors.append(relative_error)

                writer.writerow([a, b, approx_product])

        # Calculate MAE, MSE, and MRED
        mae = np.mean(errors)
        mse = np.mean(np.square(errors))
        mred = np.mean(relative_errors)

        # Output results
        print(f"LUT table has been written to {output_file}.")
        print(f"Total calculations: {total}")
        print(f"Mean Absolute Error (MAE): {mae}")
        print(f"Mean Square Error (MSE): {mse}")
        print(f"Mean Relative Error Distance (MRED): {mred * 100}%")


if __name__ == "__main__":
    # Generate the CSV file for multiplication results and calculate metrics
    generate_multiplication_lut_csv()
# 最优离散近似方案(索引): {'ca_10': 2, 'ca_11': 1, 'ca_12': 3, 'ca_17': 3, 'ca_19': 2, 'ca_22': 3, 'ca_23': 3, 'ca_25': 3, 'ca_26': 2, 'ca_28': 2, 'ca_29': 3, 'ca_3': 1, 'ca_30': 1, 'ca_32': 1, 'ca_34': 1, 'ca_4': 4, 'ca_5': 2, 'ca_6': 3, 'ca_7': 1, 'ca_8': 0, 'ca_9': 1, 'fa_15': 0, 'fa_2': 0, 'fa_20': 0, 'fa_31': 0, 'fa_33': 0, 'fa_35': 0, 'ha_1': 0, 'ha_13': 0, 'ha_14': 0, 'ha_16': 0, 'ha_18': 0, 'ha_21': 0, 'ha_24': 0, 'ha_27': 0}
