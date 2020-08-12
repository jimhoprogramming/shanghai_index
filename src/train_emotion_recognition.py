# -*- coding: utf-8 -*-
# 中文文本感情识别的训练模块
import numpy as np 
import sqlite3
import jieba
import emotion_model
import pandas as pd
from mxnet import nd

pre_trained_vector_files_url = 'c://w2v.txt'
db_url = 'c://data//all.db'

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

# 实现词语转换成向量
def one_word_to_vec(dest_word, embeddings_index):
    return embeddings_index[dest_word]

# 把一句话以词的形式分开成一列表
def sentence_to_word_list(sentence):
    seg_list = jieba.lcut_for_search(sentence)  
    return seg_list



# 载入训练集



# 载入模型
def define_model():
    model = BiRNN(vocab = 100, embed_size = 200, num_hiddens = 2, num_layers = 2)

    opt = Adam(lr = 0.005, beta_1=0.9, beta_2=0.999, decay = 0.01)
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model

# 初始化参数

# 实施训练
def run_train(model):
    model.fit([Xoh, s0, c0], outputs, epochs=1, batch_size=100)
    return True

# 读取数据文件，返回文本数据x，y
def read_text_data(url):
    x = pd.read_csv(url, encoding = 'utf-8', index_col = 0)
    x = x['text'].tolist()
    y = np.random.random_integers(0,1,len(x))
    return x,y


# 截断或补全处理一句话
def preprocess_imdb(x, y):  # 本函数已保存在d2lzh包中方便以后使用
    max_l = 30  # 将每条评论通过截断或者补'<pad>'，使得长度变成500
    def pad(x):
        return x[:max_l] if len(x) > max_l else x + [u'空格'] * (max_l - len(x))

    tokenized_data = [one_word_to_vector(pad(sentence_to_word_list(one_line))) for one_line in x]
    features = nd.array(tokenized_data)
    labels = y
    return features, labels



if __name__ == '__main__':
    # test old load w2v way
##    embeddings_index = load_vec_to_memory()
##    dest_word = '上证指数'
##    vector = one_word_to_vec(dest_word = dest_word, embeddings_index = embeddings_index)
##    print(u'词语：{}的向量值是:{}'.format(dest_word, vector))
##    text_to_sql()
##    create_word_index()

    # test sql way w2v
##    words = sentence_to_word_list('今天上山打老虎。')
##    v_list = one_word_to_vector(words = words)
##    for v in v_list:
##        print(v.shape)
##       

    # test fill sentances to 500 word
    x, y = read_text_data(url = './store_text.csv')
    print(u'feture len:{}'.format(len(x)))
    a, b = preprocess_imdb(x, y)
    print(u'regured x shape :{}.y shape:{}'.format(a.shape,b.shape))
