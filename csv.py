# -*- coding: utf8 -*-

import requests
import xlwt
import xlrd
from xlutils.copy import copy
import os
import datetime

a = float(0.75)
b = a *100
print b
# def Yesterday():
#     yesterday = datetime.datetime.now() #- datetime.timedelta(days=1)
#     yesterday_name = yesterday.strftime("%Y-%m-%d")
#     if os.path.exists(yesterday_name + '.xls'):
#         rb = xlrd.open_workbook(yesterday_name + '.xls')
#         rs = rb.sheet_by_index(0)
#         wb = copy(rb)
#         ws = wb.get_sheet(0)
#         ws.write(0, 0, 'changed!')
#         wb.save(yesterday_name + '.xls')
#     else:
#         print("不进行补全")
#
#
# def today():
#     today_name = datetime.datetime.now().strftime("%Y-%m-%d")
#     wbk = xlwt.Workbook()
#     sheet = wbk.add_sheet('sheet 1')
#     sheet.write(0, 0, u'日期')
#     sheet.write(0, 1, u'星期')
#     sheet.write(0, 2, u'时间')
#     sheet.write(0, 3, u'联赛')
#     sheet.write(0, 4, u'对阵球队')
#     sheet.write(0, 5, u'vs')
#     sheet.write(0, 6, u'对阵球队')
#
#     wbk.save(today_name + '.xls')
#
# if __name__ == '__main__':
#     Yesterday()
#     #today()
