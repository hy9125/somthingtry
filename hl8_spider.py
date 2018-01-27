# encoding=utf-8
import requests
import json

headers = {
    "Host": "www4.hl8king.com",
    "Referer": "https://www4.hl8king.com/login.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0"
}

s = requests.Session()


def login(orders):
    homedoxurl = 'https://www4.hl8king.com/home.dox'
    response = s.post(homedoxurl)
    login_before_url ='https://www4.hl8king.com/member!getAvailableDomains.do'
    response = s.get(login_before_url)
    login_url_base = 'https://www.hl8king.com/login.html'
    response = s.get(login_url_base, allow_redirects=True)
    print(s.cookies.get('homeDox'))
    login_url = 'https://www4.hl8king.com/mLogin!login.do'
    data = {"username": "aerbeisi", "password": "162804Jiang"}
    response = s.post(login_url, data=data, headers=headers, allow_redirects=False)
    info = json.loads(response.text)
    if info['code'] == 1:
        print("login success")
        token = info['data']['token']
        load_draws(orders, token)
    else:
        print("login error")


def load_draws(orders, token):
    headers = {
        "Host": "www4.hl8king.com",
        'Content-Type': "application/x-www-form-urlencoded",
        "Referer": "https://www4.hl8king.com/cp/hl8/index.jsp?g=SD11X5&token=" + str(token) + "&acctName=aerbeisi",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    }
    response = s.get('https://www4.hl8king.com/cp.html?g=CD11X5', headers=headers)
    print(response.text)
    headers = {
        "Host": "www4.hl8king.com",
        'Content-Type': "application/x-www-form-urlencoded",
        "Referer": "https://www4.hl8king.com/cp/hl8/index.jsp?g=SD11X5&token=" + str(token) + "&acctName=aerbeisi",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    }
    draws_url = "https://www4.hl8king.com/cp/loadDrawsForCno.do"
    data = {"siteCode": "SD11X5", "s": 10}
    response = s.post(draws_url, data=data, headers=headers)
    info = json.load(response.text)
    pay_caipiao(orders=orders, id=info[1]['id'], token=token)


def pay_caipiao(orders, id, token):
    pay_url = 'https://www4.hl8king.com/cp/confirmOrder.do'
    data = {
        "orders": "Fe" + orders + ".",
        "draws": [{"draw": {"id": id}, "multiply": "1"}],
        "flag": ["N"],
        "isCno": "false",
        "prize": 1910,
        "unit": 4,
        "rebate": 0,
        "cnoSetting": "N",
        "whichClientType": "PC"
    }
    headers = {
        "Host": "www4.hl8king.com",
        "Referer": "https://www4.hl8king.com/cp/hl8/index.jsp?g=SD11X5&token=" + str(token) + "&acctName=aerbeisi",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    }
    response = s.post(pay_url, data=data, headers=headers)
    if response.status_code == 200:
        pass
    else:
        print("error")


if __name__ == '__main__':
    orders = '0304060708'
    login(orders)
