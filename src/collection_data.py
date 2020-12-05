# -*- coding: utf-8 -*-

from urllib import request
import json
import configparser
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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
        try :
            page = response.read().decode('gb2312')
        except:
            page = response.read().decode('utf-8')
        #print(page)
    else:
        pass
    return page

def get_value_cpi_urllib(url):
    # 判断http 或 https
    http = True
    if http:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        req = request.Request(url, data=None, headers=headers, method='GET')
        response = request.urlopen(req)
        #print(response.read())
        try :
            page = response.read().decode()
        except:
            page = response.read().decode('utf-8')
    else:
        pass
    page = json.loads(page)
    print(page.keys())
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
def take_useful_message(html_origin, index):
    rel = html_origin['returndata']['datanodes'][int(index)]['data']['data']
    return rel

if __name__=='__main__':
    urls = read_url_aimname()
    for url in urls:
        if url[0] in ['cpi','gdp']:
            print(take_useful_message(html_origin = get_value_cpi_urllib(url[1]), index = url[-1]))
        else:
            pass
##            print(url)
##            print('{} = {}'.format(url[0], clear_data(get_value(url[1]),url[2])))    

