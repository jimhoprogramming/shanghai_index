# -*- coding: utf-8 -*-

from urllib import request
import urllib3 
import json
import configparser
import os
import re
import pandas as pd
from bs4 import BeautifulSoup

# 读取config.cfg文件得到动态的网址和目标名称
def read_url_aimname():
    rel = []
    config_file_url = 'Config.cfg'
    if os.path.exists(os.path.join(os.getcwd(),config_file_url)):
        config = configparser.ConfigParser()
        config.read(config_file_url)
        for option in config.options('Data_Feature'):
            data = config.get('Data_Feature',option)
            rel.append(eval(data))
    return rel

# 访问网站取得数据
def get_value(url):
    # 判断http 或 https
    http = True
    if http:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        response = request.urlopen(url, data=None, timeout=10)
        page = response.read().decode('gb2312')
        #print(page)
    else:
        pass
    return page


# 数据清洗
def clear_data(data, index):
    rel = 0.0
    temp_string = re.split(r',',data)
    rel = float(temp_string[int(index)])    
    return rel

# 保存数据到cvs文件相应位置
def save_to_cvs(key_name, float_value):
    pass
    


# 提取齐整有用信息去掉枝节
def take_useful_message(html_origin, condition, mode = 0):
    data = []
    #print(html_origin)
    soup = BeautifulSoup(html_origin, 'html.parser')
    #print(soup.div)
    body = soup.div
    #print(body)
    print(condition[0])
    print(condition[1])
    print(condition[2])
    # 文本中含日期的，按条件常规查
    if mode == 0:
        tag = body.find_all([condition[1],condition[2]])
        for message in tag:
            print('message is :')
            print(message.get_text())
            data = message.get_text().split()
            #print(data)
##    # 日期在a href="/premier/2019-11/04/的情形
##    elif mode == 1:
##        find_date_obj =  re.compile(r'\d{2,4}\W*\d{1,2}\W*\d{1,2}',flags = 0)
##        tag = body.find_all(condition[0], condition[1])
##        for child_tag in tag:
##            a_tag = child_tag.find_all('a')
##            for child_a_tag in a_tag:
##                if len(child_a_tag['href'])>0 and len(child_a_tag.get_text().strip())>0:
##                    data.append(child_a_tag.get_text().strip())
##                    # 找日期特征的内容
##                    date_text = find_date_obj.search(child_a_tag['href'])
##                    date_text = date_text.group().replace(r'/',r'-')
##                    data.append(date_text)
    print(u'data len are : {}'.format(len(data)))
    return data

if __name__=='__main__':
    urls = read_url_aimname()
    for url in urls:
        if url[0] == 'other':
            print(url[-1])
            print(take_useful_message(html_origin = get_value(url[1]), condition = url[1:], mode = 0))
            
        else:
            print(url)
            print('{} = {}'.format(url[0], clear_data(get_value(url[1]),url[2])))    

