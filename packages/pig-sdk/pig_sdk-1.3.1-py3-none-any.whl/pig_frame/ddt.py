# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
# @File    : ddt
# @Description :数据驱动 ，数据处理方法

import os.path
import random
import re
import time

import openpyxl as openpyxl
import pyjson5
from faker import Faker
import uuid


# def get_excel_cases(path):
#     """
#     读取Excel 测试用例
#     @param path:Excel文件路径
#     @return:
#     """
#     excel_cases = []
#     if os.path.exists(path):
#         work_book = openpyxl.load_workbook(path)
#         sheets = work_book.get_sheet_names()
#         for sheet in sheets:
#             sheet_cases = work_book.get_sheet_by_name(sheet)
#             all_value = sheet_cases[f"A3:J{sheet_cases.max_row}"]
#             for row_data in all_value:
#                 try:
#                     if row_data[0].value == "是":
#                         excel_cases.append(
#                             {
#                                 "desc": row_data[1].value,
#                                 "case_name": row_data[2].value,
#                                 "path": row_data[3].value,
#                                 "method": str(row_data[4].value).upper(),
#                                 "params": process_data(row_data[5].value),
#                                 "data": process_data(row_data[6].value),
#                                 "body": process_data(row_data[7].value),
#                                 "assert_type": row_data[8].value,
#                                 "exp": process_data(row_data[9].value),
#                             }
#                         )
#                 except:
#                     continue
#     return excel_cases


def process_data(data):
    """
    处理请求参数，期望结果等 ，插入mock数据
    @param data:
    @return:
    """
    try:
        return pyjson5.loads(data)
    except:
        return data


def read_json_data(file_path):
    case_data = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            temp_data = pyjson5.load(file.read())
            if isinstance(temp_data, list):
                case_data += temp_data
            elif isinstance(temp_data, dict):
                case_data.append(temp_data)
    except:
        pass
    return case_data


def get_json_data(file_path):
    """
    读取json文件数据
    @param file_path:
    @return:
    """
    case_data = []
    if str(file_path).__contains__("*"):
        dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        file_name = str(file_name).replace("*", ".*")
        dir_files = os.listdir(dir_path)
        for file in dir_files:
            if re.match(file_name, file) is not None:
                case_data += read_json_data(f"{dir_path}{os.sep}{file}")

    else:
        case_data += read_json_data(file_path)
    return case_data


def process_mock_data(data, loacal="zh_CN"):
    try:
        return PigFrameMock(loacal).process_mock_data(data)
    except:
        return data


class PigFrameDdt:
    def __init__(self, file_path=None):
        self.excel_case = []
        self.case_data = []
        if file_path is not None:
            if str(file_path).lower().endswith(".xlsx"):
                self.excel_case = get_excel_cases(path=file_path)
            elif str(file_path).lower().endswith(".json"):
                self.case_data = get_json_data(file_path)


class PigFrameMock:
    def __init__(self, locale="zh_CN"):
        self.faker = Faker(locale=locale)

    def get_params(self, key):
        try:
            p1 = re.compile(r"[(](.*?)[)]", re.S)
            result = re.findall(p1, key)[0]
            return str(result).split(",")
        except:
            return []

    def process_mock_data(self, data):
        if isinstance(data, dict):
            for key in data:
                data[key] = self.process_mock_data(data[key])
        elif isinstance(data, list):
            for index, value in enumerate(data):
                data[index] = self.process_mock_data(value)
        else:
            return self.get_fake_vale(data)
        return data

    def get_fake_vale(self, key):
        if str(key).lower().startswith("@name"):
            return self.faker.name()
        elif str(key).lower().startswith("@address"):
            return self.faker.address()
        elif str(key).lower().startswith("@city_name"):
            return self.faker.city_name()
        elif str(key).lower().startswith("@country"):
            return self.faker.country()
        elif str(key).lower().startswith("@postcode"):
            return self.faker.postcode()
        elif str(key).lower().startswith("@street_address"):
            return self.faker.street_address()
        elif str(key).lower().startswith("@bank_country"):
            return self.faker.bank_country()
        elif str(key).lower().startswith("@bban"):
            return self.faker.bban()
        elif str(key).lower().startswith("@ean"):
            return self.faker.ean(length=13)
        elif str(key).lower().startswith("@ean13"):
            return self.faker.ean13()
        elif str(key).lower().startswith("@company"):
            return self.faker.company()
        elif str(key).lower().startswith("@credit_card_number"):
            return self.faker.credit_card_number(card_type=None)
        elif str(key).lower().startswith("@currency_code"):
            return self.faker.currency_code()
        elif str(key).lower().startswith("@currency_name"):
            return self.faker.currency_name()
        elif str(key).lower().startswith("@date"):
            pattern = self.get_params(key)
            if len(pattern) == 0:
                pattern = "%Y-%m-%d %H:%M:%S"
            else:
                pattern = pattern[0]
            return self.faker.date(pattern=pattern, end_datetime=None)
        elif str(key).lower().startswith("@file_name"):
            pattern = self.get_params(key)
            if len(pattern) == 0:
                pattern = None
            else:
                pattern = pattern[0]
            return self.faker.file_name(category=None, extension=pattern)
        elif str(key).lower().startswith("@email"):
            return self.faker.email()
        elif str(key).lower().startswith("@ipv4"):
            return self.faker.ipv4()
        elif str(key).lower().startswith("@ipv6"):
            return self.faker.ipv6()
        elif str(key).lower().startswith("@mac_address"):
            return self.faker.mac_address()
        elif str(key).lower().startswith("@url"):
            return self.faker.uri()
        elif str(key).lower().startswith("@first_name"):
            return self.faker.first_name()
        elif str(key).lower().startswith("@last_name"):
            return self.faker.last_name()
        elif str(key).lower().startswith("@phone_number"):
            return self.faker.phone_number()
        elif str(key).lower().startswith("@ssn"):
            pattern = self.get_params(key)
            if len(pattern) == 0:
                min_age = 18
                max_age = 90
            else:
                pattern = pattern[0]
                if pattern.__contains__("-"):
                    min_age = int(pattern.split("-")[0])
                    max_age = int(pattern.split("-")[1])
                else:
                    min_age = int(pattern)
                    max_age = int(pattern) + 1
            return self.faker.ssn(min_age=min_age, max_age=max_age)
        elif str(key).lower().startswith("@timestamp"):
            return str(int(time.time() * 1000))
        elif str(key).lower().startswith("@uuid"):
            return str(uuid.uuid4())
        elif str(key).lower().startswith("@trace_id"):
            return str(uuid.uuid4()).replace("-", "")
        elif str(key).lower().startswith("@dict"):
            return self.faker.pydict()
        elif str(key).lower().startswith("@float"):
            pattern = self.get_params(key)
            min_value = None
            max_value = None
            right_digits = 5
            if len(pattern) == 0:
                pattern = None
            else:
                if pattern[0].__contains__("-"):
                    min_value = int(pattern[0].split("-")[0])
                    max_value = int(pattern[0].split("-")[1])
                if len(pattern) == 2:
                    right_digits = int(pattern[1])
            return self.faker.pyfloat(
                right_digits=right_digits,
                positive=True,
                min_value=min_value,
                max_value=max_value,
            )
        elif str(key).lower().startswith("@int"):
            pattern = self.get_params(key)
            min_value = None
            max_value = None
            if pattern[0].__contains__("-"):
                min_value = int(pattern[0].split("-")[0])
                max_value = int(pattern[0].split("-")[1])
            return self.faker.pyint(min_value=min_value, max_value=max_value, step=1)
        elif str(key).lower().startswith("@list"):
            pattern = self.get_params(key)
            if len(pattern) == 0:
                pattern = 10
            else:
                pattern = int(pattern[0])
            return self.faker.pylist(nb_elements=pattern, variable_nb_elements=True)
        elif str(key).lower().startswith("@str"):
            pattern = self.get_params(key)
            min_value = None
            max_value = None
            if pattern[0].__contains__("-"):
                min_value = int(pattern[0].split("-")[0])
                max_value = int(pattern[0].split("-")[1])
            return self.faker.pystr(min_chars=min_value, max_chars=max_value)
        elif str(key).lower().startswith("@bool"):
            return random.choice([True, False])
        elif str(key).lower().startswith("@choice"):
            return random.choice(self.get_params(key))
        elif str(key).lower().startswith("@text"):
            pattern = self.get_params(key)
            if len(pattern) == 0:
                pattern = 10
            else:
                pattern = int(pattern[0])
            return self.faker.sentence(
                nb_words=pattern, variable_nb_words=True, ext_word_list=None
            )
        else:
            return key


if __name__ == "__main__":
    mock = PigFrameMock()
    print(mock.get_fake_vale("@ipv6"))
    print(mock.get_fake_vale("@mac_address"))
    print(mock.get_fake_vale("@url"))
    print(mock.get_fake_vale("@first_name"))
    print(mock.get_fake_vale("@last_name"))
    print(mock.get_fake_vale("@phone_number"))
    print(mock.get_fake_vale("@ssn(18-20)"))
    print(mock.get_fake_vale("@timestamp"))
    print(mock.get_fake_vale("@uuid"))
    print(mock.get_fake_vale("@trace_id"))
    print(mock.get_fake_vale("@float(5-9,6)"))
    print(mock.get_fake_vale("@str(10-20)"))
    print(mock.get_fake_vale("@bool"))
    print(mock.get_fake_vale("@choice(3,5,8)"))
    print(mock.get_fake_vale("@text"))
