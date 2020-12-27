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
    weight_url = '//home//jim//shanghai_index//data//weights.params'
    # 提取已有参数
    if os.path.exists(weight_url):
        print(u'已含有旧权重文件，正在载入继续训练并更新')
        model.load_parameters(weight_url, allow_missing = True, ignore_extra = True)
    return model

def predict(net, date):
    s_t_d_obj = create_dataset.short_time_dataset([create_dataset.train_data_url_txt, create_dataset.train_data_url_dig])
    x1, x2, y = s_t_d_obj.get_one_x_by_date(date)
    x1 = nd.expand_dims(x1, axis = 0)
    x2 = nd.expand_dims(x2, axis = 0)
    print(x1.shape)
    print(x2.shape)
    print(y)
    with autograd.predict_mode():
        autograd.set_training(False)
        y_hats = net(x1, x2)
    print(y_hats)

if __name__ == '__main__':
    net = define_model()
    predict(net = net, date = '2020-12-26')

