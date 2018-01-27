# encoding=utf-8
import requests
import time

def get_info(mobile):
    headers={
      "Referer": "http://www.rwxgjp.com/Register.aspx",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "Origin": "http://www.rwxgjp.com",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5",
       "Accept": "*/*",
      "X-Requested-With": "XMLHttpRequest"
    }
    data = {"moblie":mobile,
            "productid":"141"}

    url='http://www.rwxgjp.com/Handler/CheckMoblie.ashx'

    response = requests.post(url=url, headers=headers,data=data)
    print(mobile,response.text)

for i in range(18512890000,18512899999):
    time.sleep(0.1)
    get_info(str(i))



