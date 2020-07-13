# -*- coding: utf-8 -*-
# Shang_Hai Index User Interface conctrl model
# 异步启动线程自由获取指定网站的信息数据。存到cvs文件中。
# 每次完成界面有绿灯表示。可人工控制关停。
#


import wx
from wx.lib.agw import peakmeter
import random
from collection_txt import *

class UIFrame(wx.Frame):
    def __init__(self, parent, title):
        super(UIFrame, self).__init__(parent, title = title, size = (512,384), style = wx.DEFAULT_FRAME_STYLE)
        panel = wx.Panel(parent = self, id = 0, pos = wx.DefaultPosition, size = (510,382))
        # 定义一个峰值计控制器
        self.netbugger_text_peak_ctrl = peakmeter.PeakMeterCtrl(parent = panel, id = -1, pos = wx.DefaultPosition, size = (250, 200), style = 0, agwStyle = 0x1)
        self.netbugger_text_peak_ctrl.SetMeterBands(numBands = 5, ledBands = 20)
        self.netbugger_text_peak_ctrl.ShowGrid(True)
        # 定义一个时钟控制显示频率
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        wx.CallLater(2000/2, self.Start)
        # 更新尺寸
        self.SetAutoLayout(1)
        # 显示界面
        self.Centre()
        self.Show()
        
    def Start(self):
        ''' Starts the PeakMeterCtrl. '''

        self.timer.Start(60*1000)            # 2 fps
        self.netbugger_text_peak_ctrl.Start(1000/18)        # 18 fps
        
    def OnTimer(self, event):
        '''
        Handles the ``wx.EVT_TIMER`` event for :class:`~peakmeter.PeakMeterCtrl`.

        :param `event`: a `wx.TimerEvent` event to be processed.
        '''
        # Generate 15 random number and set them as data for the meter
               
        #nElements = 5
        arrayData = []
        threads = []
        '''
        for i in range(nElements):
            print(i)
            nRandom = random.randint(0, 100)
            arrayData.append(nRandom)
        '''
        urls_list = get_urls()
        nElements = len(urls_list)

        for url in urls_list:
            #print(urls_list)
            # 加入异步线程调用每个网站一个爬虫爬数据
            #data_len = write_to_file(data_list = x , file_name = './store_text.csv', mode = mode)
            thread_obj = bugger_thread(target = netbugger, args=(url,'append'))
            thread_obj.start()
            threads.append(thread_obj)
        for obj in threads:
            obj.join()
            arrayData.append(obj.get_result())
        
            
        self.netbugger_text_peak_ctrl.SetData(arrayData, 0, nElements)
    
        

if __name__=='__main__':
    '''
        主程序入口
    '''
    app = wx.App()
    UIFrame(None, title = u'上证指数预警控制界面')
    app.MainLoop()
