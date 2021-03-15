# -*- coding: utf-8 -*-
# 训练模块
import numpy as np 
from mix_model import mix_net 
import pandas as pd
import mxnet as mx
from mxnet import nd, gluon, init, cpu, autograd
from mxnet.gluon import data as gdata, loss as gloss
from mxnet import lr_scheduler
import re
import d2l
from create_dataset import create_iter
import time
import os
from mxboard import *
        

# 载入模型
def define_model():
    model = mix_net(vocab = 4000,
                    embed_size = 300,
                    num_hiddens = 200,
                    num_layers = 2,
                    dense_layers = 10)
    # 初始化参数
    lr = 0.0003
    lr_sch = lr_scheduler.FactorScheduler(step=50, factor=0.9)
    optimizer_params={'learning_rate': lr, 'lr_scheduler': lr_sch}
    model.initialize(init.Xavier())
##    trainer = gluon.Trainer(params = model.collect_params(), optimizer = 'sgd', optimizer_params = {'learning_rate':lr})
    trainer = gluon.Trainer(params = model.collect_params(), optimizer = 'adam', optimizer_params = optimizer_params)
    loss = gloss.SoftmaxCrossEntropyLoss(sparse_label = True)
##    loss = gloss.L2Loss()
##    loss = gloss.SigmoidBinaryCrossEntropyLoss()
    accuracy = mx.metric.Accuracy()
    return model, trainer, loss



# 实施训练
def run_train(model, data, trainer, loss, num_epochs, ctx):
    test_iter = data
    train(data, test_iter, model, loss, trainer, ctx, num_epochs)
    return model
    #


def train(train_iter, test_iter, net, loss, trainer, ctx, num_epochs):
    """Train and evaluate a model."""
    # 加入学习曲线显示
    weight_url = '//home//jim//shanghai_index//data//weights.params'
    logdir_url = '//home//jim//shanghai_index//log'
    sw = SummaryWriter(logdir = logdir_url, flush_secs=10)
    # 提取已有参数
    if os.path.exists(weight_url):
        print(u'已含有旧权重文件，正在载入继续训练并更新')
        net.load_parameters(weight_url, allow_missing = True, ignore_extra = True)
    # 训练
    for epoch in range(num_epochs):
        train_loss, train_acc, train_step, start = 0.0, 0.0, 0, time.time()
        for x1, x2, y  in train_iter:
            batch_size = x1.shape[0]
            with autograd.record():
                y_hats = net(x1, x2)
                print('y_hat = {}'.format(y_hats))
                print('y = {}'.format(y))
                ls = loss(y_hats, y)
                print('loss:{}'.format(ls))
            ls.backward()
            trainer.step(batch_size)
            train_loss += np.mean(ls.asnumpy())
            train_acc += acc(y_hats, y)
            train_step += 1
        
        print('epoch {}, loss {}, train acc {}, time {} sec'.format(epoch + 1,
                                                                    train_loss/train_step,
                                                                    train_acc/train_step,
                                                                    time.time() - start))
        # 向tensorboard填数据
        sw.add_scalar(tag = 'Loss_and_acc', \
                               value = {'train_loss': train_loss/train_step, 'train_acc': train_acc/train_step}, \
                               global_step = epoch)
        # 加入某个层权重分布变化等高图
        grads = [i.grad() for i in net.collect_params('.*weight|.*bias').values()]
        param_names = [name for name in net.collect_params('.*weight|.*bias').keys()]
        assert len(grads) == len(param_names)
        # logging the gradients of parameters for checking convergence
        for i, name in enumerate(param_names):
            sw.add_histogram(tag = name, values = grads[i], global_step = epoch, bins = 20)

        # 加入保存参数
        net.save_parameters(weight_url)
        
        
def acc(output, label):
    # output: (batch, num_output) float32 ndarray
    # label: (batch, label) float32 ndarray
    return (nd.argmax(output) == label).mean().asscalar()


if __name__ == '__main__':
    # test model
    iteror = create_iter(batch_size = 4)
    model, trainer, loss = define_model()
    print(model)
    run_train(model = model,
              data = iteror,
              trainer = trainer,
              loss = loss,
              num_epochs = 100,
              ctx = cpu())
