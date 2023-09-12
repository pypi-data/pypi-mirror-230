"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :cardTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/8/17 11:28
@Descr:  证件信息判断和提取
"""
import re
import datetime
from id_validator import validator
class CardHelper:
    def __init__(self):
        pass

    # 验证身份证号是否有效
    @staticmethod
    def is_valid_of_identity_card(identity_card):
        # 使用验证器验证身份证号
        result = validator.is_valid(identity_card)
        return result

    # 通过身份证号获取性别
    @staticmethod
    def get_sex_by_identity_card(identity_card):

        sex = identity_card[16:17]
        if int(sex) % 2:
            sex = '男'
        else:
            sex = '女'
        return sex

    # 通过身份证号获取出生日期
    @staticmethod
    def get_birthday_by_identity_card(identity_card):

        year = identity_card[6:10]
        month = identity_card[10:12]
        date = identity_card[12:14]
        birthy = year + '-' + month + '-' + date
        return birthy

    # 通过身份证号获取年龄（截止到现在）
    @staticmethod
    def get_age_by_identity_card(identity_card):
        birth_year = int(identity_card[6:10])
        birth_month = int(identity_card[10:12])
        birth_day = int(identity_card[12:14])
        birth_date = datetime.date(birth_year, birth_month, birth_day)
        age = datetime.date.today().year - birth_date.year
        return age

if __name__ == '__main__':
    print(CardHelper.is_valid_of_identity_card("510125197909282834"))
    print(CardHelper.is_valid_of_identity_card("130481198211102193"))
    print(CardHelper.is_valid_of_identity_card("532527198206251411"))
    print(CardHelper.is_valid_of_identity_card("65412819861118042X"))
    print(CardHelper.is_valid_of_identity_card("510125197909282834"))
    print(CardHelper.is_valid_of_identity_card("130481198217102193"))
    print(CardHelper.is_valid_of_identity_card("532523198206251411"))
    print(CardHelper.is_valid_of_identity_card("654128198611180426"))