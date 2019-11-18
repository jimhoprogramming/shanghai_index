# -*- coding: utf-8 -*-

from urllib import request
import urllib3 
import json
import configparser
import os
import re
import pandas as pd

# 读取config.cfg文件得到动态的网址和目标名称
def read_url_aimname():
    config_file_url = 'Config.cfg'
    if os.path.exists(os.path.join(os.getcwd(),config_file_url)):
        config = configparser.ConfigParser()
        config.read(config_file_url)
        data = config.get('Data_Feature','feature1')
        key_name, url, index = eval(data)
    return key_name, url, index

# 访问网站取得数据
def get_value(url):
    # 判断http 或 https
    http = True
    if http:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        response = request.urlopen(url, data=None, timeout=10)
        page = response.read().decode('gb2312')
    else:
        pass
    return page

# 数据清洗
def clear_data(data, index):
    rel = 0.0
    #temp_string = re.findall('\d.*,',data)
    temp_string = re.split(r',',data)
    #print(temp_string[0])
    #temp_string = eval('[' + temp_string[0] + ']')
    #print(temp_string)
    rel = float(temp_string[int(index)])    
    return rel

# 保存数据到cvs文件相应位置
def save_to_cvs(key_name, float_value):
    pass
    


if __name__=='__main__':
    a , b, c= read_url_aimname()
    print(get_value(b))
    print(clear_data(get_value(b),c))    

