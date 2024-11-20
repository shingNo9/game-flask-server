#coding=utf-8
import os

def format_gm_list():
    file_path = ""
    if not os.path.exists(file_path):
        return None
    
    keyword = "addCommand(new DebugCommand("
    result_list = []
    with open(file_path, 'r') as file:
        for line in file:
            if keyword in line:
                #result_list.append(line)
                start = line.index('"')
                end = line.rfind('"')
                temp = line[start:end].replace('"', "").strip()
                data = gm_data(temp)
                result_list.append(data.get_dict())
    return result_list
    
class gm_data:
    def __init__(self, data):
        cmd_index = data.index(',')
        self.cmd = data[:cmd_index]
        temp = data[cmd_index + 1:]
        desc_index = temp.index(',')
        self.desc = temp[:desc_index].strip()
        self.example = temp[desc_index + 1:].strip()

    def get_dict(self):
        dict = {}
        dict['cmd'] = self.cmd
        dict['desc'] = self.desc
        dict['example'] = self.example
        return dict