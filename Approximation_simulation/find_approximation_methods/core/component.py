import copy
import matplotlib.pyplot as plt
import networkx as nx

from sympy import Symbol
from sympy.logic.boolalg import Not, Or


class Component:
    def __init__(self, switch_name: str, type: str, logic_expression, index: int):
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
        self.index = index

    def get_logic_expression(self):
        return self.logic_expression

    def set_logic_expression(self, logic_expression):
        # lets do some modify
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
    def __init__(self) -> None:
        self.switch_list = []
        self.output_name = []
        self.operation_sequence = []
        self.adder_id = 0
        self.input_name = []
        self.drop_type = []

    def _build_graph(self):
        def _check_output(switch_name, output_name_list):
            for output_name in output_name_list:
                if output_name in switch_name:
                    return output_name
            return None

        self.index = 0
        self.node_dict = {}
        self.output_switch_dict = {}
        self.input_switch_dict = {}
        for switch_name in self.switch_list:
            self.node_dict[switch_name] = Component(switch_name=switch_name, type="input",
                                                    logic_expression=Symbol(switch_name), index=self.index)
            if switch_name not in self.input_switch_dict:
                self.input_switch_dict[switch_name] = []
            self.input_switch_dict[switch_name].append(self.node_dict[switch_name])
            self.index += 1
        self.dependency_graph = []
        for operation in self.operation_sequence:
            if "=0" in operation:
                # the logic here is that if it is =0, then create a new Component object, and then add it to the dependency_graph
                # and set the value of the key in node_dict to this new Component, so as to avoid the circular dependency
                switch_name = operation.split("=")[0]
                logic_expression = False
                component = Component(switch_name=switch_name, type="input", logic_expression=logic_expression,
                                      index=self.index)
                self.dependency_graph.append(
                    {"sender_componet": component, "receiver_componet": component, "operation": operation})
                if switch_name not in self.input_switch_dict:
                    self.input_switch_dict[switch_name] = []
                self.input_switch_dict[switch_name].append(component)
                self.node_dict[switch_name] = component
                self.index += 1
            elif "->" in operation:
                # the logic here is that if it is ->, then extract sender and receiver respectively
                # extract the component of sender
                # while the component of receiver directly creates a new Component object, and then add it to the dependency_graph
                sender_switch, receiver_switch = operation.split("->")
                sender = self.node_dict.get(sender_switch)
                if sender is None:
                    raise ValueError(f"Invalid operation: {operation}")

                output_tag = _check_output(receiver_switch, self.output_name)
                if output_tag is not None:
                    receiver_switch = receiver_switch.replace(f"({output_tag})", "")
                    swich_type = "output"
                    self.output_switch_dict[receiver_switch] = output_tag
                else:
                    swich_type = "state"

                receiver_last = self.node_dict.get(receiver_switch)
                if receiver_last is None:
                    raise ValueError(f"Invalid operation: {operation}")

                receiver = Component(switch_name=receiver_switch, type=swich_type,
                                     logic_expression=Or(Not(sender.get_logic_expression()),
                                                         receiver_last.get_logic_expression()), index=self.index)
                self.index += 1

                receiver.add_previous_component(receiver_last)
                receiver_last.add_next_component(receiver)
                self.dependency_graph.append({"sender_componet": receiver_last, "receiver_componet": receiver,
                                              "operation": f"UPDATE:{receiver_switch}"})

                sender.add_next_component(receiver)
                receiver.add_previous_component(sender)
                self.dependency_graph.append(
                    {"sender_componet": sender, "receiver_componet": receiver, "operation": operation})

                self.node_dict[sender_switch] = sender
                self.node_dict[receiver_switch] = receiver

    def drop_output(self, drop_output_name: str):
        """
        Drop all operations related to the specified output name.
        """

        def _find_necessary_nodes(node, necessary_nodes):
            necessary_nodes.add(node.index)
            for previous_node in node.get_previous_component_list():
                if previous_node.index not in necessary_nodes:
                    _find_necessary_nodes(previous_node, necessary_nodes)

        if drop_output_name not in self.output_name:
            raise ValueError(f"Invalid output name: {drop_output_name}")

        if drop_output_name not in self.drop_type:
            self.drop_type.append(drop_output_name)
        necessary_nodes = set()

        output_nodes = []
        for key, value in self.output_switch_dict.items():
            if value != drop_output_name:
                output_nodes.append(self.node_dict[key])

        for output_node in output_nodes:
            _find_necessary_nodes(output_node, necessary_nodes)

        new_dependency_graph = []
        for node in self.dependency_graph:
            if node["receiver_componet"].index in necessary_nodes and node["sender_componet"].index in necessary_nodes:
                new_dependency_graph.append(node)
                sender_previous = node["sender_componet"].get_previous_component_list()
                receiver_previous = node["receiver_componet"].get_previous_component_list()
                sender_next = node["sender_componet"].get_next_component_list()
                receiver_next = node["receiver_componet"].get_next_component_list()
                for idx in range(len(sender_previous) - 1, -1, -1):
                    if sender_previous[idx].index not in necessary_nodes:
                        sender_previous.pop(idx)
                for idx in range(len(receiver_previous) - 1, -1, -1):
                    if receiver_previous[idx].index not in necessary_nodes:
                        receiver_previous.pop(idx)
                for idx in range(len(sender_next) - 1, -1, -1):
                    if sender_next[idx].index not in necessary_nodes:
                        sender_next.pop(idx)
                for idx in range(len(receiver_next) - 1, -1, -1):
                    if receiver_next[idx].index not in necessary_nodes:
                        receiver_next.pop(idx)
        self.dependency_graph = new_dependency_graph

        for key, value in self.output_switch_dict.items():
            if value == drop_output_name:
                self.node_dict[key] = Component(switch_name=key, type="deleted", logic_expression=False,
                                                index=self.index)
                self.index += 1

        operation_sequence = []
        for node in self.dependency_graph:
            if "UPDATE" in node["operation"]:
                continue
            operation_sequence.append(node["operation"])
        for index in range(len(operation_sequence) - 1, -1, -1):
            if "(" not in operation_sequence[index] and "->" in operation_sequence[index]:
                switch_name = operation_sequence[index].split("->")[1]
                if switch_name in self.output_switch_dict:
                    continue
                if switch_name not in self.input_name:
                    continue
                operation_sequence[index] = operation_sequence[index] + f"({drop_output_name})"
                break
        self.operation_sequence = operation_sequence
        self._build_graph()

    def operation_step(self):
        step = 0
        for operation in self.dependency_graph:
            if "UPDATE" in operation["operation"]:
                pass
            else:
                step += 1

        return step

    def visualize_dependency_graph(self, name="dependency_graph.png"):
        G = nx.DiGraph()

        for edge in self.dependency_graph:
            sender = edge["sender_componet"].index
            receiver = edge["receiver_componet"].index

            G.add_edge(sender, receiver)
            if not G.has_edge(sender, receiver):
                G.add_edge(sender, receiver)

            G.nodes[sender]["label"] = f"{edge['sender_componet'].index}:{edge['sender_componet'].switch_name}"
            G.nodes[receiver]["label"] = f"{edge['receiver_componet'].index}:{edge['receiver_componet'].switch_name}"

            G.edges[sender, receiver]["label"] = edge["operation"]

        A = nx.nx_agraph.to_agraph(G)
        A.graph_attr.update(rankdir="LR")
        A.node_attr.update(shape="box", style="rounded,filled", fillcolor="lightblue")

        A.layout(prog="dot")
        A.draw(name)

        plt.figure(figsize=(15, 4))
        img = plt.imread(name)
        plt.imshow(img)
        plt.axis("off")
        total_step = self.operation_step()
        plt.title(f"Dependency Graph (Computation Style, Total Step: {total_step})")
        plt.savefig(name, dpi=500)
        print("generate visualization successfully,stored in ", name)

    def get_output_logic_expression(self):
        output_logic_expression = {}
        for key, value in self.output_switch_dict.items():
            output_logic_expression[value] = self.node_dict[key].get_logic_expression()
        return output_logic_expression

    def set_input(self, swich_name: str, value):
        if not hasattr(self, "input_value"):
            self.input_value = {}
        self.input_value[swich_name] = value

    def get_output(self, swich_name: str):
        for output_switch_name, output_tag in self.output_switch_dict.items():
            if output_tag == swich_name:
                return self.node_dict[output_switch_name].get_logic_expression()

    def forward(self, value_dict):
        output_dict = {}
        for output_switch_name, output_tag in self.output_switch_dict.items():
            if not isinstance(self.node_dict[output_switch_name].get_logic_expression(), bool):
                output_dict[output_tag] = self.node_dict[output_switch_name].get_logic_expression().subs(value_dict)
            else:
                output_dict[output_tag] = self.node_dict[output_switch_name].get_logic_expression()
        return output_dict

    def clear_input(self, swich_name: str):
        if hasattr(self, "input_value"):
            if swich_name in self.input_value:
                del self.input_value[swich_name]

    def set_id(self, adder_id: int):
        self.adder_id = adder_id

    def support_drop_type(self):
        output_name_list = []
        for output_name in self.output_name:
            if output_name == "Sum":
                continue
            else:
                output_name_list.append(output_name)
        return output_name_list