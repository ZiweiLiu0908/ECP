import numpy as np
import pandas as pd

data = pd.read_csv('/sign/LUT/appro1_multiplication_LUT.csv')

lut = np.zeros((256, 256), dtype=np.int16)

for index, row in data.iterrows():
    a = int(row['A'])
    b = int(row['B'])
    product = int(row['Product'])
    if -128 <= a <= -1:
        a += 256
    if -128 <= b <= -1:
        b += 256
    lut[a, b] = product
print(lut)

output_file = "appro1.h"
with open(output_file, 'w') as f:
    f.write('#include <stdint.h>\n\n')
    f.write('const int16_t lut[256][256] = {\n')

    for i, row in enumerate(lut):
        row_data = ', '.join(map(str, row))
        if i < 255:
            f.write(f'    {{{row_data}}},\n')
        else:
            f.write(f'    {{{row_data}}}\n')

    f.write('};\n\n')


print(f"LUT has been written to {output_file}")

