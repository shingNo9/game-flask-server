import os
import re
import pandas as pd
import json
from scripts.excel_data import *
from datetime import datetime
from collections import Counter
#from opencc import OpenCC

def get_all_xlsx_files(xlsx_dir):
    xlsx_files = []
    for root, dirs, files in os.walk(xlsx_dir):
        for file in files:
            #ignore hidden files 排除非英文开头的表
            if file.startswith('~$') or not is_start_with_english(file) or not file.endswith('.xlsx'):
                continue
            xlsx_files.append(os.path.join(root, file))
    return xlsx_files

def is_start_with_english(s):
    if len(s) == 0:
        return False
    first_char = s
    # 判断第一个字符是否为大写或小写英文字母
    if ('A' <= first_char <= 'Z') or ('a' <= first_char <= 'z'):
        return True
    else:
        return False

def main(action, args=None):
    time_start = datetime.now()
    CheckLog.new_log()
    CheckLog.add("------start-----------")
    ############
    if action == "check":
        check_excel()
    elif action == "search":
        find_excel(args)
    ############
    CheckLog.add("--------end-----------")
    time_end = datetime.now()
    CheckLog.add(f"耗时:{time_end - time_start}")
    #print(CheckLog.get_log_list())
    return CheckLog.get_log_list()

def check_excel():
    all_excel_table = get_all_excel_table()
    json_config = read_json_config()
    check_from_config(all_excel_table, json_config)

#读取所有excel
def get_all_excel_table(): 
    path = r"/root/platform/doc/excel"
    excel_list = get_all_xlsx_files(path)
    return AllExcelTable(excel_list)

#检查y列值是否唯一
def check_unique(alltable, xtable, ycolumn):
    val_list  = alltable.get_excel_by_name(xtable).get_columns_by_name(ycolumn)
    if not val_list:
        CheckLog.add(f"{xtable}表的{ycolumn}列没有数据")
        return

    duplicates = find_duplicates(val_list)
    for i in duplicates:
        CheckLog.add(f"{xtable}表的{ycolumn}值:{i} 不唯一")

#rule one-to-one
def check_xtable_ycolumn_in_jtable_kcolumn(alltable, config):
    xtable = config.get('table')
    ycolumn = config.get('column')
    jtable = config.get('reference_table')
    kcolumn = config.get('reference_column')
    xtable_column = alltable.get_excel_by_name(xtable).get_columns_without_empty_by_name(ycolumn)
    jtable_column = alltable.get_excel_by_name(jtable).get_column_value_list(kcolumn)
    for cell in xtable_column:
        if not cell.value in jtable_column:
            CheckLog.add(f"{xtable}表{cell.row_index}行{cell.name}列的值{cell.value},不存在{jtable}表的{kcolumn}列中")

#drop表的id是否在各个表中 rewards_int
def check_reward_int(alltable, config):
    table = config.get('table')
    column = config.get('column')
    data = alltable.get_excel_by_name(table).get_columns_by_name(column)
    for value in data:
        if value.value == "":
            continue
        result = value_in_bagtype_table(alltable, value.value)
        if result is not None:
            check, check_name, check_column = result
            if check is False:
                CheckLog.add(f"{table}表{value.row_index}行{value.name}列的值:{value.value}，不在{check_name}表的{check_column}列中")
        else:
            CheckLog.add(f"{table}表{value.row_index}行{value.name}列的值:{value.value}，无法找到对应的表，请确认配置id是否正确")

    
def value_in_bagtype_table(alltable, value):
    btd = BagTypeDict()
    bag_type = int(value) // 1000000
    check_name = btd.get_table(bag_type)
    check_column = btd.get_column(bag_type)
    if check_name:
        ref_table = alltable.get_excel_by_name(check_name).get_column_value_list(check_column)
        if value not in ref_table:
            return False, check_name, check_column
        else:
            return True, check_name, check_column
    else:
        return None

def get_value_in_list(value):
    nested_list = json.loads(value)
    return to_str_list(nested_list)

def to_str_list(value):
    if isinstance(value, list):
        return [to_str_list(item) for item in value]
    else:
        return str(value)

#rewards_int_array_2
def check_reward_int_2(alltable, config):
    table = config.get('table')
    column = config.get('column')
    data = alltable.get_excel_by_name(table).get_columns_by_name(column)
    for cell in data:
        if cell.value == "":
            continue
        cell_list = get_value_in_list(cell.value)
        for i in cell_list:
            result = value_in_bagtype_table(alltable, i[0])
            if result is not None:
                check, check_name, check_column = result
                if check is False:
                    CheckLog.add(f"{table}表{cell.row_index}行{cell.name}列的值:{cell.value}中的{i[0]}，不在{check_name}表的{check_column}列中")
            else:
                CheckLog.add(f"{table}表{cell.row_index}行{cell.name}列的值:{cell.value}中的{i[0]}，无法找到对应的表，请确认配置id是否正确")

#id_in_array               
def check_xtable_ycolumn_array_in_jtable_kcolumn_array(alltable, config):
    xtable = config.get('table')
    ycolumn = config.get('column')
    jtable = config.get('reference_table')
    kcolumn = config.get('reference_column')
    xtable_column = alltable.get_excel_by_name(xtable).get_columns_without_empty_by_name(ycolumn)
    jtable_column = alltable.get_excel_by_name(jtable).get_column_value_list(kcolumn)
    for cell in xtable_column:
        if cell.value == "":
            continue
        value_list = get_value_in_list(cell.value)
        for i in value_list:
            if i not in jtable_column:
                CheckLog.add(f"{xtable}表{cell.row_index}行{cell.name}列的值:{cell.value}中的{i}，不在{jtable}表的{kcolumn}列中")

#rewards_int_array_3
def check_reward_int_3(alltable, config):
    table = config.get('table')
    column = config.get('column')
    data = alltable.get_excel_by_name(table).get_columns_by_name(column)
    for cell in data:
        if cell.value == "":
            continue
        cell_list = get_value_in_list(cell.value)
        for value in cell_list:
            for item in value:
                result = value_in_bagtype_table(alltable, item[0])
                if result is not None:
                    check, check_name, check_column = result
                    if check is False:
                        CheckLog.add(f"{table}表{cell.row_index}行{cell.name}列的值:{cell.value}中的{item[0]}，不在{check_name}表的{check_column}列中")
                else:
                    CheckLog.add(f"{table}表{cell.row_index}行{cell.name}列的值:{cell.value}中的{item[0]}，无法找到对应的表，请确认配置id是否正确")

#equipment-position-des 主动装置，且subtype在EquipmentPositioning表中的 装置技能定位描述不为空
def check_equipment_position_des(alltable, config):
    xtable = config.get('table')
    ycolumn = config.get('column')
    condition = config.get('condition')
    check = config.get('check')
    equipment_type_name = condition[0][0]
    equipment_value =condition[0][1]
    subtype = condition[1][0]
    subtype_table = condition[1][1]
    subtype_table_column = condition[1][2]
    xtable_data = alltable.get_excel_by_name(xtable)
    data = xtable_data.get_columns_by_name(ycolumn)
    subtype_values = alltable.get_excel_by_name(subtype_table).get_column_value_list(subtype_table_column)
    for cell in data:
        row_data = xtable_data.get_row_by_index(cell.row_index)
        if row_data.get_cell_by_name(equipment_type_name).value == equipment_value and row_data.get_cell_by_name(subtype).value in subtype_values:
                check_data = row_data.get_cell_by_name(check).value
                if check_data == "":
                    CheckLog.add(f"{xtable}表{cell.row_index}行{check}列的值:{cell.value}为空")

#table 中的column列 如果entitytype 为 1查warship表，3044的查交互建筑表
def check_condition_column(alltable, config):
    table_name = config.get('table')
    column_name = config.get('column')
    condition = config.get('condition')
    type_column = condition.get('type_column')
    conditoion_values = condition.get('values')
    condition_tables = condition.get('tables')
    condition_columns = condition.get('columns')
    excel_table = alltable.get_excel_by_name(table_name)
    row_data = excel_table.rows
    for row in row_data:
        column_cell = row.get_cell_by_name(column_name)
        check_column_value = row.get_cell_by_name(type_column).value
        for i in range(len(conditoion_values)):
            if check_column_value == conditoion_values[i]:
                ref_table = condition_tables[i]
                ref_column = condition_columns[i]
                ref_value_list = alltable.get_excel_by_name(ref_table).get_column_value_list(ref_column)
                if column_cell.value not in ref_value_list:
                    CheckLog.add(f"{table_name}表{column_cell.row_index}行{column_cell.name}列的值:{column_cell.value}，不在{ref_table}表的{ref_column}列中")
#value-must-set
def check_value_must_set(alltable, config):
    table_name = config.get('table')
    condition = config.get('condition')
    check_value = condition.get('value')
    type_column = condition.get('type_column')
    excel_table = alltable.get_excel_by_name(table_name)
    row_data = excel_table.rows
    for row in row_data:
        column_cell = row.get_cell_by_name(type_column[0])
        if check_value == 'All':
            for i in range(len(type_column)):
                check_column_name = type_column[i]
                check_column_value = row.get_cell_by_name(check_column_name).value
                if check_column_value == "":
                    CheckLog.add(f"{table_name}表{column_cell.row_index}行{check_column_name}列的值为空")
        else:
            if column_cell.value == check_value:
                for i in range(len(type_column)):
                    check_column_name = type_column[i]
                    check_column_value = row.get_cell_by_name(check_column_name).value
                    if check_column_value == "":
                        CheckLog.add(f"{table_name}表{column_cell.row_index}行{check_column_name}列的值为空")
#columns-value-check
def check_columns_value(alltable, config):
    table_name = config.get('table')
    column_name = config.get('column')
    filter = config.get('filter')
    filter_value = filter.get('value')
    filter_column = filter.get('column')
    check_column = config.get('check_column')
    excel_table = alltable.get_excel_by_name(table_name)
    row_data = excel_table.rows
    filter_row_list = []
    if filter_value == "All":
        filter_row_list = excel_table.filter_data(filter_column, filter_value)

    for row in row_data:
        for fr in filter_row_list:
            column_cell = row.get_cell_by_name(column_name)
            fr_value = fr.get_cell_by_name(column_name).value
            if fr_value == column_cell.value:
                check_column_value = row.get_cell_by_name(check_column).value
                if check_column_value == "1":
                    CheckLog.add(f"{table_name}表{column_cell.row_index}行{check_column}列的值为1,但该对话id含有选项不应该跳过")

#columns-only-one
def check_columns_only_one(alltable, config):
    table_name = config.get('table')
    columns_name = config.get('columns')
    noneStr = config.get('none_str')
    excel_table = alltable.get_excel_by_name(table_name)
    for row in excel_table.rows:
        check_list = []
        column_name_str = ""
        for column in columns_name:
            column_cell = row.get_cell_by_name(column)
            column_name_str += column + ","
            if column_cell.value != "" and column_cell.value != noneStr:
                check_list.append(column_cell)
        if len(check_list) > 1:
            CheckLog.add(f"{table_name}表{row.get_index()}行{column_name_str[:-1]}列都有值，只能有一个列有值")

#检测2维数组index的值是否在ref_table的ref_column列中
def check_array2_in_column(alltable, config):
    table_name = config.get('table')
    column_name = config.get('column')
    condition = config.get('condition')
    index = condition.get('index')
    ref_table = condition.get('table')
    ref_column = condition.get('column')
    excel_table = alltable.get_excel_by_name(table_name)
    ref_value_list = alltable.get_excel_by_name(ref_table).get_column_value_list(ref_column)
    for row in excel_table.rows:
        if row.id.value == "" or row.id.value is None:
            continue
        column_cell = row.get_cell_by_name(column_name)
        check_value = get_value_in_array_2(column_cell.value, index)
        if len(check_value) > 0:
            for value in check_value:
                if value not in ref_value_list:
                    CheckLog.add(f"{table_name}表{column_cell.row_index}行{column_cell.name}列的值:{column_cell.value}的{value}，不在{ref_table}表的{ref_column}列中")

#获取2维数组中index的值
def get_value_in_array_2(array_str, index):
    array = get_value_in_list(array_str)
    index = int(index)
    return [row[index] for row in array if len(row) > index]

#获取3维数组中index的值
def get_value_in_array_3(array_str, index):
    array = get_value_in_list(array_str)
    index = int(index)
    return [row[index] for row in array if len(row) > index and len(row[index]) > 0]

#获取list的维度
def list_dimension(lst):
    if not isinstance(lst, list):
        raise ValueError("Input is not a list")
    if not lst:
        return 0
    return 1 + list_dimension(lst) if isinstance(lst, list) else 1

def find_duplicates(lst):
    lst = [i.value for i in lst]
    counter = Counter(lst)
    duplicates = [item for item, count in counter.items() if count > 1]
    return duplicates

#获取excel表现有数据类型
def get_excel_table_data_type_list(all_excel_table):
    data_type_dict = {}
    for excel_table in all_excel_table.children_excel:
        row = excel_table.rows[0]
        name_list = row.get_columns_name_list()
        for name in name_list:
            data_type = row.get_cell_by_name(name).data_type
            if data_type in data_type_dict:
                continue
            else:
                data_type_dict[data_type] = excel_table.name
    #print(data_type_dict)
    #{'int': 'AchievementBox', 'string': 'ActivityExplore', 'int[][]': 'ActivityLevelup', 'int[]': 'ActivityLevelup', 'string[]': 'ActivityManage', 'string[][]': 'Buff', 'bool': 'Combat', 'int[][][]': 'CombatInterBuild', 'float[][]': 'Visitor', 'float[]': 'VisitorParkPoint', 'float': 'WarshipUILight'}
    return data_type_dict

def read_json_config():
    path = r"/root/myproject/game-flask-server/apps/scripts/rule.json"
    with open(path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    return rules.get('relashionships')

def check_from_config(alltable, json_config):
    check_functions = {
        "one-to-one": check_xtable_ycolumn_in_jtable_kcolumn,
        "rewards_int": check_reward_int,
        "rewards_int_array_2": check_reward_int_2,
        "rewards_int_array_3": check_reward_int_3,
        "id_in_array": check_xtable_ycolumn_array_in_jtable_kcolumn_array,
        "equipment-position-des": check_equipment_position_des,
        "condition-column-check": check_condition_column,
        "value-must-set": check_value_must_set,
        "columns-value-check": check_columns_value,
        "columns-only-one": check_columns_only_one,
        "array2-in-column":check_array2_in_column
    }
    
    for config in json_config:
        rule_type = config.get('type')
        check_function = check_functions.get(rule_type)
        if check_function:
            check_function(alltable, config)

def find_excel(find_str):
    find_list = re.split("[,，]", find_str)
    all_excel_table = get_all_excel_table()
    for excel in all_excel_table.tables():
        for find in find_list:
            result, cell = excel.search_value(find)
            if result:
                CheckLog.add(f"查找:{find}")
                CheckLog.add(f"找到:{excel.name}表中:{cell.row_index}行:{cell.column_index}列的值:{cell.value}")

def show_excel_check_rule():
        check_functions = {
        "one-to-one": check_xtable_ycolumn_in_jtable_kcolumn,
        "rewards_int": check_reward_int,
        "rewards_int_array_2": check_reward_int_2,
        "rewards_int_array_3": check_reward_int_3,
        "id_in_array": check_xtable_ycolumn_array_in_jtable_kcolumn_array,
        "equipment-position-des": check_equipment_position_des,
        "condition-column-check": check_condition_column,
        "ban==============value-must-set": check_value_must_set,
        "columns-value-check": check_columns_value,
        "columns-only-one": check_columns_only_one,
        "array2-in-column":check_array2_in_column
    }
