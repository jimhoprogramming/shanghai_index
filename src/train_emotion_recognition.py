# -*- coding: utf-8 -*-
# 中文文本感情识别的训练模块
import numpy as np 
import sqlite3
import jieba
from emotion_model import BiRNN 
import pandas as pd
from mxnet import nd, gluon, init, cpu
from mxnet.gluon import data as gdata, loss as gloss 
import re
import d2l


##pre_trained_vector_files_url = 'c://w2v.txt''
pre_trained_vector_files_url = '//home//jim/shanghai_index//data//w2v.txt'
db_url = 'c://data//all.db'
##db_url = '//home//jim//shanghai_index//data//all.db'
##train_data_url = 'd://github_project//shanghai_index//data//simplifyweibo_4_moods.csv'
##train_data_url = '//home//jim//shanghai_index//data//simplifyweibo_4_moods.csv'
train_data_url = 'd://github_project//shanghai_index//src//train_set.csv'

# 提取中文向量数据矩阵: 所有关键词提取300d向量到内存变量暂存
def load_vec_to_memory():
    embeddings_index = {}
    f = open(pre_trained_vector_files_url, 'r', encoding = 'utf-8', error = 'ignore')
    i = 0
    for line in f:
        i += 1
        values = line.split()
        word = values[0]
        print(u'{}:{}'.format(i,word))
        embeddings_index[word] = np.asarray(values[1:], dtype='float32')
    f.close()
    return embeddings_index

# 文本数据导入成数据库文件
def text_to_sql():
    sql_db = sqlite3.connect(db_url)
    cur = sql_db.cursor()
    cur.execute('create table if not exists w2v(id integer primary key, word text, vectors text)')
    f = open(pre_trained_vector_files_url, 'r', encoding = 'utf-8', errors = 'ignore')
    i = 0
    for line in f:
        i += 1        
        values = line.split()
        word = values[0]
        print(u'{}:{}'.format(i,word))
        cur.execute('insert into w2v values(?,?,?)',(i, word, str(values[1:])))
        if i >= 506310:
            break
    cur.execute('create index if not exists word_idx on w2v(word)')
    sql_db.commit()
    cur.close()
    f.close()
    return True

# 建立词向量表的索引加速查询速度 
def create_word_index():
    sql_db = sqlite3.connect(db_url)
    cur = sql_db.cursor()
    cur.execute('create index if not exists word_idx on w2v(word)')
    sql_db.commit()
    cur.close()
    return True

# 在数据库查指定词语的向量
def one_word_to_vector(words):
    sql_db = sqlite3.connect(db_url)
    cur = sql_db.cursor()
    result = []
    for w in words:
        
        #print(w)
        cur.execute("select vectors from w2v where word='%s'"%(w))
        last_v = None
        for v in cur:
            last_v = np.asarray(eval(v[0]), dtype='float32')
        # no return then give unk
        if last_v is None:
            cur.execute("select vectors from w2v where word='%s'"%('空缺'))
            for v in cur:
                last_v = np.asarray(eval(v[0]), dtype='float32')
        result.append(last_v)        
    cur.close()
    sql_db.close()
    return result

# 去除sql3不接受的字符
def drop_char(word):
    a = re.findall(r'\w*', word, re.S) 
    return a[0]


# 实现词语转换成向量
def one_word_to_vec(dest_word, embeddings_index):
    return embeddings_index[dest_word]

# 把一句话以词的形式分开成一列表
def sentence_to_word_list(sentence):
    seg_list = jieba.lcut_for_search(sentence)
    seg_list = [drop_char(word = w) for w in seg_list]
    #print(seg_list)
    return seg_list

# 读取数据文件，返回文本数据x，y
def read_text_data(url):
    data = pd.read_csv(url, encoding = 'utf-8')
    #x = x['text'].tolist()
    x = data['review'].tolist()
    #y = np.random.random_integers(0,1,len(x))
    y = data['label'].tolist()
    return x,y


# 截断或补全处理一句话
def preprocess_imdb(x, y):  # 本函数已保存在d2lzh包中方便以后使用
    max_l = 100  # 将每条评论通过截断或者补'<pad>'，使得长度变成500
    def pad(x):
        return x[:max_l] if len(x) > max_l else x + [u'空格'] * (max_l - len(x))

    tokenized_data = one_word_to_vector(pad(sentence_to_word_list(x)))
    features = nd.array(tokenized_data)
    labels = nd.array([y])
    return features, labels


# 建立迭代器
def create_iter():
    # 为缓解速度问题打散数据在先，提取词向量在后
    batch_size = 32
    s_t_d_obj = short_time_dataset(train_data_url)
    train_iter = gdata.DataLoader(s_t_d_obj, batch_size, shuffle = True)
    return train_iter

# 自建一个按次提取的数据集
class short_time_dataset(gdata.Dataset):
    def __init__(self, url):
        super(short_time_dataset, self).__init__()
        self.data = pd.read_csv(url, encoding = 'utf-8')        
    def __len__(self):
        #print(self.data.shape[0])
        return self.data.shape[0]
    def __getitem__(self, idx):
        #print(idx)
        x = self.data.iloc[idx,1]
        y = self.data.iloc[idx,0]
        #print(x)
        #print(y)
        x, y = preprocess_imdb(x, y)
        #print(x.shape)
        #print(y.shape)
        #y = nd.one_hot(y,4)
        #y = nd.squeeze(y)
        return x, y
        

# 载入模型
def define_model():
    model = BiRNN(vocab = 100, embed_size = 300, num_hiddens = 200, num_layers = 2)
    lr, num_epochs = 0.01, 5
    model.initialize(init.Xavier(), ctx=cpu())
    trainer = gluon.Trainer(model.collect_params(), 'adam', {'learning_rate':lr})
    loss = gloss.SoftmaxCrossEntropyLoss()
    return model, trainer, loss

# 初始化参数

# 实施训练
def run_train(model, data, trainer, loss, num_epochs, ctx):
    test_iter = data
    d2l.train(data, test_iter, model, loss, trainer, ctx, num_epochs)
    return model
    #




if __name__ == '__main__':
    # test old load w2v way
##    embeddings_index = load_vec_to_memory()
##    dest_word = '上证指数'
##    vector = one_word_to_vec(dest_word = dest_word, embeddings_index = embeddings_index)
##    print(u'词语：{}的向量值是:{}'.format(dest_word, vector))

    # create sql data using sql to do
##    text_to_sql()
##    create_word_index()

    # test sql way w2v
##    words = sentence_to_word_list('今天上山打老虎。')
##    v_list = one_word_to_vector(words = words)
##    for v in v_list:
##        print(v.shape)
##       

    # test fill sentances to 500 word
##    x, y = read_text_data(url = './store_text.csv')
##    print(u'feture len:{}'.format(len(x)))
##    a, b = preprocess_imdb(x, y)
##    print(u'regured x shape :{}.y shape:{}'.format(a.shape,b.shape))

    # test iter
##    iteror = create_iter()
##    for x,y in iteror:
##        print('X', x.shape, 'y', y.shape)
##        break
##    '#batches:', len(iteror)

    # test model
    iteror = create_iter()
    model, trainer, loss = define_model()
    run_train(model = model, data = iteror, trainer = trainer, loss = loss, num_epochs = 5, ctx = cpu())
