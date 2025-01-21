try:
    from core.adder import FullAdder, HalfAdder,Compressor_4_2,AND_GATE
except:
    from .adder import FullAdder, HalfAdder,Compressor_4_2,AND_GATE
from cv2 import add
from numpy import False_
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
            adder_tag_id=self.forward_sequence["adders"][adder_id-1]
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

    def convert_mode(self,adder_id):
        if adder_id in self.forward_sequence["adders"]:
            adder_tag_id=self.forward_sequence["adders"][adder_id]
        elif adder_id in self.adder_dict:
            adder_tag_id=adder_id
        else:
            raise ValueError(f"Invalid adder ID: {adder_id}")
        
        self.adder_dict[adder_tag_id].convert_mode()

    def write_csv_file(self,file_dir="./mul_step"):
        import os
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        temp_register_list=[
            f"w{i}" for i in range(64) 
        ]
        input_register_list=[
            f"a{i}" for i in range(8)
        ]+[
            f"b{i}" for i in range(8)
        ]
        output_register_list=[
            f"y{i}" for i in range(16)
        ]
        register_list=temp_register_list+input_register_list+output_register_list+["S1","S2","temp_store","Cin"]
        register_list = [item for switch in register_list for item in [switch, f"{switch}_sw"]]
        generation_operation_time={
            key:[["0u",0]] for key in register_list
        }

        temp_value_record_dict={}
        for index,value in self.forward_sequence["middle_values"].items():
            operation_sequence=self.adder_dict[value].operation_sequence
            replace_name_dict=self.adder_dict[value].input_value 
            replace_name_dict={str(key):str(value) for key,value in replace_name_dict.items()}   
            generate_operation_time(generation_operation_time,operation_sequence,replace_name_dict)
            output_switch=self.adder_dict[value].output_switch_dict
            for key,output_name in output_switch.items():
                # only sum need to be stored
                False_logic(generation_operation_time,"temp_store")
                Implication(generation_operation_time,key,"temp_store")
                w_indx=int(value[1])*8+int(value[3])
                False_logic(generation_operation_time,f"w{w_indx}")
                Implication(generation_operation_time,"temp_store",f"w{w_indx}")
            temp_value_record_dict[value]={"Sum":f"w{w_indx}"}     
        for index,value in self.forward_sequence["adders"].items():
            operation_sequence=self.adder_dict[value].operation_sequence
            connect=self.connections[value]
            inputs=connect["inputs"]

            inputs={k:temp_value_record_dict[v[0]][v[1]] for k,v in inputs.items()}
            generate_operation_time(generation_operation_time,operation_sequence,inputs)
            output_switch=self.adder_dict[value].output_switch_dict
            can_store_dict={
                key: True for key in inputs.keys()
            }
            for idx,(key,output_name) in enumerate(output_switch.items()):
                if key in inputs.keys():
                    if value in temp_value_record_dict.keys():
                        temp_value_record_dict[value][output_name]=inputs[key]
                    else:
                        temp_value_record_dict[value]={output_name:inputs[key]}
                    can_store_dict[key]=False
                else:
                    true_key=[k for k,v in can_store_dict.items() if v==True][0]
                    can_store_dict[true_key]=False
                    False_logic(generation_operation_time,"temp_store")
                    Implication(generation_operation_time,key,"temp_store")
                    False_logic(generation_operation_time,inputs[true_key])
                    Implication(generation_operation_time,"temp_store",inputs[true_key])
                    if value in temp_value_record_dict.keys():
                        temp_value_record_dict[value][output_name]=inputs[true_key]
                    else:
                        temp_value_record_dict[value]={output_name:inputs[true_key]}
        for output_value,transfoer_node in self.output_logic_expression.items():
            transfoer_node=list(transfoer_node.keys())+list(transfoer_node.values())
            False_logic(generation_operation_time,"temp_store")
            Implication(generation_operation_time,temp_value_record_dict[transfoer_node[0]][transfoer_node[1]],"temp_store")
            False_logic(generation_operation_time,output_value)
            Implication(generation_operation_time,"temp_store",output_value)

        
        generate_csv_file(file_dir,generation_operation_time)

def generate_operation_time(generation_operation_time,operation_list,replace_name_dict):
    for operation in operation_list:
        operation=operation.replace("(Sum)","")
        operation=operation.replace("(Cout)","")
        operation=operation.replace("(Carry)","")
        if operation=="":
            continue
        if "=0" in operation:
            switch_name=operation.replace("=0","")
            switch_name=replace_name_dict.get(switch_name,switch_name)
            False_logic(generation_operation_time,switch_name)
        elif "->" in operation:
            operation_list=operation.split("->")
            swich_a=operation_list[0]
            swich_b=operation_list[1]
            swich_a=replace_name_dict.get(swich_a,swich_a)
            swich_b=replace_name_dict.get(swich_b,swich_b)
            
            Implication(generation_operation_time,swich_a,swich_b)
        else:
            raise Exception("operation not supported")
    return generation_operation_time

def False_logic(generation_operation_time,switch_name):
    if switch_name not in generation_operation_time:
        raise Exception("switch_name not in generation_operation_time")
    for key in generation_operation_time.keys():
        last_operation=generation_operation_time[key][-1]
        operation_start_time=get_operation_start_time(last_operation)
        if switch_name==key:
            generation_operation_time[key].append([f"{operation_start_time}u",'-1'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'-1'])
        elif switch_name+"_sw"==key:
            generation_operation_time[key].append([f"{operation_start_time}u",'1'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'1'])
        else:
            generation_operation_time[key].append([f"{operation_start_time}u",0])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'0'])

def get_operation_start_time(last_operation):
    last_operation_time=int(last_operation[0].replace("u",""))
    operation_start_time=last_operation_time+0.001
    return operation_start_time

def Implication(generation_operation_time,swich_a,swich_b):
    if swich_a not in generation_operation_time or swich_b not in generation_operation_time:
        raise Exception(f"switch_name not in generation_operation_time {swich_a},{swich_b}")
    for key in generation_operation_time.keys():
        last_operation=generation_operation_time[key][-1]
        operation_start_time=get_operation_start_time(last_operation)
        if swich_a==key:
            generation_operation_time[key].append([f"{operation_start_time}u",'900m'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'900m'])
        elif swich_a+"_sw"==key:
            generation_operation_time[key].append([f"{operation_start_time}u",'1'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'1'])
        elif swich_b==key:
            generation_operation_time[key].append([f"{operation_start_time}u",'1'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'1'])
        elif swich_b+"_sw"==key:
            generation_operation_time[key].append([f"{operation_start_time}u",'1'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'1'])
        else:
            generation_operation_time[key].append([f"{operation_start_time}u",'0'])
            generation_operation_time[key].append([f"{int(operation_start_time)+30}u",'0'])

def generate_csv_file(fold_dir,generation_operation_time):
    for key,values in generation_operation_time.items():
        with open(f"{fold_dir}/{key}.csv","w") as f:
            for value in values:
                f.write(f"{value[0]},{value[1]}\n")
            f.close()
