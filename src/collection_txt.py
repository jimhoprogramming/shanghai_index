# -*- coding: utf-8 -*-

import urllib3
from urllib import request
import json
import re
import bs4
import os
import configparser

# 读取config.cfg文件得到动态的网址和目标名称
def read_url_aimname():
    config_file_url = 'Config.cfg'
    if os.path.exists(os.path.join(os.getcwd(), config_file_url)):
        config = configparser.ConfigParser()
        config.read(config_file_url)
        data = config.get('Text_Feature', 'feature1')
        #print(data)
        #data_list = re.split(r',',data)
        data_list = eval(data)
    return data_list

# 访问网站取得数据
def get_value(url_list):
    for i in range(len(url_list)):
        if i>0:
            # 判断http 或 https
            url = url_list[i]
            #print(url)
            http = re.findall('^.*:', url)
            # 访问
            if http[0] == 'http:':
                print(' the http url = %s'%(url))
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
                response = request.urlopen(url, data=None, timeout=10)
                context = response.read()
                code = getCoding(context)
                #print(code)
                page = context.decode(code)
                print(page)
            elif http[0] == 'https:':
                print('pass')
                print(url)
            else:
                print('no http')
                print(url)
    return True


# 检查返回内容的编码格式 
def getCoding(strInput):
    '''
    获取编码格式
    '''
    try:
        strInput.decode("utf-8")
        return 'utf-8'
    except:
        pass
    try:
        strInput.decode("gb2312")
        return 'gb2312'
    except:
        pass

if __name__=='__main__':
    b= read_url_aimname()
    print(get_value(b))
    #print(clear_data(get_value(b),c))
