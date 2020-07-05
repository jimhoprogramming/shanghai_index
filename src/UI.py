# -*- coding: utf-8 -*-
# Shang_Hai Index User Interface conctrl model
# 异步启动线程自由获取指定网站的信息数据。存到cvs文件中。
# 每次完成界面有绿灯表示。可人工控制关停。
#


import wx
from wx.lib.agw import peakmeter

class UIFrame(wx.Frame):
    def __init__(self, parent, title):
        super(UIFrame, self).__init__(parent, title = title, size = (512,384), style = wx.DEFAULT_FRAME_STYLE)
        panel = wx.Panel(parent = self, id = 0, pos = wx.DefaultPosition, size = (510,382))
        # 定义一个峰值计控制器
        netbugger_text_peak_ctrl = peakmeter.PeakMeterCtrl(parent = panel, id = -1, pos = wx.DefaultPosition, size = (250, 200), style = 0, agwStyle = 0x1)
        netbugger_text_peak_ctrl.SetMeterBands(numBands = 10, ledBands = 30)
        netbugger_text_peak_ctrl.ShowGrid(True)
        # 更新尺寸
        self.SetAutoLayout(1)
        # 显示界面
        self.Centre()
        self.Show()

if __name__=='__main__':
    '''
        主程序入口
    '''
    app = wx.App()
    UIFrame(None, title = u'上证指数预警控制界面')
    app.MainLoop()
