# -*- coding: utf-8 -*-
# 训练模块
import numpy as np 
from mix_model import mix_net 
import pandas as pd
from mxnet import nd, gluon, init, cpu
from mxnet.gluon import data as gdata, loss as gloss 
import re
import d2l
        

# 载入模型
def define_model():
    model = mix_net(vocab = 100, embed_size = 300, num_hiddens = 200, num_layers = 2)
    lr, num_epochs = 0.01, 32
    model.initialize(init.Xavier(), ctx=cpu())
    trainer = gluon.Trainer(model.collect_params(), 'adam', {'learning_rate':lr})
    loss = gloss.SoftmaxCrossEntropyLoss(sparse_label = True)
    return model, trainer, loss

# 初始化参数

# 实施训练
def run_train(model, data, trainer, loss, num_epochs, ctx):
    test_iter = data
    d2l.train(data, test_iter, model, loss, trainer, ctx, num_epochs)
    return model
    #


if __name__ == '__main__':
    # test model
    iteror = create_iter()
    model, trainer, loss = define_model()
    run_train(model = model, data = iteror, trainer = trainer, loss = loss, num_epochs = 32, ctx = cpu())
