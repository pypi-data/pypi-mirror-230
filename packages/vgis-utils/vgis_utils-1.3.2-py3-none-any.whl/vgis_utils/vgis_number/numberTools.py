"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :numberTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/8/30 11:47
@Descr:
"""
import cn2an


class NumberHelper:
    def __int__(self):
        pass

    # 将阿拉伯数字转换为中文数字（小写，大写，人民币）
    # mode:lower,up,rmb
    @staticmethod
    def convert_alabic_number_to_chinese_number(alabic_number, mode):
        return cn2an.an2cn(alabic_number, mode)

    # 将中文数字（小写，大写）转为阿拉伯数字
    # mode:lower,up,rmb
    @staticmethod
    def convert_chinese_number_to_alabic_number(chinese_number):
        return cn2an.an2cn(chinese_number)