# -* - coding: UTF-8 -* -
import os
import configparser
 
CONFIG_FILE = "Config.cfg"
if __name__ == "__main__":
 
    conf = configparser.ConfigParser()
    cfgfile = open(CONFIG_FILE,'w')
    
    # 第一个参数是段名，第二个参数是选项名，第三个参数是选项对应的值
    conf.add_section('Text_Feature') # 在配置文件中增加一个段
    conf.set('Text_Feature', 'Feature1', 'goverment') 
    conf.set('Text_Feature', 'Feature2', 'netmessage')
    conf.set('Text_Feature', 'Feature3', 'perf_report')
    conf.set('Text_Feature', 'Feature4', 'inte_situation')
    conf.set('Text_Feature', 'Feature5', 'mili_situation')
    
    conf.add_section('Data_Feature') # 在配置文件中增加一个段
    conf.set('Data_Feature', 'Feature1', 'amer_stock')
    conf.set('Data_Feature', 'Feature2', 'loca_stock')
    conf.set('Data_Feature', 'Feature3', 'euro_stock')
    conf.set('Data_Feature', 'Feature4', 'japa_stock')
    conf.set('Data_Feature', 'Feature5', 'hk_stock')
    conf.set('Data_Feature', 'Feature6', 'gold')
    conf.set('Data_Feature', 'Feature7', 'oil')
    conf.set('Data_Feature', 'Feature8', 'loca_cpi')
    conf.set('Data_Feature', 'Feature9', 'loca_gdp')
    conf.set('Data_Feature', 'Feature10', 'soci_financing')
    conf.set('Data_Feature', 'Feature11', 'bank_rate')
    
    conf.add_section('Index_Feature') # 在配置文件中增加一个段
    conf.set('Index_Feature', 'Feature1', 'index_close')
    conf.set('Index_Feature', 'Feature2', 'index_amp')
    conf.set('Index_Feature', 'Feature3', 'index_increase')
    conf.set('Index_Feature', 'Feature4', 'index_updown')
    conf.set('Index_Feature', 'Feature5', 'index_amount')
    conf.set('Index_Feature', 'Feature6', 'index_count')
    conf.set('Index_Feature', 'Feature7', 'index_hight')
    conf.set('Index_Feature', 'Feature8', 'index_low')
    conf.set('Index_Feature', 'Feature9', 'index_quantity_ratio')
    conf.set('Index_Feature', 'Feature10', 'index_turnover_rate')    
    
 
    # 将conf对象中的数据写入到文件中
    conf.write(cfgfile)
    cfgfile.close()
