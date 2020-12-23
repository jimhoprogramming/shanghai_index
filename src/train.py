# -*- coding: utf-8 -*-
# 训练模块
import numpy as np 
from mix_model import mix_net 
import pandas as pd
import mxnet as mx
from mxnet import nd, gluon, init, cpu, autograd
from mxnet.gluon import data as gdata, loss as gloss 
import re
import d2l
from create_dataset import create_iter
import time
        

# 载入模型
def define_model():
    model = mix_net(vocab = 4000,
                    embed_size = 300,
                    num_hiddens = 200,
                    num_layers = 2,
                    dense_layers = 100)
    lr = 0.001
    model.initialize(init.Xavier(), ctx=cpu())
    trainer = gluon.Trainer(model.collect_params(), 'adam', {'learning_rate':lr})
##    loss = gloss.SoftmaxCrossEntropyLoss(sparse_label = True)
    loss = gloss.L2Loss()
    return model, trainer, loss

# 初始化参数

# 实施训练
def run_train(model, data, trainer, loss, num_epochs, ctx):
    test_iter = data
    train(data, test_iter, model, loss, trainer, ctx, num_epochs)
    return model
    #


def train(train_iter, test_iter, net, loss, trainer, ctx, num_epochs):
    """Train and evaluate a model."""
    print('training on', ctx)
    if isinstance(ctx, mx.Context):
        ctx = [ctx]
    for epoch in range(num_epochs):
        train_loss, train_acc, train_step, start = 0.0, 0.0, 0, time.time()
        for x1, x2, y  in train_iter:
            batch_size = x1.shape[0]
            with autograd.record():
                y_hats = net(x1, x2)
                print('y_hat = {}'.format(y_hats))
                print('y = {}'.format(y))
                ls = loss(y_hats, y)
                #print(ls)
                ls.backward()
            trainer.step(batch_size)
            train_loss += np.mean(ls.asnumpy())
            train_acc += acc(y_hats, y)
            train_step += 1
        
        print('epoch {}, loss {}, train acc {}, time {} sec'.format(epoch + 1,
                                                                    train_loss/train_step,
                                                                    train_acc/train_step,
                                                                    time.time() - start))

def acc(output, label):
    # output: (batch, num_output) float32 ndarray
    # label: (batch, label) float32 ndarray
    return (output == label).mean().asscalar()  

if __name__ == '__main__':
    # test model
    iteror = create_iter(batch_size = 1)
    model, trainer, loss = define_model()
    print(model)
    run_train(model = model,
              data = iteror,
              trainer = trainer,
              loss = loss,
              num_epochs = 32,
              ctx = cpu())
