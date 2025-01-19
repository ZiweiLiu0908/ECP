try:
    from core.component import Component,BasicAdder
except:
    from .component import Component,BasicAdder

from sympy import Symbol
class Compressor_4_2(BasicAdder):
    def __init__(self):
        super().__init__()
        self.switch_list = ["S1", "S2", "X1", "X2", "X3", "X4", "Cin"]
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
        self.index=0
        self.node_dict = {}
        self.output_switch_dict = {}
        self.input_switch_dict={}
        for switch_name in self.switch_list:
            self.node_dict[switch_name] = Component(switch_name=switch_name, type="input", logic_expression=Symbol(switch_name),index=self.index)
            if switch_name not in self.input_switch_dict:
                self.input_switch_dict[switch_name] = []
            self.input_switch_dict[switch_name].append(self.node_dict[switch_name])
            self.index+=1
        self._build_graph()

class HalfAdder(BasicAdder):
    def __init__(self) -> None:
        super().__init__()
        self.switch_list = ["X1", "X2","S1","S2"]
        self.output_name = ["Sum", "Cout"]

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
        self.switch_list = ["X1","X2","S1"]
        self.output_name = ["Sum"]
        self.operation_sequence=[
            "S1=0",
            "X2->S1",
            "X1->S1",
            "X1=0",
            "S1->X1(Sum)"
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
            output_dict[output_tag]=self.node_dict[output_switch_name].get_logic_expression().subs(symbol)
        return output_dict