# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import os
import datetime
from urllib import request
import urllib
import re
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']= False
#
url = '../data/class_data.csv'
StockBasics_Addr = '../data/StockBasics_bk.csv'
DData_dir = '../data/DData'
month_array_url = '../data/month_data.npy'
quarter_array_url = '../data/quarter_data.npy'
#
# 直接声明用户令牌使tushare pro可用
pro = ts.pro_api('51d649f02caf6313a891d2f30d6222bfa246067d382641ddadbc3365')

def define_class():
    '''
        # 定义分类代表的个股
    '''
    class_dict_stock_list = {u'白酒':['000799','600519','000858','600197','600962'],
                             u'光伏':['300118','600089','601012','600710','601137'],
                             u'消费':['000651','603288','603899','600887','603517'],
                             u'医疗':['600276','600196','002007','002422','300760'],
                             u'黄金':['601899','600547','600988','600459','600489'],
                             u'证券':['601995','300059','601995','600999','600030'],
                             u'大盘':['601398','601288','601857','300750','601186'],
                             u'有色':['601600','603993','000060','600111','600219'],
                             u'能源':['000155','601778','601908','600886','000531'],
                             u'军工':['600072','300527','300589','300008','300659'],
                             u'芯片':['688981','600460','003026','600584','002916']
                             }
    return class_dict_stock_list

def get_stocks_k(class_dict,start_date,end_date = None):
    '''
        # 获取每个行业的龙头股指定时间段的k线值
    '''
    rel = {}
    for c in list(class_dict.keys()):
        rel[c] = []
        for s in class_dict[c]:
            #print(s)
            df = ts.get_k_data(s, start = start_date, end = end_date)
            rel[c].append(df)
    return rel

def get_percend(stocks_df):
    '''
        # 统计升高的幅度百分比
    '''
    rel = {}
    for c in list(stocks_df.keys()):
        rel[c] = []
        for s in stocks_df[c]:
            s.sort_values(by = 'date', ascending = True, inplace = True)
            #print(s)
            percend = (s.iloc[-1,3] - s.iloc[0,2])/s.iloc[0,2]
            #print(percend)
            rel[c].append(percend)
    rel = pd.DataFrame(rel)
    return rel
    

def save_to_file(series_mean, mark_date = None):
    '''
        # 保存本次结果并给予一个日期,同日期的被替代
    '''
    if mark_date is None:
        date_dt_obj =  datetime.date.today()
        str_date = datetime.date.strftime(date_dt_obj, '%Y-%m-%d')
    else:
        str_date = mark_date
    # 读旧记录
    if os.path.exists(url):
        df = pd.read_csv(url, encoding = 'utf-8', index_col = 0)
        # 检查日期有则替换，无则增加
        if str_date in df.columns:
            print(u'有今天记录，替换今天')
        else:
            print(u'增加今天')
        df[str_date] = series_mean    
    else:
        df = pd.DataFrame(series_mean, columns = [str_date])
    # 保存并替代原文件
    df.sort_index(axis = 1, ascending = True, inplace = True)
    df.to_csv(url, encoding = 'utf-8')
    return True

def plot_class_by_date():
    '''
        # 显示走势图
    '''
    # 读旧记录
    if os.path.exists(url):
        df = pd.read_csv(url, encoding = 'utf-8', index_col = 0)
        print(u'根2020-06-30日价格比较的升幅')
        print(df)
        plt.close('all')
        fig, ax = plt.subplots(2,1)
        print(ax)
        df.T.plot(ax = ax[0])
        df = df.sub(df['2021-02-01'], axis = 0)
        print(u'与本月第一日升幅比较的升幅')
        print(df)
        df.T.plot(ax = ax[1])
        plt.show()
    else:
        print(u'文件不存在无法显示！')
    return True
    
def run_todate(start_date = '2020-06-30', end_date = None):
    c = define_class()
    d = get_stocks_k(c, start_date, end_date = end_date)
    rel = get_percend(d)
    series_mean = rel.mean(0)
    save_to_file(series_mean, mark_date = end_date)
    print(series_mean)    
    return True

def get_stock_id_list(class_dict):
    rel = []
    for c in list(class_dict.keys()):
        for s in class_dict[c]:
            #print(s)
            rel.append(str(s))
    return rel
    

def get_stock_basics_bk(stockids):
    '''
        # 获得所有列表股票的上市日期
        #
        沪深上市公司基础情况替代方案：
        code,代码
        name,名称
        industry,细分行业
        area,地区
        pe,市盈率
        outstanding,流通股本
        totals,总股本(万)
        totalAssets,总资产(万)
        liquidAssets,流动资产
        fixedAssets,固定资产
        reserved,公积金
        reservedPerShare,每股公积金
        eps,每股收益
        bvps,每股净资
        pb,市净率
        timeToMarket,上市日期
    '''
    
    if (os.path.exists(StockBasics_Addr)==False):
        basic_df = pro.stock_basic()
        basic_df.reset_index(inplace=True)
        basic_df.to_csv(StockBasics_Addr,encoding='utf-8')
    else:
        basic_df=pd.read_csv(StockBasics_Addr, dtype={'symbol':str}, index_col = 0)
    print(basic_df.shape)
    EpsNear = basic_df[basic_df['symbol'].isin(stockids)][['symbol','name','industry','list_date']] 
    print(EpsNear.shape)
    print(len(stockids))
    totals = []
    outstanding = []
    esp = []
    holders = []
    name = []
    for stock in EpsNear['symbol']:
        url = 'http://hq.sinajs.cn/list=fillin_i'.replace('fillin', GetMarket(stock))
        print(url)
        my_request = request.urlopen(url)
        try:
            str_data = my_request.read()
        except:
            str_data = None
        #
        try:
            str_data = str_data.decode('gb2312')
        except:
            try:
                str_data = str_data.decode('utf-8')
            except:
                str_data = str_data.decode('gbk')
        str_data = re.findall('"A.*"',str_data)
        data_list = str_data[0].split(',')
        totals.append(data_list[7])
        outstanding.append(data_list[8])
        esp.append(data_list[4])
        holders.append(data_list[7])
        name.append(data_list[22])
        #break
    EpsNear['ck_name'] = name
    EpsNear['totals'] = totals
    EpsNear['outstanding'] = outstanding
    EpsNear['esp'] = esp
    EpsNear['holders'] = holders
    EpsNear['code'] = EpsNear['symbol']
    EpsNear['timeToMarket'] = EpsNear['list_date']
    return EpsNear
    
def GetMarket(StockId):
    '''
        市场前序增添工具
    '''
    Rel = None
    TempRel = re.match('0|3',StockId,flags=0)
    if TempRel is not None:
        Rel = 'sz'+ StockId
    else:
        Rel = 'sh' + StockId
    return Rel


def get_hist_by_startdate(basic_df):
    '''
        # 下载列表中数据的全部日线并保存在数据目录备用
    '''
    m = basic_df.shape[0]
    for i in range(m):
        start_date = basic_df.iloc[i,2]
        start_date = start_date[0:4] + '-' + start_date[4:6] + '-' + start_date[6:]
        stock_id = basic_df.iloc[i,0]
        print('股票:{}, 上市日期:{}'.format(basic_df.iloc[i,1], start_date))
        df = ts.get_k_data(stock_id, start = start_date)    
        stock_url = DData_dir + '/' + str(stock_id) + '.csv'
        df.to_csv(stock_url, encoding = 'utf-8')
    return True

def get_stock_id_and_startdate(stock_id_list):
    basic_df = pd.read_csv(StockBasics_Addr, dtype={'symbol':str, 'list_date':str}, index_col = 0)
    EpsNear = basic_df[basic_df['symbol'].isin(stock_id_list)][['symbol','name','list_date']] 
    return EpsNear
    

def find_max_date_data(stock_id_list):
    '''
        # 输入日期找到有最大日期的一个作为输出
    '''
    rel = []
    for stock_id in stock_id_list:
        stock_url = DData_dir + '/' + str(stock_id) + '.csv'
        df = pd.read_csv(stock_url, dtype = {'code':str, 'date':str}, index_col = 0)
        df.sort_values(by = 'date', ascending = True, inplace = True)
        rel.append(df.iloc[0,0])
    return min(rel)

def create_segment_array(class_dict, start_date = '1994-01-06'):
    '''
        # 定义每个区段的时间分隔形式，输出日期对数组
        # 每30个日期输出一个日期值
        # 每30 x 3 季度输出一个日期值
        # 输出两个4维数组
    '''
    start_year = int(start_date[0:4])
    y_counts = datetime.datetime.now().year - start_year
    print('总年数：{}'.format(y_counts))
    class_counts = len(class_dict)
    stock_counts = len(class_dict[list(class_dict.keys())[0]])
    print('分类数{}，每类含股票数：{}'.format(class_counts,stock_counts))
    month_array = np.zeros((y_counts,12,class_counts,stock_counts))
    quarter_array = np.zeros((y_counts,4,class_counts,stock_counts))    
    return month_array,quarter_array

def caculate_percend(month_array, quarter_array,class_dict, start_date =  '1994-01-06'):
    '''
        # 统计百分比出现的概率，按照时间分隔，按类别分隔。
    '''
    start_year = int(start_date[0:4])
    y_counts,m_counts,c_counts,s_counts = month_array.shape
    _,m_q_counts,_,_ = quarter_array.shape
    for c in np.arange(c_counts):
        class_name = list(class_dict.keys())[c]
        for s in np.arange(s_counts):
            stock_id = class_dict[class_name][s]
            # read stock data
            stock_url = DData_dir + '/' + str(stock_id) + '.csv'
            print('读取原始数据文件地址：{}'.format(stock_url))
            df = pd.read_csv(stock_url, dtype = {'code':str, 'date':str}, index_col = 0)
            df['y_m_date'] = df['date'].str[:7]
            for y in np.arange(y_counts):
                year = str(start_year + y)
                print('计算年份为:{}'.format(year))
                # 月
                for m in np.arange(m_counts):
                    month = str(m + 1).zfill(2)
                    # fill 
                    month_array[y,m,c,s] = get_month_percend(df = df, condiction = [year,month], is_quarter = False)
                # 季
                print('========')
                for m in np.arange(m_q_counts):
                    month = str(m).zfill(2)
                    quarter_array[y,m,c,s] = get_month_percend(df = df, condiction = [year,month], is_quarter = True)
                print('--------')
                
            print('\n')
        print('--------{}类股票入完-------\n'.format(class_name))
    # 保存文件
    np.save(month_array_url, month_array)
    np.save(quarter_array_url, quarter_array)
    return month_array, quarter_array
    
def get_month_percend(df,condiction, is_quarter = False):
    '''
    # 计算实现的子函数。核心函数。
    '''
    percend = 0
    #print(df.head(5))
    #print(condiction)
    y_m = [str(condiction[0]) + '-' + str(condiction[1])]
    #y_m = '1997-09'
    if is_quarter:
        y_m = [str(condiction[0]) + '-' + str(i + int(condiction[1]) * 3).zfill(2) for i in np.arange(1,4)]
    print('月或季的范围：{}'.format(y_m))    
    y_m_df = df[df['y_m_date'].isin(y_m)]
    print('符合范围的数据维度:{}'.format(y_m_df.shape))
    if y_m_df.shape[0] >= 2:
        #print(y_m_df)
        s = y_m_df.sort_values(by = 'date', ascending = True, inplace = False)
        #print(s)
        percend = (s.iloc[-1,3] - s.iloc[0,2])/s.iloc[0,2]
    print('计算幅度百分比小数值是：{}'.format(percend))
    return percend

def run_get_hist_data():
    '''
        批处理运行获得历史所有股票数据并保存下来。（年只须一次）
    '''
    c = define_class()
    stock_id_list = get_stock_id_list(class_dict = c)
    get_stock_basics_bk(stockids = stock_id_list)
    stocks_df = get_stock_id_and_startdate(stock_id_list = stock_id_list)
    get_hist_by_startdate(basic_df = stocks_df)
    return True

def run_caculate_percend():
    '''
        批处理运行计算所有数据的月、季升跌百分比并保存下来。（年只须一次）
    '''
    c = define_class()
    month_array,quarter_array = create_segment_array(class_dict = c)
    print(month_array.shape)
    print(quarter_array.shape)
    caculate_percend(month_array = month_array, quarter_array = quarter_array, class_dict = c, start_date = '1994-01-06')
    return True



def plot_class_mean(rel, month, class_n):
    '''
        # 找出最能赚钱的类别
    '''
    class_dict = define_class()
    start_date = '1994-01-06'
    start_year = int(start_date[0:4])
    # make df
    y_counts, c_counts, _ = rel.shape
    show_dict = {}
    for c in np.arange(c_counts):
        class_name = list(class_dict.keys())[c]
        #print(class_name)
        show_dict[class_name] = rel[:,c,0].tolist()
    #
    columns = [str(start_year + y) for y in np.arange(y_counts)]
    show_df = pd.DataFrame(show_dict,index = columns)
    # show
    #print(show_df)
    plt.close('all')
    fig, ax = plt.subplots(2,2)
    #show_df.diff().hist(alpha = 1.0, bins=10, stacked=False)
    show_df.iloc[:,int(class_n)].hist(ax = ax[0,0], alpha = 1.0, bins=10, stacked=False)
    ax[0,0].set_xlabel(list(class_dict.keys())[int(class_n)])
    show_df.iloc[:,int(class_n)].plot.barh(ax = ax[0,1])
    ax[0,1].set_xlabel(list(class_dict.keys())[int(class_n)])
    show_df.plot.kde(ax = ax[1,0])
    ax[1,0].set_xlabel(u'所有类别历年来{}月份概率率分布kde'.format(str(int(month) + 1)))
    plt.show()

def plot_find_stock(one_class_array, class_n):
    '''
        # 在类别中找最能赚钱的股票
    '''
    class_dict = define_class()
    start_date = '1994-01-06'
    start_year = int(start_date[0:4])
    class_dict = define_class()
    # make df
    y_counts, m_counts, s_counts = one_class_array.shape
    print(one_class_array.shape)
    month_mean_dict = {}
    year_mean_dict = {}
    class_name = list(class_dict.keys())[int(class_n)]
    year_index = [str(start_year + y) for y in np.arange(y_counts)]
    month_index = [str(m + 1) + u'月' for m in np.arange(m_counts)]
    # 按股票分列
    for s in np.arange(s_counts):
        stock_id_name = class_dict[list(class_dict.keys())[int(class_n)]][s]
        # 按月平均。显示每年每只股票中最好收益的股票
        month_mean = np.mean(one_class_array, axis = 1, keepdims = True)
        month_mean_dict[stock_id_name] = month_mean[:,0,s].tolist()
        # 按年平均。显示每月每只股票中最好收益的股票
        year_mean = np.mean(one_class_array, axis = 0, keepdims = True)
        year_mean_dict[stock_id_name] = year_mean[0,:,s].tolist()
    #
    month_mean_df = pd.DataFrame(month_mean_dict, index = year_index)
    year_mean_df = pd.DataFrame(year_mean_dict, index = month_index)
    # show
    #print(month_mean_df)
    #print(year_mean_df)
    plt.close('all')
    fig, ax = plt.subplots(1,2)
    month_mean_df.plot.barh(ax = ax[0])
    year_mean_df.plot.barh(ax = ax[1])
    ax[0].set_xlabel(u'历史年份12个月累加计平均值')
    ax[1].set_xlabel(u'显示每个月表现最好的')
    fig.suptitle(u'类别:{}'.format(class_name), fontsize=12, fontweight='bold')
    plt.show()
    return True

def plot_need(month = 0, class_n = 0):
    '''
        # 输出图表
    '''

    m_array = np.load(month_array_url)
    q_array = np.load(quarter_array_url)
    print(m_array.shape)
    # years, months, classes, stockids
    #
    # 判断是否看某类别个股12个月的年平均盈收百分比
    if month is None:
        need_array = m_array[:,:,int(class_n),:]
        #rel = np.mean(need_array, axis = 0, keepdims = True)
        #print(rel.shape)
        plot_find_stock(one_class_array = need_array, class_n = class_n)
    else:
        need_array = m_array[:,int(month),:,:]
        rel = np.mean(need_array, axis = -1, keepdims = True)
        plot_class_mean(rel = rel, month = month, class_n = class_n)
    return True

if __name__=='__main__':
    '''
    # test near day percend
    run_todate()
    plot_class_by_date()    
    '''
    '''
    # test get max data date
    c = define_class()
    stock_id_list = get_stock_id_list(class_dict = c)
    start_date = find_max_date_data(stock_id_list = stock_id_list)
    print(start_date)
    '''
    '''
    # test create rel array
    run_caculate_percend()
    '''
    # plot result
    #class = ['0白酒', '1光伏', '2消费', '3医疗', '4黄金', '5证券', '6大盘', '7有色', '8能源', '9军工', '10芯片']
    plot_need(month = None, class_n = 7)
    






