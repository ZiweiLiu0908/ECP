import copy
import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz as pgv
from sympy import Symbol
from sympy.logic.boolalg import Not,Or

class Component:
    def __init__(self, switch_name:str, type:str, logic_expression,index:int):
        """
        parameters:
        switch_name: str, the name of the switch, e.g., "S1"
        type: str, the type of the switch, e.g., "input", "output", "state"
        current_logic_expression: str, the current logic expression of the switch, e.g., "S1=0"
        previous_component_list: list, the list of previous components. e.g., "X1->S1" means X1 is the previous component of S1
        next_component_list: list, the list of next components. e.g., "S1->X2" means X2 is the next component of S1
        """
        self.type = type  
        self.switch_name = switch_name  
        self.logic_expression = logic_expression 
        self.previous_component_list = [] 
        self.next_component_list = []  
        self.index=index

    def get_logic_expression(self):
        return self.logic_expression
    
    def set_logic_expression(self, logic_expression):
        self.logic_expression = logic_expression

    def get_previous_component_list(self):
        return self.previous_component_list
    
    def get_next_component_list(self):
        return self.next_component_list
    
    def add_previous_component(self, component):
        self.previous_component_list.append(component)
    
    def add_next_component(self, component):
        self.next_component_list.append(component)

    def __str__(self):
        return (f"Component: {self.switch_name}, Type: {self.type}, "
                f"Logic: {self.logic_expression}, "
                f"Previous: {[comp.switch_name for comp in self.previous_component_list]}, "
                f"Next: {[comp.switch_name for comp in self.next_component_list]}\n")

    def __repr__(self):
        return self.__str__()
    
    def deep_copy(self):
        return copy.deepcopy(self)
    
class Compressor42:
    def __init__(self) -> None:
        self.switch_list = ["S1", "S2", "X1", "X2", "X3", "X4", "Cin"]
        self.output_name = ["Sum", "Carry","Cout"]

        self.operation_sequence_42 = [
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
            "X4->X2",
            "S2->Cin",
            "S1=0",
            "X2->S1",
            "Cin->S1",
            "Cin=0",
            "S1->Cin(Sum)",
        ]
        self.index=0
        self.node_dict = {}
        for switch_name in self.switch_list:
            self.node_dict[switch_name] = Component(switch_name=switch_name, type="input", logic_expression=Symbol(switch_name),index=self.index)
            self.index+=1
        self._build_graph()

    def _build_graph(self):
        self.dependency_graph = []
        for operation in self.operation_sequence_42:
            if "=0" in operation:
                # 这里的逻辑是，如果是=0，那么创建一个新的Component对象，然后将其加入到dependency_graph中
                # 并将node_dict中的key为switch_name的值设置为这个新的Component，从而避免依赖关系的循环
                switch_name = operation.split("=")[0]
                logic_expression=False
                component=Component(switch_name=switch_name, type="input", logic_expression=logic_expression,index=self.index)
                self.dependency_graph.append({"sender_componet":component,"receiver_componet":component,"operation":operation})
                self.node_dict[switch_name] = component
                self.index+=1
            elif "->" in operation:
                # 这里的逻辑是，如果是->，那么将sender和receiver分别提取出来
                # 将sender的component提取出来，如果不存在，那么创建一个新的Component对象
                # 而receiver的component则直接创建一个新的Component对象
                switch_name_1, switch_name_2 = operation.split("->")
                sender=self.node_dict.get(switch_name_1)
                if sender is None:
                    raise ValueError(f"Invalid operation: {operation}")
                
                output_tag=self._check_output(switch_name_2)
                if output_tag is not None:
                    switch_name_2=switch_name_2.replace(f"({output_tag})","")
                    swich_type="output"
                else:
                    swich_type="state"

                receiver_last=self.node_dict.get(switch_name_2)
                if receiver_last is None:
                    raise ValueError(f"Invalid operation: {operation}")
                
                receiver=Component(switch_name=switch_name_2, type=swich_type, logic_expression=receiver_last.get_logic_expression(),index=self.index)
                self.index+=1
                receiver.add_previous_component(receiver_last)
                receiver_last.add_next_component(receiver)
                self.dependency_graph.append({"sender_componet":receiver_last,"receiver_componet":receiver,"operation":f"UPDATE:{switch_name_2}"})
                
                sender.add_next_component(receiver)
                receiver.add_previous_component(sender)
                sender_logic_expression = sender.get_logic_expression()
                receiver_logic_expression = receiver.get_logic_expression()
                receiver.set_logic_expression(Or(Not(sender_logic_expression), receiver_logic_expression))
                self.dependency_graph.append({"sender_componet":sender,"receiver_componet":receiver,"operation":operation})
                
                self.node_dict[switch_name_1] = sender
                self.node_dict[switch_name_2] = receiver
        print("generate dependency graph successfully")
    
    def _check_output(self, switch_name):
        for output_name in self.output_name:
            if output_name in switch_name:
                return output_name
        return None

    def visualize_dependency_graph(self):
        # Create a directed graph
        G = nx.DiGraph()

        # Add edges and set node labels
        for edge in self.dependency_graph:
            sender = edge["sender_componet"].index
            receiver = edge["receiver_componet"].index

            G.add_edge(sender, receiver)
            # Ensure edge uniqueness
            if not G.has_edge(sender, receiver):
                G.add_edge(sender, receiver)

            # Set node labels
            G.nodes[sender]["label"] = edge["sender_componet"].switch_name
            G.nodes[receiver]["label"] = edge["receiver_componet"].switch_name

            # Set edge labels
            G.edges[sender, receiver]["label"] = edge["operation"]

        # Create an AGraph for better layout control
        A = nx.nx_agraph.to_agraph(G)

        # Set graph attributes for horizontal layout
        A.graph_attr.update(rankdir="LR")  # Left to Right layout
        A.node_attr.update(shape="box", style="rounded,filled", fillcolor="lightblue")

        # Render graph to a file and display
        A.layout(prog="dot")  # Use Graphviz's dot program for layered layout
        A.draw("dependency_graph.png")

        # Display the generated graph
        plt.figure(figsize=(15, 4))
        img = plt.imread("dependency_graph.png")
        plt.imshow(img)
        plt.axis("off")
        plt.title("Dependency Graph (Computation Style)")
        #plt.show()
        plt.savefig("dependency_graph.png", dpi=500)
    
    def operation_step(self):
        step=0
        for operation in self.dependency_graph:
            if "UPDATE" in operation["operation"]:
                pass
            else:
                step+=1
        
        return step

if __name__ == "__main__":
    compressor42=Compressor42()
    compressor42.visualize_dependency_graph()  
    print(compressor42.operation_step())       
