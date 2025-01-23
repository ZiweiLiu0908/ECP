import itertools
from sympy import Nor, symbols,Or, And,  Xor


X1, X2, X3, X4, Cin = symbols('X1 X2 X3 X4 Cin')

S=Xor(X1,X2,X3)

Carry=Or(And(X4,S),And(Cin,Xor(X1,X2,X3,X4)))
Cout=Or(And(X1,X2),And(X3,Xor(X1,X2)))
Sum=Xor(X1,X2,X3,X4,Cin)

# Define the inputs
inputs = ["X1", "X2", "X3", "X4", "Cin"]
# Generate all possible input combinations (truth table)
truth_table = list(itertools.product([0, 1], repeat=len(inputs)))


Cout_new=Or(And(X1,X2),And(X3,Xor(X1,X2)))
S_new=Or(Nor(X3),And(Nor(X1),Nor(X2)),And(X1,X2))
Carry_new=Or(And(S_new,X4),Cin)
Sum_new=Nor(Xor(And(S_new,X4),Cin))

sum_acc=0
carry_acc=0
cout_acc=0
ca=Approximate_Comp_4_2()
for i1,i2,i3,i4,i5 in truth_table:
    inputs={
        "X1":i1,
        "X2":i2,
        "X3":i3,
        "X4":i4,
        "Cin":i5
    }
    gt_sum=int(bool(Sum.subs(inputs)))
    gt_carry=int(bool(Carry.subs(inputs)))
    gt_cout=int(bool(Cout.subs(inputs)))
    sum_=int(bool(Sum_new.subs(inputs)))
    carry_=int(bool(Carry_new.subs(inputs)))
    cout_=int(bool(Cout_new.subs(inputs)))
    s_new_res=int(bool(Sum_new.subs(inputs)))
    # approximant_output=ca.forward(inputs)
    # approximant_output={k:int(bool(v)) for k,v in approximant_output.items()}
    # sum_acc+=gt_sum==approximant_output['Sum']
    # carry_acc+=gt_carry==approximant_output['Carry']
    # cout_acc+=gt_cout==approximant_output['Cout']
    sum_acc+=gt_sum==sum_
    carry_acc+=gt_carry==carry_
    cout_acc+=gt_cout==cout_
    
    #print(f"{i1} {i2} {i3} {i4} {i5} {sum_==approximant_output['Sum']} {carry_==approximant_output['Carry']} {cout_==approximant_output['Cout']}" )

sum_acc/=len(truth_table)
carry_acc/=len(truth_table)
cout_acc/=len(truth_table)

print(f"Sum: {sum_acc}, Carry: {carry_acc}, Cout: {cout_acc}")
