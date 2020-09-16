# -*- coding: utf-8 -*-
# for create y
import pandas as pd
import numpy as np
import easygui
import re,os
import datetime

source_url = './store_text.csv'
target_url = './train_set.csv'

def setup_choicebox(date, text):
    '''
        设定对话框
    '''
    msg = u'{} \n{}\n'.format(date, text)
    title = u'管理训练数据'
    choices = [u'喜=0', u'怒=1', u'哀=2', u'乐=3', '无影响=4']
    choice = easygui.choicebox(msg, title, choices)


    # make sure that none of the fields was left blank
    print(choice)
    return re.findall('\d.*', choice)[0]

def create_y(only_today = True):
    # 打开目标文件
    if os.path.exists(target_url):
        target_data = pd.read_csv(target_url, encoding = 'utf-8', index_col = 0)
    else:
        target_data = pd.DataFrame(columns = ['review','label'])
    # 读当天爬回来的数据文件
    source_data = pd.read_csv(source_url, encoding = 'utf-8', index_col = 0)
    # 按日期分开当天的和不是当天的数据
    sub_data_by_date_group = source_data.groupby('date')
    #print(sub_data_by_date_group.size())
    for name, group in sub_data_by_date_group:
        # 是否只如当天的记录
        today = datetime.date.strftime(datetime.date.today(),'%Y-%m-%d')
        if only_today:
            for i in np.arange(group.shape[0]):
                if group.iloc[i,0] == today:
                    x = group.iloc[i,1]
                    y = setup_choicebox(group.iloc[i,0], group.iloc[i,1])
                    print(x)
                    print(y)
                    # 逐条显示当天的
                    target_data = target_data.append({'review':x, 'label':y}, ignore_index = True)
        else:
            for i in np.arange(group.shape[0]):
                x = group.iloc[i,1]
                y = setup_choicebox(group.iloc[i,0], group.iloc[i,1])
                print(x)
                print(y)
                # 逐条显示当天的
                target_data = target_data.append({'review':x, 'label':y}, ignore_index = True)            
    # 加入到新文件里面
    target_data.drop_duplicates(inplace = True)
    target_data.to_csv(target_url, encoding = 'utf-8') 


if __name__ == '__main__':
    create_y(only_today = True)





 
