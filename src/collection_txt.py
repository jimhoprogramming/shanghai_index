# -*- coding: utf-8 -*-

from urllib import request
import json
import re
from bs4 import BeautifulSoup
import os
import configparser
import numpy as np
import pandas as pd
import datetime as dt
import tushare as ts
import threading

# 读取config.cfg文件得到动态的网址list
def get_urls():
    rel = []
    config_file_url = 'Config.cfg'
    if os.path.exists(os.path.join(os.getcwd(), config_file_url)):
        config = configparser.ConfigParser()
        config.read(config_file_url)
        # 加入循环读取文本setion内部的option
        for option in config.options('Text_Feature'):
            data = config.get('Text_Feature', option)
            rel.append(eval(data))
    return rel

# 访问网站取得数据
def get_value(one_url):
    find_condition = []
    for i in np.arange(len(one_url)):
        if i == 1 :
            # 判断http 或 https
            url = one_url[i]
            #print(url)
            http = re.findall('^.*:', url)
            # 访问
            if http[0] == 'http:':
                print(' the http url = {}'.format(url))
                response = request.urlopen(url, data=None, timeout=10)
            else:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
                url = request.Request(url, headers = headers)
                response = request.urlopen(url, data=None, timeout=10)
            context = response.read()
            code = getCoding(context)
            page = context.decode(code)
            #print(u'debug origin response : {}'.format(page))
        if i > 1 :
            find_condition.append(one_url[i])
    # 提取有用信息
    #print(find_condition)
    return take_useful_message(page, find_condition, mode = find_condition[-1])           
    


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
def take_useful_message(html_origin, condition, mode = 0):
    data = []
    soup = BeautifulSoup(html_origin, 'html.parser')
    body = soup.body
    #print(body)
    print(condition[0])
    print(condition[1])
    print(condition[2])
    # 文本中含日期的，按条件常规查
    mode = condition[2]
    if mode == 0:
        tag = body.find_all(condition[0], condition[1])
        for message in tag:
            #print(message.get_text())
            data = message.get_text().split()
            #print(data)
    # 日期在a href="/premier/2019-11/04/的情形
    elif mode == 1:
        find_date_obj =  re.compile(r'\d{2,4}\W*\d{1,2}\W*\d{1,2}',flags = 0)
        tag = body.find_all(condition[0], condition[1])
        for child_tag in tag:
            a_tag = child_tag.find_all('a')
            for child_a_tag in a_tag:
                if len(child_a_tag['href'])>0 and len(child_a_tag.get_text().strip())>0:
                    data.append(child_a_tag.get_text().strip())
                    # 找日期特征的内容
                    date_text = find_date_obj.search(child_a_tag['href'])
                    date_text = date_text.group().replace(r'/',r'-')
                    data.append(date_text)
    elif mode == 2:
        tag = body.find_all(condition[0], condition[1])
        for message in tag:
            data = message.get_text().split()
            # 将正文日期变更为统一的横线日期格式
            temp_data = []
            find_data_obj = re.compile(r'\d{2,4}\D*\d{0,2}\D*\d{0,2}\D*', flags = 0)
            for text in data:
                rel = find_data_obj.match(text)
                if rel and len(text)<=11:
                    date_text = re.sub(r'\D',r'-',rel.group())
                    rel = date_text[0:10]
                else:
                    rel = text
                temp_data.append(rel)
            data = temp_data
    elif mode == 3:
        tag = body.find_all(condition[0], condition[1])
        for message in tag:
            data = message.get_text().split()
            #print(data)
            # 将正文日期变更为统一的横线日期格式
            temp_data = []
            find_data_obj_1 = re.compile(r'\d{2,4}\D*\d{0,2}\D*\d{0,2}\D*', flags = 0)
            find_data_obj_2 = re.compile(r'[小时,分钟]以前', flags = 0)
            for text in data:
                rel = find_data_obj_1.match(text)
                if rel and len(text)<=11:
                    date_text = re.sub(r'\D',r'-',rel.group())
                    rel = date_text[0:10]
                elif find_data_obj_2.match(text):
                    rel = str(dt.datetime.now().year) + r'-' + str(dt.datetime.now().month) + r'-' + str(dt.datetime.now().day) 
                else:
                    rel = text
                temp_data.append(rel)
            data = temp_data
            #print(data)
    print(u'data len are : {}'.format(len(data)))
    return data

# 按日期，内容入成文件
def write_to_file(data_list, file_name, mode = 'create'):
    # 找日期特征的内容
    #find_date_obj =  re.compile(r'\d{2,4}\W*\d{0,2}\W*\d{0,2}',flags = 0)
    find_date_obj =  re.compile(r'\d{2,4}-\d{0,2}-\d{0,2}',flags = 0)
    date_list = []  
    text_list = []
    text_temp = ''
    for text in data_list:
        rel = find_date_obj.match(text)
        if rel:
            date_list.append(rel.group())
            text_list.append(text_temp)
            text_temp = ''
        else:
            text_temp = text_temp + text
    #print('text : {}'.format(text_list))
    #print('date : {}'.format(date_list))
    rel = make_pandas(date_list, text_list, mode = mode, file_name = file_name)
    #print(rel)
    rel.to_csv(file_name, encoding = 'utf-8')
    return len(data_list)

    

def make_pandas(date_list, text_list, mode, file_name):    
    if len(date_list) == len(text_list):
        rel = pd.DataFrame(data = {'date':date_list, 'text':text_list}, index = np.arange(len(date_list)))
        if mode == 'create':
            pass
        else:        
            df = pd.read_csv(file_name,encoding = 'utf-8', index_col = 0)
            rel = pd.concat([df, rel], axis = 0, ignore_index = True)
    return rel

def StrDateAdd(strDate,n):
    '''
        功能：日期字串加减
    '''    
    #字串变datetime        
    DateTimeObj=dt.datetime.strptime(strDate,'%Y-%m-%d')
    #实现加减
    TempDateTimeObj = DateTimeObj + dt.timedelta(days=n)
    Rel=dt.datetime.strftime(TempDateTimeObj,'%Y-%m-%d')
    return Rel

def get_tushare_txt(date, file_name = '', mode = 'append'):
    # init
    pro = ts.pro_api(token = '51d649f02caf6313a891d2f30d6222bfa246067d382641ddadbc3365')
    start_date = str(date) + ' ' + '00:00:00'
    end_date = StrDateAdd(date,1) + ' ' + '00:00:00'
    # get df
    rel = pro.major_news(src = '', start_date = start_date, end_date = end_date)  # fields='title,content'
    # adjust
    rel['pub_time'] = rel['pub_time'].apply(lambda s:s[0:10])
    new_df = pd.DataFrame({'date':rel['pub_time'].tolist(), 'text':rel['title'].tolist()})
    if mode == 'create':
        pass
    else:        
        df = pd.read_csv(file_name,encoding = 'utf-8', index_col = 0)
        rel = pd.concat([df, new_df], axis = 0, ignore_index = True)
        rel.to_csv(file_name, encoding = 'utf-8')
    return new_df
    
def netbugger(url, mode = 'append'):
    x = get_value(one_url = url)
    return write_to_file(data_list = x , file_name = './store_text.csv', mode = mode)    
    

class bugger_thread(threading.Thread):
    def __init__(self, target, args = ()):
        super(bugger_thread, self).__init__(target = target, args = args, daemon = True)
        self.func = target
        self.args = args
        self.result = None
    def run(self):
        self.result = self.func(*self.args)
    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None


if __name__=='__main__':
    
    urls_list = get_urls()
    n = 1
    for url in urls_list:
        print(urls_list)
        x = get_value(one_url = url)
        if n == 0:
            mode = 'create'
        else:
            mode = 'append'
        write_to_file(data_list = x , file_name = './store_text.csv', mode = mode)
        n += 1
    
    a = get_tushare_txt(date = '2020-10-26', file_name = './store_text.csv', mode = 'append')


