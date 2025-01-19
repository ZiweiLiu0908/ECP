from sympy import Xor, symbols
from core import HalfAdder, Compressor_4_2,FullAdder,AND_GATE,Multiplier
from itertools import product

mul=Multiplier()
input={"a":[0,0,0,0,0,0,1,1],"b":[0,0,0,0,0,0,1,1]}
res=mul.forward(input)
print(input)
print(res)

# ca=Compressor_4_2()
# ca.drop_output("Carry")
# ca.drop_output("Cout")
# ca.visualize_dependency_graph()

# full adder test
# fa=FullAdder()
# x=fa.get_output_logic_expression()
# X1, X2,Cin= symbols('X1 X2 Cin')

# for input1,input2,input3 in product(range(2),range(2),range(2)):
#     sum=x["Sum"].subs({X1:input1,X2:input2,Cin:input3})
#     cout=x["Cout"].subs({X1:input1,X2:input2,Cin:input3})
#     print(f"X1={input1}, X2={input2},Cin={input3}, Sum={int(bool(sum))}, Cout={int(bool(cout))}")

# compressor test
# ca=Compressor_4_2()
# x=ca.get_output_logic_expression()
# X1, X2,X3,X4,Cin= symbols('X1 X2 X3 X4 Cin')

# logic_expression=Xor(X1,X2,X3,X4,Cin)


# for input1,input2,input3,input4,input5 in product(range(2),range(2),range(2),range(2),range(2)):
#     sum=x["Sum"].subs({X1:input1,X2:input2,X3:input3,X4:input4,Cin:input5})
#     cout=x["Cout"].subs({X1:input1,X2:input2,X3:input3,X4:input4,Cin:input5})
#     carry=x["Carry"].subs({X1:input1,X2:input2,X3:input3,X4:input4,Cin:input5})
#     print(f"X1={input1}, X2={input2},X3={input3},X4={input4},Cin={input5}, Sum={int(bool(sum))}, Carry={int(bool(carry))}, Cout={int(bool(cout))}")
#     print(f"logic_expression={int(bool(logic_expression.subs({X1:input1,X2:input2,X3:input3,X4:input4,Cin:input5})))}")