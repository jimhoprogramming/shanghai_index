# -*- coding: utf-8 -*-
from mix_model import mix_net
import create_dataset
import os
from mxnet import autograd, nd

# 载入模型
def define_model():
    model = mix_net(vocab = 4000,
                    embed_size = 300,
                    num_hiddens = 200,
                    num_layers = 2,
                    dense_layers = 10)
    #weight_url = '//home//jim//shanghai_index//data//weights.params'
    weight_url = '..//data//weights.params'
    # 提取已有参数
    if os.path.exists(weight_url):
        print(u'已含有旧权重文件，正在载入继续训练并更新')
        model.load_parameters(weight_url, allow_missing = True, ignore_extra = True)
    return model

def predict(net, date):
    s_t_d_obj = create_dataset.short_time_dataset([create_dataset.train_data_url_txt, create_dataset.train_data_url_dig])
    x1, x2, y = s_t_d_obj.get_ndate_data(date, 4)
    #print(x1.shape)
    #print(x2.shape)
    #print(y)
    with autograd.predict_mode():
        y_hats = net(x1, x2)
    print(y_hats)
    y_class = nd.argmax(y_hats, axis = 1)
    print(y_class)
    print(u'预测{}的次日上证指数最低位置将会{}'.format(date,s_t_d_obj.y_class_to_value(y_class[0].asscalar())))
if __name__ == '__main__':
    net = define_model()
    predict(net = net, date = '2021-03-15')

