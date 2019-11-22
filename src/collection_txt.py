# -*- coding: utf-8 -*-

from urllib import request
import json
import re
from bs4 import BeautifulSoup
import os
import configparser

# 读取config.cfg文件得到动态的网址和目标名称
def read_url_aimname():
    config_file_url = 'Config.cfg'
    if os.path.exists(os.path.join(os.getcwd(), config_file_url)):
        config = configparser.ConfigParser()
        config.read(config_file_url)
        data = config.get('Text_Feature', 'feature1_3')
        #print(data)
        #data_list = re.split(r',',data)
        one_url = eval(data)
    return one_url

# 访问网站取得数据
def get_value(one_url):
    find_condition = []
    for i in range(len(one_url)):
        if i == 1 :
            # 判断http 或 https
            url = one_url[i]
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
                #print(page)
        if i > 1 :
            find_condition.append(one_url[i])
    # 提取有用信息
    print(find_condition)
    return take_useful_message(page, find_condition)           
    


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


# 提取齐整有用信息去掉枝节
def take_useful_message(html_origin, condition):
    data = []
    soup = BeautifulSoup(html_origin, 'html.parser')
    body = soup.body
    #print(body)
    print(condition[0])
    print(condition[1])
    tag = body.find_all(condition[0], condition[1])
    for message in tag:
        #print(message.get_text())
        data = message.get_text().split()
    print(u'data len are : {}'.format(len(data)))
    return data
    

if __name__=='__main__':
    b= read_url_aimname()
    print(b)
    print(get_value(b))
    
