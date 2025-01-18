# Description of approximation method
The approximate method we use is based on the following three levels:
- Ignore the carry or cout of the 4-2 compression adder. But control it from a more precise level
- 4-2 Approximation of the compressor logic expression level. The approximation here is mainly for the approximation of the LUT table
- Mix the previous two approximations to balance the effects of the wrong LUT table and ignoring the carry and cout carry as much as possible.
# Method 1: Ignore the carry or cout of the 4-2 compression adder. 
We found that ignoring the Carry or Cout of the 4-2 compression adder at the bit level will lead to a serious drop in accuracy, and it is troublesome to manually consider the coupling between different 4-2 compression adders to handle exceptions. In order to simplify manual processing and fine-grained control of the 4-2 compression adder's carry or not, we proposed a heuristic-based 4-2 compression adder selection model.
## How it work
In order to be able to use heuristic methods, we need to specify a good evaluation metric that helps us determine how many 4-2 compressors can be approximated with a good level of error.
### Determination of evaluation indicators
The evaluation indicators we use here mainly include two aspects: 1. Ignoring the impact of a single or multiple 4-2 compression-based adders on the calculation steps of the entire 8-bit multiplier. 2. Ignoring the error impact and variance of a single or multiple 4-2 compression-based adders on the entire 8-bit multiplier LUT table.
####  Processing of evaluation index 1
1. Here we mainly construct three different adders based on the paper `Power-Area Efficient Serial IMPLY-based 4-2 Compressor Applied in Data-Intensive Application` and construct a logical expression tree according to the algorithm flow.
2. We can determine the predecessors that carry and cout depend on based on the established logical expression tree, and delete these predecessors to determine the number of steps that can be reduced.
3. And we can construct a larger multiplication logic expression tree to detect the impact of the change of the carry of a 4-2 compression-based adder on the adder (hereinafter referred to as a) that depends on its result, so as to update the adder process of a. In this way, we can save steps in the entire multiplication logic.

# Method 2: 4-2 Approximation of the compressor logic expression level.

# Method 3: Mix the method 1 and method 2
