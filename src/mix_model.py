from mxnet import gluon, init, nd
from mxnet.gluon import nn, rnn 



class mix_net(nn.Block):
    def __init__(self, vocab, embed_size, num_hiddens, num_layers, dense_layers, **kwargs):
        super(mix_net, self).__init__(**kwargs)
        self.encoder = rnn.LSTM(num_hiddens, num_layers=num_layers, bidirectional=True, input_size=embed_size)
        self.decoder = nn.Dense(1, activation = 'relu')
        #self.bn = nn.BatchNorm(axis = 0, use_global_stats = True)
        self.bn = nn.LayerNorm(axis = 0)
        self.dnn = nn.HybridSequential()
        for i in nd.arange(int(dense_layers * 1/5)):
            self.dnn.add(nn.Dense(int(22 * 2), activation = 'relu'))
        for i in nd.arange(int(dense_layers * 1/5)):
            self.dnn.add(nn.Dense(int(22 * 4), activation = 'relu'))
        for i in nd.arange(int(dense_layers * 1/5)):
            self.dnn.add(nn.Dense(int(22 * 8), activation = 'relu'))
        for i in nd.arange(int(dense_layers * 1/5)):
            self.dnn.add(nn.Dense(int(22 * 2), activation = 'relu'))
        for i in nd.arange(int(dense_layers * 1/5)):
            self.dnn.add(nn.Dense(int(22 * 1), activation = 'relu'))
        self.out_dense = nn.Dense(5)

    def forward(self, inputs_text, inputs_digital):
        # inputs的形状是(批量大小, 词数)，因为LSTM需要将序列作为第一维，所以将输入转置后
        # 再提取词特征，输出形状为(词数, 批量大小, 词向量维度)
        #embeddings = self.embedding(inputs.T)
        embeddings = nd.transpose(inputs_text, axes = (1,0,2))
        # rnn.LSTM只传入输入embeddings，因此只返回最后一层的隐藏层在各时间步的隐藏状态。
        # outputs形状是(词数, 批量大小, 2 * 隐藏单元个数)
        outputs = self.encoder(embeddings)
        #print(outputs[0].shape)
        #print(outputs[1].shape)
        # 连结初始时间步和最终时间步的隐藏状态作为全连接层输入。它的形状为
        # (批量大小, 4 * 隐藏单元个数)。
        encoding = nd.concat(outputs[0], outputs[-1])
        #print(encoding.shape)
        outs = self.decoder(encoding)
        #print(outs.shape)
        x = nd.concat(inputs_digital, outs, dim = 1)
        x = self.bn(x)
        #print(x)
        x = self.dnn(x)
        y = self.out_dense(x)
        return y
