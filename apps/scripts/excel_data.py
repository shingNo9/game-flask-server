import os
import pandas as pd
from enum import Enum

class ExcelRow:
    def __init__(self, column_dict:dict, index):
        self.__columns_dict = column_dict
        self.__index = index
        for key, value in column_dict.items():
            setattr(self, key, value)
        

    def get_cell_by_name(self, attribute_name:str):
        return getattr(self, attribute_name)
    
    def __str__(self):
        return f"ExcelRow {self.__columns_dict}"
    
    def count(self):
        return len(self.__columns_dict.keys())

    def get_columns_name_list(self):
        return self.__columns_dict.keys()
    
    def get_index(self):
        return self.__index + 1

class ExcelCell:
    def __init__(self, row_index:int, excel_col:str, value:str, name_cn:str, name:str, data_type:str, read_type:str):
        self.row_index = row_index + 1
        self.name_cn = name_cn
        self.name = name
        self.data_type = data_type
        self.read_type = read_type
        self.value = value
        self.column_index = excel_col

    def __str__(self):
        return f"ExcelCell: row_index={self.row_index}, column_index={self.column_index}, name={self.name}, name_cn={self.name_cn}, data_type={self.data_type}, value={self.value}"

class AllExcelTable:
    def __init__(self, excel_list:list):
        self.__excel_dict = {}
        self.__excel_list = []
        for excel in excel_list:
            excel_data = ExcelTable(excel)
            self.__excel_dict[excel_data.name] = excel_data
            self.__excel_list.append(excel_data)
        for key, value in self.__excel_dict.items():
            setattr(self, key, value)

    def get_excel_by_name(self, attribute_name):
        return getattr(self, attribute_name)
    
    def tables(self):
        return self.__excel_list

class ExcelTable:
    def __init__(self, path):
        self.path = path
        #4,5行不知道是什么，数据从6开始
        self.__head_index = 5
        
        self.__load_excel()
        self.__get_head_data()
        self.__get_excel_data()

        self.__read_all_cells()
        

    def __load_excel(self):
        self.__pd_data_frame = pd.read_excel(self.path, sheet_name=0,header=None)
        basename = os.path.basename(self.path)
        self.name = os.path.splitext(basename)[0]

    def __get_head_data(self):
        head_data = self.__pd_data_frame.head(self.__head_index + 1)
        cut_index = 0
        first_row = head_data.iloc[0]
        for i in first_row:
            if pd.isna(i):
                break
            cut_index += 1
        
        head_data = head_data.iloc[:,:cut_index]
        self.__cut_index = cut_index
        rows = head_data.iloc
        head_dict = {}
        for name in HeadName:
            if name.name in head_dict:
                raise ValueError(f"{self.name}表列名{name.name}重复了")
            head_dict[name.name] = [str(elem) for elem in rows[name.value].values]
        #print(head_dict)
        self.head_dict = head_dict

    def __get_excel_data(self):
        #这里的index是从1开始的所以要+1
        row_index = self.__head_index + 1
        #fillna("") Nan值替换
        excel_data_frame = self.__pd_data_frame.fillna("")
        excel_data_frame = excel_data_frame.iloc[row_index:, :self.__cut_index]
        #把所有值都转化为str并去除空格，类型由datatype提供
        self.excel_data_frame = excel_data_frame.apply(lambda x: x.astype(str).str.strip())
        #print(self.excel_data_frame )
    
    def __read_all_cells(self):
        row_list = []
        column_dict = {}
        #print(self.excel_data_frame)
        for index, row in self.excel_data_frame.iterrows():
            row_data = {}
            for col_index in range(len(row)):
                cell_value = row[col_index]
                name_cn = self.head_dict[HeadName.Name_cn.name][col_index]
                name = self.head_dict[HeadName.Name.name][col_index]
                data_type = self.head_dict[HeadName.Datatype.name][col_index]
                read_type = self.head_dict[HeadName.Readtype.name][col_index]
                cell = ExcelCell(index, self.get_excel_column_names(col_index), cell_value, name_cn, name, data_type, read_type)
                row_data[name] = cell
                if name not in column_dict:
                    column_dict[name] = []
                column_dict[name].append(cell)
            excel_row = ExcelRow(row_data, index)
            row_list.append(excel_row)
        #print(row_list)
        self.rows = row_list
        #print(column_dict)
        self.columns = column_dict

    def get_excel_column_names(self, index):
        number = index + 1
        column_name = ""
        while number > 0:
            number, remainder = divmod(number - 1, 26)
            column_name = chr(65 + remainder) + column_name
        return column_name
    
    def get_columns_by_name(self, name):
        return self.columns[name]

    def get_columns_without_empty_by_name(self, name):
        col_list = self.columns[name]
        col_list = [i for i in col_list if i.value != ""]
        return col_list
    
    def get_column_value_list(self, name):
        columns = self.get_columns_without_empty_by_name(name)
        col_list = []
        for i in columns:
            col_list.append(i.value)
        return col_list
    
    def get_columns_name_list(self):
        return self.columns.keys()
    
    def get_row_by_index(self, index:int):
        index = index - 7
        return self.rows[index]

    def filter_data(self, column_name, value):
        result_list = []
        for row in self.rows:
            data = row.get_cell_by_name(column_name)
            if value == "All":
                if data.value != "":
                    result_list.append(row)
            elif data.value == value:
                result_list.append(row)

        return result_list
    
    def search_value(self, find_str):
        for row in self.rows:
            for col in row.get_columns_name_list():
                cell = row.get_cell_by_name(col)
                if find_str in cell.value:
                    return True, cell
                
        return False, None
    
    def search_value_match(self, find_str):
        for row in self.rows:
            for col in row.get_columns_name_list():
                cell = row.get_cell_by_name(col)
                if find_str == cell.value:
                    return True, cell
                
        return False, None
'''
class ExcelDataType:
    int
    int[]
    int[][]
    int[][][]
    string
    string[]
    string[][]
    float
    float[]
    float[][]
    bool
'''
class HeadName(Enum):
    Name_cn = 0
    Datatype = 1
    Name = 2
    Readtype = 3

class BagTypeDict:
    def __init__(self):
        
        self.type_dict = {
            1: {"table": "Item", "column": "itemId"},
            2: {"table": "Equipment", "column": "equipmentId"},
            3: {"table": "Warship", "column": "warshipId"},
            4: {"table": "Currency", "column": "currencyId"},
            6: {"table": "WarshipComponent", "column": "componentId"},
            8: {"table": "DropPlan", "column": "dropPlanId"},
            9: {"table": "Crew", "column": "crewId"},
            101: {"table": "ReprisalBuff", "column": "reprisalBuffId"}
        }

    def get_table(self, key, default=None):
        return self.type_dict.get(key, {}).get('table', default)
    
    def get_column(self, key, default=None):
        return self.type_dict.get(key, {}).get('column', default)
    
class CheckLog:
    __log_list = None
    
    @staticmethod
    def add(text):
        CheckLog.__log_list.append(text)

    @staticmethod
    def print_log():
        for i in CheckLog.__log_list:
            print(i)

    @staticmethod
    def write_file(save_path):
        write_list = [line + "\n" for line in CheckLog.__log_list]
        with open(save_path, "w",  encoding='utf-8') as file:
            file.writelines(write_list)

    @staticmethod
    def get_log_list():
        return CheckLog.__log_list
    
    @staticmethod
    def new_log():
        CheckLog.__log_list = []
