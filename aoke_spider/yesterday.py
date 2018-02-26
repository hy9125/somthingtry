# -*- coding: utf8 -*-


from aoke_spider import *

def Yesterday():
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday_name = yesterday.strftime("%Y-%m-%d")
    if os.path.exists(yesterday_name + '.xls'):
        rb = xlrd.open_workbook(yesterday_name + '.xls')
        rs = rb.sheet_by_index(0)
        wb = copy(rb)
        ws = wb.get_sheet(0)
        caiguo_infos = get_caiguo_info()
        for caiguo_info in caiguo_infos:
            i = int(caiguo_info['xuhao'][-3:])
            bifen = caiguo_info['bifen'] if caiguo_info['bifen'] else None
            rangqiu_ya = None
            daxiao_jieguo = None
            rangqiu_peilv = None
            daxiao_ya = None
            daxiao_peilv = None
            if bifen:
                zhudui = rs.cell(i, 5).value
                zhudui_bifen = float(bifen.split(':')[0])
                kedui_bifen = float(bifen.split(':')[1])
                if '(' in zhudui:
                    bifen = bifen
                else:
                    bifen = str(int(kedui_bifen)) + ':' + str(int(zhudui_bifen))
                sum_jinqiu = zhudui_bifen + kedui_bifen
                rangqiu_ya = change(caiguo_info['jishi_ya']) if caiguo_info['jishi_ya'] else change(
                    caiguo_info['chupan_ya'])
                rangqiu = zhudui_bifen - kedui_bifen
                if rangqiu > rangqiu_ya:
                    rangqiu_peilv = float(caiguo_info['jishi_ya_shou']) * 100
                elif rangqiu < rangqiu_ya:
                    rangqiu_peilv = float(caiguo_info['jishi_ya_rang']) * 100
                else:
                    rangqiu_peilv = u'走'
                if '(' not in zhudui:
                    rangqiu_ya = -rangqiu_ya
                # daxiao_ya = change_daxiao(caiguo_info['jishi_daxiao']) if caiguo_info[
                #     'jishi_daxiao'] else change_daxiao(caiguo_info['chupan_daxiao'])
                daxiao_ya = change_daxiao(caiguo_info['chupan_daxiao'])
                if sum_jinqiu > daxiao_ya:
                    daxiao_peilv = float(caiguo_info['chupan_daxiao_da']) * 100
                    daxiao_jieguo = u'大'
                elif sum_jinqiu < daxiao_ya:
                    daxiao_peilv = float(caiguo_info['chupan_daxiao_xiao']) * 100
                    daxiao_jieguo = u'小'
                else:
                    daxiao_peilv = u'走'
                    daxiao_jieguo = u'走'
            ws.write(i, 10, str(rangqiu_ya))
            ws.write(i, 11, daxiao_jieguo)
            ws.write(i, 12, rangqiu_peilv)
            ws.write(i, 15, str(daxiao_ya))
            ws.write(i, 16, daxiao_peilv)
            ws.write(i, 6, bifen)
            ws.write(i, 17, caiguo_info['peilv'])
            ws.write(i, 18, caiguo_info['bifen_peilv'])
            ws.write(i, 19, caiguo_info['jinqiu_peilv'])
            ws.write(i, 20, caiguo_info['sum_jinqiu'])
            ws.write(i, 21, caiguo_info['banquan_peilv'])
            ws.write(i, 22, caiguo_info['banquan'])
        wb.save(yesterday_name + '.xls')
    else:
        print("不进行补全")

if __name__ == '__main__':
    Yesterday()