# -*- coding: utf8 -*-

import requests
import xlwt
import xlrd
from xlutils.copy import copy
import os
import datetime
from lxml import etree
import re
import time

yapan_to_shuzi = {
    "平手": 0,
    "平/半": 0.25,
    "半球": 0.5,
    "半/一": 0.75,
    "一球": 1,
    "一/球半": 1.25,
    "球半": 1.5,
    "球半/两": 1.75,
    "两球": 2,
    "两/两球半": 2.25,
    "两球半": 2.5,
    "两球半/三": 2.75,
    "三球": 3,
    "三/三球半": 3.25,
    "三球半": 3.5,
    "受平/半": -0.25,
    "受半球": -0.5,
    "受半/一": -0.75,
    "受一球": -1,
    "受一/球半": -1.25,
    "受球半": -1.5,
    "受球半/两": -1.75,
    "受两球": -2,
    "受两/两球半": -2.25,
    "受两球半": -2.5,
    "受两球半/三": -2.75,
    "受三球": -3,
    "受三/三球半": -3.25,
    "受三球半": -3.5
}

xingqi_to_shuzi = {
    "周一": 1,
    "周二": 2,
    "周三": 3,
    "周四": 4,
    "周五": 5,
    "周六": 6,
    "周日": 7,
}


def get_jingcai_info():
    url = 'http://www.okooo.com/jingcai/'
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; '
                      '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E) '
    }
    response = requests.get(url, headers=headers)
    content = etree.HTML(response.content.decode('gb2312', 'ignore'))
    riqi = content.xpath('//div[@id="content"]/div[contains(@class, "cont")][2]//div[@id="ChangeDate"]/a/span[1]/text()')
    data_xingqi = '未知'
    data_riqi = "未知"
    if riqi:
        data = riqi[0].encode('utf-8')
        data_riqi = filter(lambda ch: ch in '0123456789-', data)
        data_xingqi = filter(lambda ch: ch not in '0123456789-', data)
    touzhu_infos = content.xpath('//div[@id="content"]/div[contains(@class, "cont")][2]//div[@data-morder]')
    touzhu_info_list = []
    for touzhu_info in touzhu_infos:
        duizhen_id = touzhu_info.xpath('@data-morder')[0]
        liansai_info = touzhu_info.xpath('div[@class="liansai"]/a/@title')
        if liansai_info:
            liansai = liansai_info[0].encode('utf-8')
        else:
            liansai = '未知'
        shijian_info = touzhu_info.xpath('div[@class="liansai"]/div/@mtime')
        if shijian_info:
            shijian = shijian_info[0].encode('utf-8')
        else:
            shijian = '未知'
        zhudui_info = touzhu_info.xpath('div[contains(@class, "shenpf ")]/div[@style]/div[1]//div[@title]/@title')
        if zhudui_info:
            zhudui = zhudui_info[0].encode('utf8') + '(主)'
        else:
            zhudui = '未知(主)'
        kedui_info = touzhu_info.xpath('div[contains(@class, "shenpf ")]/div[@style]/div[3]//div[@title]/@title')
        if kedui_info:
            kedui = kedui_info[0].encode("utf-8")
        else:
            kedui = '未知'
        params = {
            "action": "more",
            "LotteryNo": data_riqi,
            "MatchOrder": duizhen_id
        }
        headers = {
            'Referer': 'http://www.okooo.com/jingcai/',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; '
                      '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E) '        }
        url = 'http://www.okooo.com/jingcai/'
        response = requests.get(url, params=params, headers=headers)
        content = etree.HTML(response.content.decode('utf-8'))
        peilv = content.xpath('//div[@class="peilv_1 p_1 fff hui_colo red_colo"]/text()')
        if float(peilv[0].encode()) > float(peilv[1].encode()):
            flag = 1
        else:
            flag = -1
        infos = {
            'riqi': data_riqi,
            'xingqi': data_xingqi,
            'shijian': shijian,
            'liansai': liansai,
            'xuhao': duizhen_id,
            'zhudui': zhudui,
            'kedui': kedui,
            'flag': flag
        }
        touzhu_info_list.append(infos)
    return touzhu_info_list


def get_qiutan_info(date):
    params = {
        "date": date
    }
    url = 'http://a.haocai138.com/info/match/Jingcai.aspx'
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; '
                      '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E) '
    }
    response = requests.get(url, params=params, headers=headers)
    content = etree.HTML(response.content)
    bisai_infos = content.xpath('//tr[@gamename]')
    bisai_info_list = []
    for bisai_info in bisai_infos:
        xuhao = filter(lambda ch: ch in '0123456789-', bisai_info.xpath('td[1]/text()')[0])
        before_xuhao = str(xingqi_to_shuzi[
                               filter(lambda ch: ch not in '0123456789-', bisai_info.xpath('td[1]/text()')[0]).encode(
                                   "utf8")]) + xuhao
        url = bisai_info.xpath('td[last()-1]/a[last()]/@href')[0].split('/')[-1]
        full_url = 'http://a.haocai138.com/analysis/odds/' + url + '?' + str(int(time.time())) + '000'
        response = requests.get(full_url, headers=headers)
        pattern = 'Crown;(.*?);Bet365'
        content = re.findall(pattern, response.content)
        yapan = content[0].split(';')
        chupan = yapan[0].split(',')
        jishi = yapan[1].split(',')
        chupan_ya = chupan[8]
        chupan_daxiao = chupan[12]
        chupan_daxiao_da = chupan_daxiao[11]
        chupan_daxiao_xiao = chupan_daxiao_xiao[13]
        jishi_ya = jishi[8]
        jishi_ya = jishi_ya if jishi_ya != chupan_ya else None
        jishi_daxiao = jishi[12]
        jishi_ya_pei_shou = jishi[7]
        jishi_ya_pei_rang = jishi[9]
        jishi_daxiao_pei_da = jishi[11]
        jishi_daxiao_pei_xiao = jishi[13]
        jishi_daxiao = jishi_daxiao if jishi_daxiao != chupan_daxiao else None
        bisai_all_info = {
            'xuhao': before_xuhao,
            'chupan_ya': chupan_ya,
            'chupan_daxiao': chupan_daxiao,
            'jishi_ya': jishi_ya,
            'jishi_daxiao': jishi_daxiao,
            'jishi_ya_shou': jishi_ya_pei_shou,
            'jishi_ya_rang': jishi_ya_pei_rang,
            'jishi_daxiao_da': jishi_daxiao_pei_da,
            'jishi_daxiao_xiao': jishi_daxiao_pei_xiao,
            'chupan_daxiao_da': chupan_daxiao_da,
            'chupan_daxiao_xiao': chupan_daxiao_xiao
        }
        bisai_info_list.append(bisai_all_info)
    return bisai_info_list


def get_caiguo_info():
    url = 'http://www.okooo.com/jingcai/'
    headers = {
        'Referer': 'http://www.okooo.com/jingcai/',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; '
                      '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E) '     }
    response = requests.get(url, headers=headers)
    content = etree.HTML(response.content.decode('gb2312', 'ignore'))
    touzhu_infos = content.xpath('//div[@id="content"]/div[contains(@class, "cont")][1]/div[@class="touzhu"]/div[@data-morder]')
    date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yapan_infos = get_qiutan_info(date)
    touzhu_info_list = []
    for touzhu_info in touzhu_infos:
        duizhen_id = touzhu_info.xpath('@data-morder')[0]
        peilv_info = touzhu_info.xpath('div[contains(@class, "shenpf")]//div[contains(@class, "saiguo_color")]/div[contains(@class, "peilv")]/text()')
        if peilv_info:
            peilv = peilv_info[0].strip()
        else:
            peilv = None
        bifen_info = touzhu_info.xpath('div[@class="more weiks"]/div/p[1]/text()')
        if bifen_info:
            bifen = bifen_info[0].strip()
        else:
            bifen = None
        detail_info = get_caiguo_detail(date, duizhen_id)
        detail_info['xuhao'] = duizhen_id
        detail_info['peilv'] = peilv
        detail_info['bifen'] = bifen
        touzhu_info_list.append(detail_info)
    final_list = []
    for touzhu_info in touzhu_info_list:
        for yapan_info in yapan_infos:
            if touzhu_info['xuhao'] == yapan_info['xuhao']:
                final_info = touzhu_info.copy()
                final_info.update(yapan_info)
                final_list.append(final_info)
    return final_list


def get_caiguo_detail(date, MatchOrder):
    params = {
        "action": "more",
        "LotteryNo": date,
        "MatchOrder": MatchOrder
    }
    headers = {
        'Referer': 'http://www.okooo.com',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; '
                      '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E) '}
    url = 'http://www.okooo.com/jingcai/'
    response = requests.get(url, params=params, headers=headers)
    content = etree.HTML(response.content.decode('utf-8'))
    infos = content.xpath('//div[contains(@class, "saiguo_color")]')
    bifen_peilv = None
    jinqiu_peilv = None
    sum_jinqiu = None
    banquan_peilv = None
    banquan = None
    for info in infos:
        caiguo = info.xpath('div/div/text()')
        caiguo_info = caiguo[0]
        peilv = caiguo[1]
        if '总' in caiguo_info.encode("utf-8"):
            jinqiu_peilv = peilv
            sum_jinqiu = filter(lambda ch: ch in '0123456789>', caiguo_info.encode('utf-8'))
        elif '/' in caiguo_info:
            banquan_peilv = peilv
            banquan_info = caiguo_info.encode("utf-8").split('/')
            banquan_ban = {'胜': 'w', '平': 'd', '负': 'l'}.get(banquan_info[0], None)
            banquan_quan = {'胜': 'w', '平': 'd', '负': 'l'}.get(banquan_info[1], None)
            banquan = banquan_ban + banquan_quan
        else:
            bifen_peilv = peilv

    all_info = {
        "bifen_peilv": bifen_peilv,
        "jinqiu_peilv": jinqiu_peilv,
        "sum_jinqiu": sum_jinqiu,
        "banquan_peilv": banquan_peilv,
        "banquan": banquan,
    }
    return all_info


def change(yapan):
    try:
        return float(yapan_to_shuzi[yapan])
    except:
        return 'other'


def change_daxiao(num):
    num_list = num.split('/')
    sum_num = 0
    for num in num_list:
        sum_num += float(num)
    return sum_num / len(num_list)

if __name__ == '__main__':
    get_jingcai_info()