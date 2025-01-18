import copy
import matplotlib.pyplot as plt
import networkx as nx

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
    
class BasicAdder:
    def __init_(self) -> None:
        self.switch_list=[]
        self.output_name=[]
        self.operation_sequence=[]
        self.index=0
        self.node_dict={}
        self._build_graph()
    
    def _build_graph(self):
        self.dependency_graph = []
        for operation in self.operation_sequence:
            if "=0" in operation:
                # the logic here is that if it is =0, then create a new Component object, and then add it to the dependency_graph
                # and set the value of the key in node_dict to this new Component, so as to avoid the circular dependency
                switch_name = operation.split("=")[0]
                logic_expression=False
                component=Component(switch_name=switch_name, type="input", logic_expression=logic_expression,index=self.index)
                self.dependency_graph.append({"sender_componet":component,"receiver_componet":component,"operation":operation})
                self.node_dict[switch_name] = component
                self.index+=1
            elif "->" in operation:
                # the logic here is that if it is ->, then extract sender and receiver respectively
                # extract the component of sender
                # while the component of receiver directly creates a new Component object, and then add it to the dependency_graph
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
    
    def drop_output(self, drop_output_name: str):
        """
        Drop all operations related to the specified output name.
        """
        if drop_output_name not in self.output_name:
            raise ValueError(f"Invalid output name: {drop_output_name}")

        necessary_nodes = set()

        output_nodes=[]
        output_name=self.output_name.remove(drop_output_name)
        for idx in range(len(self.dependency_graph)-1,-1,-1):
            for output_name in self.output_name:
                if output_name in self.dependency_graph[idx]["operation"]:
                    output_nodes.append(self.dependency_graph[idx]["receiver_componet"])
        
        for output_node in output_nodes:
            self._find_necessary_nodes(output_node, necessary_nodes)
        
        new_dependency_graph = []
        for node in self.dependency_graph:
            if node["receiver_componet"].index in necessary_nodes and node["sender_componet"].index in necessary_nodes:
                new_dependency_graph.append(node)
                sender_previous=node["sender_componet"].get_previous_component_list()
                receiver_previous=node["receiver_componet"].get_previous_component_list()
                sender_next=node["sender_componet"].get_next_component_list()
                receiver_next=node["receiver_componet"].get_next_component_list()
                for idx in range(len(sender_previous)-1,-1,-1):
                    if sender_previous[idx].index not in necessary_nodes:
                        sender_previous.pop(idx)
                for idx in range(len(receiver_previous)-1,-1,-1):
                    if receiver_previous[idx].index not in necessary_nodes:
                        receiver_previous.pop(idx)
                for idx in range(len(sender_next)-1,-1,-1):
                    if sender_next[idx].index not in necessary_nodes:
                        sender_next.pop(idx)
                for idx in range(len(receiver_next)-1,-1,-1):
                    if receiver_next[idx].index not in necessary_nodes:
                        receiver_next.pop(idx)
        self.dependency_graph = new_dependency_graph
            
    def _find_necessary_nodes(self, node, necessary_nodes):
        necessary_nodes.add(node.index)
        for previous_node in node.get_previous_component_list():
            if previous_node.index not in necessary_nodes:
                self._find_necessary_nodes(previous_node, necessary_nodes)

    def operation_step(self):
        step=0
        for operation in self.dependency_graph:
            if "UPDATE" in operation["operation"]:
                pass
            else:
                step+=1
    
        return step
    
    def visualize_dependency_graph(self,name="dependency_graph.png"):
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
            G.nodes[sender]["label"] = f"{edge['sender_componet'].index}:{edge['sender_componet'].switch_name}"
            G.nodes[receiver]["label"] = f"{edge['receiver_componet'].index}:{edge['receiver_componet'].switch_name}"

            # Set edge labels
            G.edges[sender, receiver]["label"] = edge["operation"]

        # Create an AGraph for better layout control
        A = nx.nx_agraph.to_agraph(G)

        # Set graph attributes for horizontal layout
        A.graph_attr.update(rankdir="LR")  # Left to Right layout
        A.node_attr.update(shape="box", style="rounded,filled", fillcolor="lightblue")

        # Render graph to a file and display
        A.layout(prog="dot")  # Use Graphviz's dot program for layered layout
        A.draw(name)

        # Display the generated graph
        plt.figure(figsize=(15, 4))
        img = plt.imread(name)
        plt.imshow(img)
        plt.axis("off")
        total_step=self.operation_step()
        plt.title(f"Dependency Graph (Computation Style, Total Step: {total_step})")
        plt.savefig(name, dpi=500)
        print("generate visualization successfully,stored in ",name)