# -*- coding: utf8 -*-


from aoke_spider import *

def today():
    today_name = datetime.datetime.now().strftime("%Y-%m-%d")
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('sheet 1')
    sheet.write(0, 0, u'日期')
    sheet.write(0, 1, u'星期')
    sheet.write(0, 2, u'时间')
    sheet.write(0, 3, u'联赛')
    sheet.write(0, 4, u'序号')
    sheet.write(0, 5, u'对阵球队')
    sheet.write(0, 6, u'vs')
    sheet.write(0, 7, u'对阵球队')
    sheet.write(0, 8, u'让球初盘')
    sheet.write(0, 9, u'即时')
    sheet.write(0, 10, u'终盘')
    sheet.write(0, 11, u'大小')
    sheet.write(0, 12, u'赢的终盘')
    sheet.write(0, 13, u'盘口初盘')
    sheet.write(0, 14, u'即时')
    sheet.write(0, 15, u'终盘')
    sheet.write(0, 16, u'大小球赢的终盘')
    sheet.write(0, 17, u'跑出赔率')
    sheet.write(0, 18, u'比分赔率')
    sheet.write(0, 19, u'进球数赔率')
    sheet.write(0, 20, u'进球数')
    sheet.write(0, 21, u'半全场')
    sheet.write(0, 22, u'半全场')
    touzhu_list = get_jingcai_info()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    final_list = []
    yapan_list = get_qiutan_info(date)
    for yapan in yapan_list:
        for touzhu in touzhu_list:
            if touzhu['xuhao'] == yapan['xuhao']:
                final_info = touzhu.copy()
                final_info.update(yapan)
                final_list.append(final_info)
    for final in final_list:
        i = int(final['xuhao'][-3:])
        sheet.write(i, 0, final['riqi'].decode("utf8"))
        sheet.write(i, 1, final['xingqi'].decode("utf8"))
        sheet.write(i, 2, final['shijian'].decode("utf8"))
        sheet.write(i, 3, final['liansai'].decode("utf8"))
        sheet.write(i, 4, final['xuhao'].decode("utf8"))
        if final['flag'] > 0:
            sheet.write(i, 5, final['zhudui'].decode("utf8"))
            sheet.write(i, 7, final['kedui'].decode("utf8"))
            sheet.write(i, 8, str(change(final['chupan_ya'])).decode("utf-8"))
            sheet.write(i, 9, str(change(final['jishi_ya'])).decode("utf-8") if final['jishi_ya'] else None)
        else:
            sheet.write(i, 5, final['kedui'].decode("utf8"))
            sheet.write(i, 7, final['zhudui'].decode("utf8"))
            sheet.write(i, 8, str(-change(final['chupan_ya'])).decode("utf-8") if float(change(final['chupan_ya'])) != 0.0 else u'0.0')
            if final['jishi_ya']:
                sheet.write(i, 9, str(-change(final['jishi_ya'])).decode("utf-8") if float(change(final['jishi_ya'])) != 0.0 else u'0.0')
            else:
                sheet.write(i, 9, None)
        sheet.write(i, 13, str(change_daxiao(final['chupan_daxiao'])))
        sheet.write(i, 14, str(change_daxiao(final['jishi_daxiao'])) if final['jishi_daxiao'] else None)
    wbk.save(today_name + '.xls')

if __name__ == '__main__':
    today()