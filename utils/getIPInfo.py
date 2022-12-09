from flask import request, g
import requests
import re
import geoip2.database


class getIPInfo:
    def __init__(self, ip):
        self.ip = ip
        self.soip = 'http://txt.go.sohu.com/ip/soip'
        self.header = {
            'Host': 'www.cip.cc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'http://www.cip.cc/',
            'Upgrade-Insecure-Requests': '1'
        }

    def getIP(self):
        if request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != '127.0.0.1':  # if拿到IP
            self.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)  # 获取外网IP
        else:  # 如果没有符合的IP，默认本地
            response = requests.get(self.soip)
            text = response.text
            self.ip = re.findall('window.sohu_user_ip="(.*?)"', text, re.S)[0]
        return self.ip

    def getWea(self):
        if self.ip is None or self.ip == '127.0.0.1':
            self.getIP()
        try:
            response = requests.get(url=f'http://www.cip.cc/{self.ip}', headers=self.header)
            rerere = response.text
            rerere = re.findall('中国  (.*?)\n运营商', rerere, re.S)[0]
        except Exception as e:
            rerere = '未知'
            print(e)
        with geoip2.database.Reader("./data/GeoLite2-City.mmdb") as reader:
            c = reader.city(self.ip)
            target_city = c.city.names.get('zh-CN')  # 拿到城市，可能存在匹配不到
            if not target_city:
                target_city = '上海'
        try:
            path = f'http://wthrcdn.etouch.cn/weather_mini?city={target_city}'
            response = requests.get(path)  # 对该地址和参数进行get请求
            result = response.json()  # 将返回的结果转成json串
            if result.get("status") != 1000:
                wea = ''
            else:
                type = result.get('data').get("forecast")[0].get("type")
                high = result.get('data').get("forecast")[0].get("high")
                low = result.get('data').get("forecast")[0].get("low")
                wea = type + '，' + high + '，' + low
        except Exception as e:
            wea = ''
            print(e)
        return wea

    def getIPAddress(self):
        if self.ip is None or self.ip == '127.0.0.1':
            self.getIP()
        try:
            response = requests.get(url=f'http://www.cip.cc/{self.ip}', headers=self.header)
            rerere = response.text
            rerere = re.findall('中国  (.*?)\n运营商', rerere, re.S)[0]
        except Exception as e:
            rerere = '未知'
            print(e)
        return rerere
