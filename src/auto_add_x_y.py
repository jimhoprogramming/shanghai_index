# -*- coding: utf-8 -*-
import datetime, time
import pandas as pd
import numpy as np
import os
import collection_txt as ct
import collection_data as cd
import collection_index as ci
import wx
import class_percend
import predict
import datetime


# 常驻运行按时启动某一函数
class UIFrame(wx.Frame):
    def __init__(self, parent, title):
        #主框架SetMaxSize((953,640))
        super(UIFrame, self).__init__(parent,
                                      title = title,
                                      size = (300,150),
                                      style = wx.DEFAULT_FRAME_STYLE)
        #self.SetMaxSize((1024,738))
        self.SetBackgroundColour((0,255,0,0))
        #定义一个计时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__OnTimer, self.timer)
        #绑定事件
        self.Bind(wx.EVT_RIGHT_DOWN, self.__OnOneRun, self) 
        self.Bind(wx.EVT_LEFT_DOWN, self.__OnClassPercend, self)
        self.Bind(wx.EVT_MIDDLE_DCLICK, self.__OnPredict, self)
        #更新尺寸
        self.SetAutoLayout(1)
        #显示界面
        self.Centre()
        self.Show()
        self.timer.Start(1000 * 60 * 30)
        
    def __OnTimer(self, event):
        # 设定24时制几时运行一次
        c = self.__check_timming(6)
        print(u'时间到')
        print(u'可以运行吗：{}'.format(c))
        if c:
            data_df = run()
            
    def __OnOneRun(self, event):
        # 立即运行一次数据收集
        data_df = run()
        
    def __check_timming(self, str_time):
        Now=time.localtime()
        MinToHour=Now.tm_min*1.0/60
        NowHours=Now.tm_hour+MinToHour
        print(u'系统时间{}'.format(NowHours))
        if str_time < NowHours and NowHours < (str_time + 0.5):
            return True
        else:
            return False
        
    def __OnClassPercend(self, event):
        # 运行按行业比较价格升跌百分比
        class_percend.run_todate()
        class_percend.plot_class_by_date()

    def __OnPredict(self, event):
        # 运行预测指数的最低跌幅
        date_dt_obj =  datetime.date.today()
        str_date = datetime.date.strftime(date_dt_obj, '%Y-%m-%d')
        predict.net = define_model()
        predict.predict(net = net, date = str_date)
        
def run():
    # 打开文本数据追加当天资讯类数据
    today = datetime.date.strftime(datetime.date.today(),'%Y-%m-%d')
    ct.run(data_date = today)


    # 打开数据类文件追加当天数据类数据
    data = {'str_date': today}
    data = cd.run(data = data)

    # 打开标签文件追加新一天的上证高低幅度数据
    data = ci.run(data = data)
    #print(data)

    # 生成一行数据的df
    data_url_addr = '../data/store_digital.csv'
    today_data_df = pd.DataFrame.from_dict(data)
    #print(today_data_df)
    if os.path.exists(data_url_addr):
        target_data = pd.read_csv(data_url_addr, encoding = 'utf-8', index_col = 0)
        target_data = target_data.append(today_data_df, ignore_index = True)
        target_data.drop_duplicates(inplace = True)
        target_data.to_csv(data_url_addr, encoding = 'utf-8')
    else:
        today_data_df.to_csv(data_url_addr, encoding = 'utf-8')
    return today_data_df

if __name__=='__main__':
    '''
        主程序入口
    '''
    app = wx.App()
    UIFrame(None, title = u'自动获得上证训练数据')
    app.MainLoop()
