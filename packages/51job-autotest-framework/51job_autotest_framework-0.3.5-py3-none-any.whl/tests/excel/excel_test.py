#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/5/30 8:00 下午
# @Author  : zhengyu.0985
# @FileName: excel_test.py
# @Software: PyCharm

from src.rolling_king.jason.openpyxl.excel_util import ExcelUtil


def get_json():
    excel_obj = ExcelUtil(excel_path="/Users/admin/Downloads/CICD.xlsx",
                          excel_sheet="2")
    print(excel_obj.rows)
    sample_dict = {
        "business_name": "企业经营",
        "second_business_name": "",
        "bytetree_node": [],
        "drop_psm": []
    }
    cat_dict = {

    }
    # for i in range(1, excel_obj.rows):
    for i in range(60, 87):  # 不包括87，左闭右开。
        val = excel_obj.get_cell_value(row=i, col=10)
        print(i, "=", val)
        if val == "Faas" or val == "Cronjob":
            dir_name = excel_obj.get_cell_value_by_cell_name(cell_name="{}{}".format("D", str(i)))
            point_id = excel_obj.get_cell_value_by_cell_name(cell_name="{}{}".format("E", str(i)))
            print("dir_name={}, point_id={}".format(dir_name, point_id))
            if dir_name in cat_dict.keys():
                cat_dict[dir_name].append(str(point_id))
            else:
                cat_dict[dir_name] = [str(point_id)]
    print(cat_dict)
    result_list = []
    for k, v in cat_dict.items():
        curr_dict = {
            "business_name": "企业经营",
            "second_business_name": k,
            "bytetree_node": v,
            "drop_psm": []
        }
        result_list.append(curr_dict)
    print(result_list)


if __name__ == '__main__':
    get_json()
