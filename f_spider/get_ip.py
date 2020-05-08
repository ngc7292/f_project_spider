#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ngc7293'
__mtime__ = '2020/4/18'
"""
import requests
from bs4 import BeautifulSoup
import json
import random


def crawl_ips():
    # 爬取西刺网代理ip
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
    }
    ip_poll = []
    for i in range(1, 30):
        # print("==================", i)
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        text = re.text
        soup = BeautifulSoup(text,features="lxml")
        tr_list = soup.select("tr")
        tr_list = tr_list[1:]
        for td_list in tr_list:
            td_ip = td_list.select("td")[1].get_text()
            td_port = td_list.select("td")[2].get_text()
            http_type = td_list.select("td")[5].get_text()
            speed = float((td_list.select("td")[6].div.get('title'))[:-1])
            if speed > 1:
                continue
            if judge_ip(http_type,td_ip,td_port):
                ip_poll.append([http_type, td_ip, td_port, speed])
    return ip_poll


def judge_ip(http_type, ip, port):
    # 判断ip是否可用
    http_url = "http://www.baidu.com"
    proxy_url = "{0}://{1}:{1}".format(http_type, ip, port)
    try:
        proxy = {'http_type': ip + ":" + port}
        response = requests.get(http_url, proxies=proxy)
    except Exception as e:
        # print("Invalid ip and port: " + ip)
        return False
    else:
        code = response.status_code
        if code >= 200 and code < 300:
            return True
        else:
            return False

def save_ip():
    ip_poll = crawl_ips()
    with open('ip.db','wb') as fp:
        fp.write(json.dumps(ip_poll).encode("utf-8"))
        
def get_ip_from_web():
    return crawl_ips()
    
def get_ip_form_db():
    with open('ip.db','rb') as f:
        f_data = f.read()
        f_data = json.loads(f_data.decode("utf-8"))
        return random.sample(f_data,1)[0]
    
if __name__ == "__main__":
    pass
    # save_ip()
    # print(get_ip_form_db())
# getip = GetIP()
# print(getip.get_random_ip())
