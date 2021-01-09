# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd

def define_class():
    # 定义分类代表的个股
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


def get_stocks_k(class_dict,start_date):
    # 获取每个行业的龙头股指定时间段的k线值
    rel = {}
    for c in list(class_dict.keys()):
        rel[c] = []
        for s in class_dict[c]:
            #print(s)
            df = ts.get_k_data(s, start = start_date)
            rel[c].append(df)
    return rel


def get_percend(stocks_df):
    # 统计升高的幅度百分比
    rel = {}
    for c in list(stocks_df.keys()):
        rel[c] = []
        for s in stocks_df[c]:
            #print(s)
            percend = s.iloc[-1,3] - s.iloc[0,2]/s.iloc[0,2]
            rel[c].append(percend)
    rel = pd.DataFrame(rel)
    return rel
    


if __name__=='__main__':
    c = define_class()
    d = get_stocks_k(c, '2020-6-30')
    rel = get_percend(d)
    print(rel)
    print(rel.mean(0))





# 输出结果DF










