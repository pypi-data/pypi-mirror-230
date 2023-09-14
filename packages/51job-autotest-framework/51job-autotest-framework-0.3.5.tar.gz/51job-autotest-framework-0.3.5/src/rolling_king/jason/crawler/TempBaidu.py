#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/10/24 5:42 PM
# @Author  : zhengyu.0985
# @FileName: TempBaidu.py
# @Software: PyCharm

import requests
from bs4 import BeautifulSoup

fileObj = open("/Users/admin/Desktop/baidu.html", mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
print("文件名: ", fileObj.name)
print("是否已关闭 : ", fileObj.closed)
print("访问模式 : ", fileObj.mode)
str_list = fileObj.readlines()
val = ''
for curr in str_list:
    val += curr
# print(val)

soup = BeautifulSoup(val, "lxml")
print(type(soup))
# print(soup.find('a', class_='pagenum').text)
div_tag = soup.find('div', attrs={'class': ['c-row', 'content-wrapper_1SuJ0']})
print('-------------------')
print(f'div_tag={div_tag}')
# page_num: int = len(ul_tag.find_all('li'))

cookie = "BIDUPSID=4A1485563FA4A8F48BBA72A0DE6C86DD; PSTM=1666270645; BAIDUID=4A1485563FA4A8F4BC48518904109E08:FG=1; BD_UPN=123253; MCITY=-75:; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=36548_37358_37299_36885_37628_36807_36789_37540_37499_26350; BAIDUID_BFESS=4A1485563FA4A8F4BC48518904109E08:FG=1; delPer=0; BD_CK_SAM=1; PSINO=2; BA_HECTOR=0g85000la50k252l0424dqlu1hlcni51b; ZFY=6deFW77nFLKhW:A5JxO6akg7YzaDrDvStePnOta1Ka3U:C; H_PS_645EC=c8e7bAhaJW/MO9zWkp/H2nIXr8Xy3k5JAZTecHXru40trcMBk/SJguwj7SY; COOKIE_SESSION=3_0_8_9_5_17_0_1_7_6_1_3_28_0_2_0_1666604643_0_1666604641|9#0_0_1666604641|1; BDSVRTM=0; WWW_ST=1666605811625"
url_str = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word=%E5%8D%97%E9%80%9A&x_bfe_rqs=03E80&x_bfe_tjscore=0.100000&tngroupname=organic_news&newVideo=12&goods_entry_switch=1&rsv_dl=news_b_pn&pn=10"
# url_str = "https://www.baidu.com/s?ie=utf-8&medium=0&rtt=1&bsst=1&rsv_dl=news_t_sk&cl=2&wd=%E5%8D%97%E9%80%9A&tn=news&rsv_bp=1&rsv_sug3=1&rsv_sug1=2&rsv_sug7=100&rsv_sug2=0&oq=&rsv_btype=t&f=8&rsv_sug4=918&rsv_sug=1"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "cookie": "",
    # "Host": "www.baidu.com"
    # "Referer": "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word=南通&x_bfe_rqs=03E80&x_bfe_tjscore=0.100000&tngroupname=organic_news&newVideo=12&goods_entry_switch=1&rsv_dl=news_b_pn&pn=10"
}

headers['cookie'] = cookie
resp = requests.get(url=url_str, headers=headers)
print(resp.text)
