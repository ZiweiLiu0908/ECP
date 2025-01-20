try:
    from core.adder import FullAdder, HalfAdder,Compressor_4_2,AND_GATE
except:
    from .adder import FullAdder, HalfAdder,Compressor_4_2,AND_GATE
from cv2 import add
from sympy import Symbol
import matplotlib.pyplot as plt
import networkx as nx

class Multiplier:
    def __init__(self) -> None:
        self.input_symbols = [
            Symbol(f"a{i}") for i in range(8)
        ] + [Symbol(f"b{i}") for i in range(8)]
        self.output_logic_expression = {}
        self.adder = {
            f"ha_{i}": HalfAdder() for i in [1, 13, 14, 16, 18, 21, 24, 27]
        } | {
            f"fa_{i}": FullAdder() for i in [2, 15, 20, 31, 33, 35]
        } | {
            f"ca_{i}": Compressor_4_2() for i in range(36) if i not in [0, 1, 13, 14, 16, 18, 21, 24, 27, 2, 15, 20, 31, 33, 35]
        }

        adder_num={"ha":0,"fa":0,"ca":0,"and":64}
        for key, adder in self.adder.items():
            if adder is not None:
                adder_id=key
                adder_num[key.split("_")[0]]+=1
                adder.set_id(adder_id)

        # first inintialize the middle values of the input
        self.middle_values = {
            f"a{i}b{j}": AND_GATE() for i in range(8) for j in range(8)
        }
        for key,middle_values in self.middle_values.items():
            middle_values.set_id(key)

        for key,middle_values in self.middle_values.items():
            index1=int(key[1])
            index2=int(key[3])
            middle_values.set_input("X1",self.input_symbols[index1])
            middle_values.set_input("X2",self.input_symbols[8+index2])

        self.connections = {
            **{adder_id: {"inputs": {}, "outputs": []} for adder_id in self.adder.keys()},
            **{middle_values_id: {"inputs": {}, "outputs": []} for middle_values_id in self.middle_values.keys()}
        }
        self.adder_dict = {**self.adder, **self.middle_values}

        self.forward_sequence = {
            "middle_values": {i*8+j: f"a{i}b{j}" for i in range(8) for j in range(8)},
            "adders": {i: adder_id for i, adder_id in enumerate(sorted(self.adder.keys(), key=lambda x: int(x.split("_")[1])))}
        }

        print(f"generate multiplier: ha[{adder_num['ha']}], fa[{adder_num['fa']}], ca[{adder_num['ca']}], and[{adder_num['and']}]")
        self._build_graph()

    def connect(self, src_id, src_port, dst_id, dst_port):
        """
        连接两个加法器的输入和输出
        :param src_id: 源加法器 ID
        :param src_port: 源加法器输出端口名称
        :param dst_id: 目标加法器 ID
        :param dst_port: 目标加法器输入端口名称
        """
        if src_id in self.adder_dict and dst_id in self.adder_dict:
            # 记录连接
            self.connections[src_id]["outputs"].append((dst_id, dst_port))
            self.connections[dst_id]["inputs"][dst_port] = (src_id, src_port)
            # 设置加法器连接
            src_output = self.adder_dict[src_id].get_output(src_port)
            self.adder_dict[dst_id].set_input(dst_port, src_output)
        else:
            raise ValueError(f"Invalid adder IDs: {src_id}, {dst_id}")

    # def disconnect(self, src_id, src_port, dst_id, dst_port):
    #     """
    #     断开两个加法器的输入和输出
    #     :param src_id: 源加法器 ID
    #     :param src_port: 源加法器输出端口名称
    #     :param dst_id: 目标加法器 ID
    #     :param dst_port: 目标加法器输入端口名称
    #     """
    #     if dst_id in self.connections and dst_port in self.connections[dst_id]["inputs"]:
    #         # 删除连接
    #         self.connections[src_id]["outputs"].remove((dst_id, dst_port))
    #         del self.connections[dst_id]["inputs"][dst_port]
    #         # 清空加法器输入
    #         self.adder_dict[dst_id].clear_input(dst_port)
    #     else:
    #         raise ValueError(f"Invalid connection: {src_id}.{src_port} -> {dst_id}.{dst_port}")

    def _build_graph(self):
        # y0
        self.output_logic_expression["y0"]={"a0b0":"Sum"}

        # ha
        self.connect("a1b0", "Sum", "ha_1", "X1")
        self.connect("a0b1", "Sum", "ha_1", "X2")

        # y1
        self.output_logic_expression["y1"]={"ha_1":"Sum"}

        # fa_2
        self.connect("a2b0", "Sum", "fa_2", "X1")
        self.connect("a1b1", "Sum", "fa_2", "X2")
        self.connect("a0b2", "Sum", "fa_2", "Cin")

        # ca_3
        self.connect("a3b0", "Sum", "ca_3", "X1")
        self.connect("a2b1", "Sum", "ca_3", "X2")
        self.connect("a1b2", "Sum", "ca_3", "X3")
        self.connect("a0b3", "Sum", "ca_3", "X4")
        self.connect("fa_2", "Cout", "ca_3", "Cin")

        # ca_4
        self.connect("a4b0", "Sum", "ca_4", "X1")
        self.connect("a3b1", "Sum", "ca_4", "X2")
        self.connect("a2b2", "Sum", "ca_4", "X3")
        self.connect("a1b3", "Sum", "ca_4", "X4")
        self.connect("a0b4", "Sum", "ca_4", "Cin")

        # ca_5
        self.connect("a5b0", "Sum", "ca_5", "X1")
        self.connect("a4b1", "Sum", "ca_5", "X2")
        self.connect("a3b2", "Sum", "ca_5", "X3")
        self.connect("a2b3", "Sum", "ca_5", "X4")
        self.connect("a1b4", "Sum", "ca_5", "Cin")

        # ca_6
        self.connect("a6b0", "Sum", "ca_6", "X1")
        self.connect("a5b1", "Sum", "ca_6", "X2")
        self.connect("a4b2", "Sum", "ca_6", "X3")
        self.connect("a3b3", "Sum", "ca_6", "X4")
        self.connect("a2b4", "Sum", "ca_6", "Cin")

        # ca_7
        self.connect("a7b0", "Sum", "ca_7", "X1")
        self.connect("a6b1", "Sum", "ca_7", "X2")
        self.connect("a5b2", "Sum", "ca_7", "X3")
        self.connect("a4b3", "Sum", "ca_7", "X4")
        self.connect("a3b4", "Sum", "ca_7", "Cin")

        # ca_8
        self.connect("a7b1", "Sum", "ca_8", "X1")
        self.connect("a6b2", "Sum", "ca_8", "X2")
        self.connect("a5b3", "Sum", "ca_8", "X3")
        self.connect("a4b4", "Sum", "ca_8", "X4")
        self.connect("a3b5", "Sum", "ca_8", "Cin")

        # ca_9
        self.connect("a7b2", "Sum", "ca_9", "X1")
        self.connect("a6b3", "Sum", "ca_9", "X2")
        self.connect("a5b4", "Sum", "ca_9", "X3")
        self.connect("a4b5", "Sum", "ca_9", "X4")
        self.connect("a3b6", "Sum", "ca_9", "Cin")

        # ca_10
        self.connect("a7b3", "Sum", "ca_10", "X1")
        self.connect("a6b4", "Sum", "ca_10", "X2")
        self.connect("a5b5", "Sum", "ca_10", "X3")
        self.connect("a4b6", "Sum", "ca_10", "X4")
        self.connect("a3b7", "Sum", "ca_10", "Cin")

        # ca_11
        self.connect("a7b4", "Sum", "ca_11", "X1")
        self.connect("a6b5", "Sum", "ca_11", "X2")
        self.connect("a5b6", "Sum", "ca_11", "X3")
        self.connect("a4b7", "Sum", "ca_11", "X4")
        self.connect("ca_10", "Cout", "ca_11", "Cin")

        # ca_12
        self.connect("a7b5", "Sum", "ca_12", "X1")
        self.connect("a6b6", "Sum", "ca_12", "X2")
        self.connect("a5b7", "Sum", "ca_12", "X3")
        self.connect("ca_11", "Cout", "ca_12", "X4")
        self.connect("ca_11", "Carry", "ca_12", "Cin")

        # ha_13
        self.connect("fa_2","Sum","ha_13","X1")
        self.connect("ha_1","Cout","ha_13","X2")

        # y2
        self.output_logic_expression["y2"]={"ha_13":"Sum"}

        # ha_14
        self.connect("ca_3","Sum","ha_14","X1")
        self.connect("ha_13","Cout","ha_14","X2")

        # y3
        self.output_logic_expression["y3"]={"ha_14":"Sum"}

        # fa_15
        self.connect("ca_4","Sum","fa_15","X1")
        self.connect("ca_3","Cout","fa_15","X2")
        self.connect("ca_3","Carry","fa_15","Cin")

        # ha_16
        self.connect("fa_15","Sum","ha_16","X1")
        self.connect("ha_14","Cout","ha_16","X2")

        # y4
        self.output_logic_expression["y4"]={"ha_16":"Sum"}

        # ca_17
        self.connect("a0b5","Sum","ca_17","X1")
        self.connect("ca_5","Sum","ca_17","X2")
        self.connect("ca_4","Cout","ca_17","X3")
        self.connect("ca_4","Carry","ca_17","X4")
        self.connect("fa_15","Cout","ca_17","Cin")

        # ha_18
        self.connect("ca_17","Sum","ha_18","X1")
        self.connect("ha_16","Cout","ha_18","X2")

        # y5
        self.output_logic_expression["y5"]={"ha_18":"Sum"}

        # ca_19
        self.connect("a1b5","Sum","ca_19","X1")
        self.connect("a0b6","Sum","ca_19","X2")
        self.connect("ca_6","Sum","ca_19","X3")
        self.connect("ca_5","Cout","ca_19","X4")
        self.connect("ca_5","Carry","ca_19","Cin")

        # fa_20
        self.connect("ca_19","Sum","fa_20","X1")
        self.connect("ca_17","Cout","fa_20","X2")
        self.connect("ca_17","Carry","fa_20","Cin")

        # ha_21
        self.connect("fa_20","Sum","ha_21","X1")
        self.connect("ha_18","Cout","ha_21","X2")

        # y6
        self.output_logic_expression["y6"]={"ha_21":"Sum"}

        # ca_22
        self.connect("a2b5","Sum","ca_22","X1")
        self.connect("a1b6","Sum","ca_22","X2")
        self.connect("a0b7","Sum","ca_22","X3")
        self.connect("ca_7","Sum","ca_22","X4")
        self.connect("ca_6","Cout","ca_22","Cin")

        # ca_23
        self.connect("ca_22","Sum","ca_23","X1")
        self.connect("ca_6","Carry","ca_23","X2")
        self.connect("ca_19","Cout","ca_23","X3")
        self.connect("ca_19","Carry","ca_23","X4")
        self.connect("fa_20","Cout","ca_23","Cin")

        # ha_24
        self.connect("ca_23","Sum","ha_24","X1")
        self.connect("ha_21","Cout","ha_24","X2")

        # y7
        self.output_logic_expression["y7"]={"ha_24":"Sum"}

        # ca_25
        self.connect("a2b6","Sum","ca_25","X1")
        self.connect("a1b7","Sum","ca_25","X2")
        self.connect("ca_8","Sum","ca_25","X3")
        self.connect("ca_7","Cout","ca_25","X4")
        self.connect("ca_7","Carry","ca_25","Cin")

        # ca_26
        self.connect("ca_25","Sum","ca_26","X1")
        self.connect("ca_22","Cout","ca_26","X2")
        self.connect("ca_22","Carry","ca_26","X3")
        self.connect("ca_23","Cout","ca_26","X4")
        self.connect("ca_23","Carry","ca_26","Cin")

        # ha_27
        self.connect("ca_26","Sum","ha_27","X1")
        self.connect("ha_24","Cout","ha_27","X2")

        # y8
        self.output_logic_expression["y8"]={"ha_27":"Sum"}

        # ca_28
        self.connect("a2b7","Sum","ca_28","X1")
        self.connect("ca_9","Sum","ca_28","X2")
        self.connect("ca_8","Cout","ca_28","X3")
        self.connect("ca_8","Carry","ca_28","X4")
        self.connect("ca_25","Cout","ca_28","Cin")

        # ca_29
        self.connect("ca_28","Sum","ca_29","X1")
        self.connect("ca_25","Carry","ca_29","X2")
        self.connect("ca_26","Cout","ca_29","X3")
        self.connect("ca_26","Carry","ca_29","X4")
        self.connect("ha_27","Cout","ca_29","Cin")

        # y9
        self.output_logic_expression["y9"]={"ca_29":"Sum"}

        # ca_30
        self.connect("ca_10","Sum","ca_30","X1")
        self.connect("ca_9","Cout","ca_30","X2")
        self.connect("ca_9","Carry","ca_30","X3")
        self.connect("ca_28","Cout","ca_30","X4")
        self.connect("ca_28","Carry","ca_30","Cin")

        # fa_31
        self.connect("ca_30","Sum","fa_31","X1")
        self.connect("ca_29","Cout","fa_31","X2")
        self.connect("ca_29","Carry","fa_31","Cin")

        # y10
        self.output_logic_expression["y10"]={"fa_31":"Sum"}

        # ca_32
        self.connect("ca_11","Sum","ca_32","X1")
        self.connect("ca_10","Carry","ca_32","X2")
        self.connect("ca_30","Cout","ca_32","X3")
        self.connect("ca_30","Carry","ca_32","X4")
        self.connect("fa_31","Cout","ca_32","Cin")

        # y11
        self.output_logic_expression["y11"]={"ca_32":"Sum"}

        # fa_33
        self.connect("ca_12","Sum","fa_33","X1")
        self.connect("ca_32","Cout","fa_33","X2")
        self.connect("ca_32","Carry","fa_33","Cin")

        # y12
        self.output_logic_expression["y12"]={"fa_33":"Sum"}

        # ca_34
        self.connect("a7b6","Sum","ca_34","X1")
        self.connect("a6b7","Sum","ca_34","X2")
        self.connect("ca_12","Cout","ca_34","X3")
        self.connect("ca_12","Carry","ca_34","X4")
        self.connect("fa_33","Cout","ca_34","Cin")

        # y13
        self.output_logic_expression["y13"]={"ca_34":"Sum"}

        # fa_35
        self.connect("a7b7","Sum","fa_35","X1")
        self.connect("ca_34","Cout","fa_35","X2")
        self.connect("ca_34","Carry","fa_35","Cin")

        # y14
        self.output_logic_expression["y14"]={"fa_35":"Sum"}

        # y15
        self.output_logic_expression["y15"]={"fa_35":"Cout"}

    def operation_step(self):
        total_step=0
        for adder_id, connections in self.connections.items():
            total_step+=self.adder_dict[adder_id].operation_step()
        return total_step
    
    def forward(self, input_values):
        # input values format: {"a":[0,1,0,1,0,1,0,1],"b":[0,1,0,1,0,1,0,1]}
        # reverse the input values

        input_symbols={
            self.input_symbols[i]:input_values["a"][8-i-1] for i in range(8)
        }
        input_symbols.update({
            self.input_symbols[8+i]:input_values["b"][8-i-1] for i in range(8)
        })

        # first calculate the middle values
        result={}
        for index,value in self.forward_sequence["middle_values"].items():
            result[value]=self.adder_dict[value].forward(input_symbols)

        for index,adder_value in self.forward_sequence["adders"].items():
            connection=self.connections[adder_value]
            adder_input={}
            for key,middle_value in connection["inputs"].items():
                adder_input[Symbol(key)]=result[middle_value[0]][middle_value[1]]
            result[adder_value]=self.adder_dict[adder_value].forward(adder_input)

        # finally calculate the output
        output={}
        for key,value in self.output_logic_expression.items():
            for key1,value1 in value.items():
                output[key]=int(bool(result[key1][value1]))
        
        return output

    def visualize_dependency_graph(self,name="multiplier_dependency_graph.png"):
        G = nx.DiGraph()
        for idex,(adder_id, adder) in enumerate(self.adder_dict.items()):
            G.add_node(adder_id)
            G.nodes[adder_id]["label"] = f"{idex}: {adder_id}"
        
        for output_name, output in self.output_logic_expression.items():
            G.add_node(output_name)
            for key,value in output.items():
                G.add_edge(key,output_name)
                G.edges[key,output_name]["label"]=value

        for adder_id, connections in self.connections.items():
            for dst_id, dst_port in connections["outputs"]:
                G.add_edge(adder_id, dst_id)
                G.edges[adder_id, dst_id]["label"] = f"{dst_port}"

        A=nx.nx_agraph.to_agraph(G)
        A.graph_attr.update(randir="LR")

        for node_name in A.nodes():
            node=A.get_node(node_name)
            if node_name in self.output_logic_expression.keys():
                node.attr.update({"fillcolor": "orange", "shape": "box", "style": "rounded,filled"})
            else:
                node.attr.update({"fillcolor": "lightblue", "shape": "box", "style": "rounded,filled"})

        A.layout(prog="dot")
        A.draw(name)

        plt.figure(figsize=(10,10))
        img = plt.imread(name)
        plt.imshow(img)
        plt.axis("off")
        total_step=self.operation_step()
        plt.title(f"Dependency Graph (Computation Style, Total Step: {total_step})")
        plt.savefig(name, dpi=500)
        print("generate visualization successfully,stored in ",name)

    def drop_adder_Carry_or_Cout(self,adder_id,tag):
        if adder_id in self.forward_sequence["adders"]:
            adder_tag_id=self.forward_sequence["adders"][adder_id]
        elif adder_id in self.adder_dict:
            adder_tag_id=adder_id
        else:
            raise ValueError(f"Invalid adder ID: {adder_id}")
        
        try:
            if isinstance(tag,str):
                self.adder_dict[adder_tag_id].drop_output(tag)
            elif isinstance(tag,list):
                for t in tag:
                    self.adder_dict[adder_tag_id].drop_output(t)
            else:
                raise ValueError(f"Invalid tag: {tag}")
        except:
            raise ValueError(f"Invalid tag: {tag}")
        
    def support_drop_type(self):
        support_drop_type_dict = {}
        for adder_id, adder in self.adder_dict.items():
            support_drop_type_dict[adder_id] = adder.support_drop_type()

        support_combine_dict = {}
        for key, value in support_drop_type_dict.items():
            new_key = tuple(value)
            if new_key not in support_combine_dict:
                support_combine_dict[new_key] = []
            support_combine_dict[new_key].append(key)

        for key, value in support_combine_dict.items():
            adder_id = ",".join(value) 
            print(f"Adder ID: {adder_id} support drop type: {list(key)}") 

    def check_is_correct(self):
        for adder_id, adder in self.adder_dict.items():
            if isinstance(adder,AND_GATE):
                continue
            if isinstance(adder,FullAdder):
                connect=self.connections[adder_id]
                output=2
                if adder_id in ["fa_31","fa_33"]:
                    output=1
                elif adder_id =="fa_35":
                    output=0
                if len(connect["inputs"])!=3 or len(connect["outputs"])!=output:
                    raise ValueError(f"FullAdder {adder_id} is not correct,inputs:{len(connect['inputs'])},outputs:{len(connect['outputs'])}")
            if isinstance(adder,HalfAdder):
                connect=self.connections[adder_id]
                output=1
                if adder_id in ["ha_1","ha_13","ha_14","ha_16","ha_18","ha_21","ha_24","ha_27"]:
                    output=0
                if len(connect["inputs"])!=2 or len(connect["outputs"])!=1:
                    raise ValueError(f"HalfAdder {adder_id} is not correct,inputs:{len(connect['inputs'])},outputs:{len(connect['outputs'])}")
            if isinstance(adder,Compressor_4_2):    
                connect=self.connections[adder_id]
                output=3
                if adder_id in ["ca_29","ca_32","ca_34"]:
                    output=2
                if len(connect["inputs"])!=5 or len(connect["outputs"])!=output:
                    raise ValueError(f"Compressor_4_2 {adder_id} is not correct,inputs:{len(connect['inputs'])},outputs:{len(connect['outputs'])}")