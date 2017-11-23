#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/11/17 23:33
# @Author  : Tiancc
# @Site    : 
# @File    : start_asd.py
# @Software: PyCharm

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import main


# def choose():
    # dicts ='''
    #     1:添加主机
    #     2:运行FTP Server
    #     9:退出
    # '''
    # print(dicts)

if __name__ == '__main__':
    main.Asd()
    # u_choose={
    #     '1':'',
    #     '2':main.FtpServerr,
    #     '9':exit
    # }
    # while True:
    #     choose()
    #     _input=input('选择序号>: ').strip()
    #     if _input not in u_choose:continue
    #     # elif _input == 2:
    #     u_choose[_input]()