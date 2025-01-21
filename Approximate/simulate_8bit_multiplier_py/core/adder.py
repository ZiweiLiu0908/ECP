try:
    from core.component import BasicAdder
except:
    from .component import BasicAdder

from sympy import Symbol

class Compressor_4_2(BasicAdder):
    def __init__(self):
        super().__init__()
        self.switch_list = ["S1", "S2", "X1", "X2", "X3", "X4", "Cin"]
        self.input_name = ["X1", "X2", "X3", "X4"]
        self.output_name = ["Sum", "Carry","Cout"]

        self.operation_sequence = [
            "S1=0",  # FALSE(S1)
            "S2=0",  # FALSE(S2)
            "X2->S1",  # S1 = ~X2
            "X1->S1",  # S1 = ~X1 + ~X2
            "X1->S2",  # S2 = ~X1
            "S2->X2",  # X2 = X1 + X2
            "S2=0",  # FALSE(S2)
            "S1->S2",  # S2 = ~(~X1 + ~X2) = X1X2
            "X2->S2",  # S2 = ~X1~X2 + X1X2
            "X2=0",  # FALSE(X2)
            "S2->X2",  # X2 = X1 ⊕ X2 = G4
            "X3->S2",  # S2 = G5
            "X1=0",  # FALSE(X1)
            "S2->X1",  # X1 = ~G5
            "S1->X1(Cout)",  # X1 = Cout
            "S1=0",
            "X2->S1",
            "S1->X3",
            "S1=0",
            "S2->S1",
            "X3->S1",
            "X3=0",
            "S1->X3",
            "X4->S1",
            "X2=0",
            "X3->X2",
            "X2->X4",
            "X2=0",
            "S1->X2",
            "X4->X2",
            "X4=0",
            "X2->X4",
            "Cin->X2",
            "X3=0",
            "S1->X3",
            "X2->X3(Carry)",
            "S2=0",
            "X4->S2",
            "S2->Cin",
            "S1=0",
            "X2->S1",
            "Cin->S1",
            "Cin=0",
            "S1->Cin(Sum)",
        ]
        self.approximation_sequence = [
            "S1=0",  # FALSE(S1)
            "S2=0",  # FALSE(S2)
            "X2->S1",  # S1 = ~X2
            "X1->S1",  # S1 = ~X1 + ~X2
            "X1->S2",  # S2 = ~X1
            "S2->X2",  # X2 = X1 + X2
            "S2=0",  # FALSE(S2)
            "S1->S2",  # S2 = ~(~X1 + ~X2) = X1X2
            "X2->S2",  # S2 = ~X1~X2 + X1X2
            "X2=0",  # FALSE(X2)
            "S2->X2",  # X2 = X1 ⊕ X2 = G4
            "X3->S2",  # S2 = G5 =
            "X1=0",  # FALSE(X1)
            "S2->X1",  # X1 = ~G5
            "S1->X1(Cout)",  # X1 = Cout
            "S1=0",
            "X4->S1", # S1=~X4
            "S2->S1", # S1= ~(G5 AND G4)
            "S1->Cin(Carry)",
            "X3=0",
            "Cin->X3(Sum)",
        ]
        self.adder_type="exact"
        self._build_graph()

    def convert_mode(self):
        temp=self.operation_sequence    
        self.operation_sequence=self.approximation_sequence
        self.approximation_sequence=temp
        self._build_graph()
        if len(self.drop_type)>0:
            for drop in self.drop_type:
                self.drop_output(drop)
        if self.adder_type=="exact":
            self.adder_type="approximate"
        else:
            self.adder_type="exact"
        print(f"Adder type changed to {self.adder_type}")

class HalfAdder(BasicAdder):
    def __init__(self) -> None:
        super().__init__()
        self.switch_list = ["X1", "X2","S1","S2"]
        self.output_name = ["Sum", "Cout"]
        self.input_name=["X1","X2"]

        self.operation_sequence = [
            "S1=0",
            "S2=0",
            "X1->S1",
            "X2->S2",
            "S1->S2",
            "X2->S1",
            "X1->X2",
            "X1=0",
            "S1->X1(Cout)",
            "S1=0",
            "S2->S1",
            "X2->S1(Sum)",
        ]

        self._build_graph()

class FullAdder(BasicAdder):
    def __init__(self) -> None:
        super().__init__()
        self.switch_list = ["X1","X2","Cin","S1","S2"]
        self.output_name = ["Sum", "Cout"]
        self.input_name = ["X1","X2"]

        self.operation_sequence = [
            "S1=0",
            "S2=0",
            "X1->S1",
            "X2->S2",
            "S1->X2",
            "X1->S2",
            "X1=0",
            "X2->X1",
            "S2->X1",
            "S1=0",
            "Cin->S1",
            "S2->Cin",
            "X1->S1",
            "X1=0",
            "S1->X1",
            "S2=0",
            "Cin->S2",
            "X2->S2",
            "X2->Cin",
            "Cin->X1(Sum)",
            "Cin=0",
            "S2->Cin(Cout)",
        ]
        self._build_graph()

class AND_GATE(BasicAdder):
    def __init__(self) -> None:
        super().__init__()
        self.switch_list = ["X1","X2","S1","S2"]
        self.output_name = ["Sum"]
        self.input_name = ["X1","X2"]
        self.operation_sequence=[
            "S1=0",
            "X2->S1",
            "X1->S1",
            "S2=0",
            "S1->S2(Sum)"
        ]
        self._build_graph()
    
    def forward(self,value_dict):
        # we use override the forward method to get the output of the AND_GATE
        # because we can't use the connection from multiplier to AND_GATE
        output_dict={}
        for output_switch_name,output_tag in self.output_switch_dict.items():
            symbol={}
            for key,value in self.input_value.items():
                symbol[Symbol(key)]=value.subs(value_dict)
            if not isinstance(self.node_dict[output_switch_name].get_logic_expression(),bool):
                output_dict[output_tag]=self.node_dict[output_switch_name].get_logic_expression().subs(symbol)
            else:
                output_dict[output_tag]=self.node_dict[output_switch_name].get_logic_expression()
        return output_dict