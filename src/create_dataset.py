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
#import d2l
import tushare as ts


##pre_trained_vector_files_url = 'c://w2v.txt''
pre_trained_vector_files_url = '//home//jim/shanghai_index//data//w2v.txt'
##db_url = 'c://data//all.db'
db_url = '//home//jim//shanghai_index//data//all.db'
##train_data_url = 'd://github_project//shanghai_index//data//simplifyweibo_4_moods.csv'
##train_data_url = '//home//jim//shanghai_index//data//simplifyweibo_4_moods.csv'
##train_data_url = 'd://github_project//shanghai_index//src//train_set.csv'
train_data_url_txt = '//home//jim//shanghai_index//data//store_text.csv'
train_data_url_dig = '//home//jim//shanghai_index//data//store_digital.csv'
##train_data_url_txt = 'd://github_project//shanghai_index//data//store_text.csv'
##train_data_url_dig = 'd://github_project//shanghai_index//data//store_digital.csv'




def load_vec_to_memory():
    '''
        提取中文向量数据矩阵: 所有关键词提取300d向量到内存变量暂存
    '''
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

def text_to_sql():
    '''
        文本数据导入成数据库文件
    '''
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

def create_word_index():
    '''
        建立词向量表的索引加速查询速度 
    '''
    sql_db = sqlite3.connect(db_url)
    cur = sql_db.cursor()
    cur.execute('create index if not exists word_idx on w2v(word)')
    sql_db.commit()
    cur.close()
    return True

def one_word_to_vector(words):
    '''
        在数据库查指定词语的向量
    '''
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

def drop_char(word):
    '''
        去除sql3不接受的字符
    '''
    a = re.findall(r'\w*', word, re.S) 
    return a[0]


def one_word_to_vec(dest_word, embeddings_index):
    '''
        实现词语转换成向量
    '''
    return embeddings_index[dest_word]

def sentence_to_word_list(sentence):
    '''
        把一句话以词的形式分开成一列表
    '''
    seg_list = jieba.lcut_for_search(sentence)
    seg_list = [drop_char(word = w) for w in seg_list]
    #print(seg_list)
    return seg_list

def read_text_data(url):
    '''
        读取数据文件，返回文本数据x，y
    '''
    data = pd.read_csv(url, encoding = 'utf-8', index_col = 0)
    data.reindex([i for i in range(data.shape[0])], fill_value = '4')
    #x = x['text'].tolist()
    x = data['review'].tolist()
    #y = np.random.random_integers(0,1,len(x))
    y = data['label'].tolist()
    return x,y


def preprocess_imdb(x, y):  # 本函数已保存在d2lzh包中方便以后使用
    '''
    # 截断或补全处理一句话
    '''
    max_l = 4000  # 将每条评论通过截断或者补'<pad>'，使得长度变成500
    def pad(x):
        return x[:max_l] if len(x) > max_l else x + [u'空格'] * (max_l - len(x))

    tokenized_data = one_word_to_vector(pad(sentence_to_word_list(x)))
    features = nd.array(tokenized_data)
    labels = nd.array([y])
    return features, labels

def define_model():
    '''
        载入模型
    '''
    model = BiRNN(vocab = 100, embed_size = 300, num_hiddens = 200, num_layers = 2)
    lr, num_epochs = 0.001, 125
    model.initialize(init.Xavier(), ctx=cpu())
    trainer = gluon.Trainer(model.collect_params(), 'adam', {'learning_rate':lr})
    loss = gloss.SoftmaxCrossEntropyLoss(sparse_label = True)
    return model, trainer, loss

# 初始化参数


def run_train(model, data, trainer, loss, num_epochs, ctx):
    '''
        实施训练
    '''
    test_iter = data
    d2l.train(data, test_iter, model, loss, trainer, ctx, num_epochs)
    return model
    #

class short_time_dataset(gdata.Dataset):
    '''
        自建一个按次提取的数据集
    '''
    def __init__(self, url):
        super(short_time_dataset, self).__init__()
        self.date_list, self.data_text_dict, self.data_digital = self.__open_file(url = url)
    def __len__(self):
        m = len(self.date_list)
        print('data numbers = {}'.format(m))
        return m
    def __getitem__(self, idx):
        #print('idx = {}'.format(idx))
        index_value = self.date_list[idx]
        x_text = self.data_text_dict[index_value]
        print(u'text lenght : {}'.format(len(x_text)))
        x_digital_series = self.data_digital.loc[index_value]
        x_digital = x_digital_series.tolist()
        x_digital = nd.array(x_digital[:-1])
        y = x_digital_series['y_value']
        #x_digital = nd.random.uniform(shape=(21,))
        #y = nd.random.uniform(0,1).asscalar()
        #y = np.random.choice([0,1,2,3,4,5,6,7,8,9],1)[0]
        y = self.__split_y_segment(y)
        #print(x_text)
        #print(x_digital)
        #print(y)
        x_text, y = preprocess_imdb(x_text, y)
        #print(x_text.shape)
        #print(y.shape)
        #print(y)
        #y = nd.one_hot(y, 10)
        #y = nd.squeeze(y)
        return x_text, x_digital, y
    
    def __split_y_segment(self, y):
        '''
            把y值变成分类问题
        '''
        #print(y)
        rel = 0
        if (y > 0):
            rel = 0
        elif (0 > y >= -0.001):
            rel = 1
        elif (-0.001 > y >= -0.005):
            rel = 2
        elif (-0.005 > y > -0.01):
            rel = 3
        elif (-.01 >= y ):
            rel = 4
        #print(rel)
        return int(rel)


    def __open_file(self, url):
        '''
            提取文件；按日期合并text的行；按日期计算下一天的y；
        '''
        try :
            data_text = pd.read_csv(url[0], encoding = 'utf-8', index_col = 0)
        except:
            try:
                data_text = pd.read_csv(url[0], encoding = 'gbk',index_col = 0)
            except:
                data_text = pd.read_csv(url[0], encoding = 'gb2312',index_col = 0)
        data_digital = pd.read_csv(url[1],index_col = 0)
        
        print(data_text.shape)
        data_text.drop_duplicates(['text'], inplace = True)
        print(data_text.shape)
        grouped = data_text.groupby(['date'])
        data_text_dict = {}
        for name, group in grouped:
            temp_data = ';'.join(group['text'].tolist())
            data_text_dict[name] = temp_data
        # 按日期先后排序好数据计算所有需要的y值
        data_digital = data_digital.set_index(['str_date'])
        data_digital = data_digital.sort_index(ascending = True)
        y_next = (data_digital['index_low'] - data_digital['index_before']) / data_digital['index_before']
        y_next = y_next.tolist()[1:]
        y_next.append(0)
        #print(y_next)
        data_digital['y_value'] = y_next
        #print(data_digital)
        # 生成有效日期列表，清除周六日数据或非交易日数据行
        date_list = []
        for date in data_digital.index:
            if CheckTradeDateTrue(date):
                date_list.append(date)
        
        return date_list, data_text_dict, data_digital

    def get_one_x_by_date(self, date):
        x_text = self.data_text_dict[date]
        print(u'text lenght : {}'.format(len(x_text)))
        x_digital_series = self.data_digital.loc[date]
        x_digital = x_digital_series.tolist()
        x_digital = nd.array(x_digital[:-1])
        y = x_digital_series['y_value']
        x_text, y = preprocess_imdb(x_text, y)
        return x_text, x_digital, y 
        
        

def CheckTradeDateTrue(InputDate=None):
    '''
        功能：检查输入的日期是否交易日，
        输入：'2017-10-11'格式日期
        输出：是或否
    '''
    Rel = True
    if InputDate is not None:
        TempDate=InputDate
        print(u'被判断的日期是:'+TempDate)
        #检查那天上证指数是否空            
        KData=ts.get_k_data('000001',start=TempDate,end=TempDate)
        if KData is None:
            Rel = False
        elif len(KData)<1:
            Rel = False
    if Rel:
        print(u'是交易日')
    else:
        print(u'不是交易日')
    return Rel


    
    

def create_iter(batch_size = 2):
    '''
        建立迭代器
        为缓解速度问题打散数据在先，提取词向量在后
    '''
    
    s_t_d_obj = short_time_dataset([train_data_url_txt, train_data_url_dig])
    train_iter = gdata.DataLoader(s_t_d_obj, batch_size, shuffle = True, last_batch = 'rollover')
    return train_iter



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
       

    # test fill sentances to 500 word
##    x, y = read_text_data(url = './store_text.csv')
##    print(u'feture len:{}'.format(len(x)))
##    a, b = preprocess_imdb(x, y)
##    print(u'regured x shape :{}.y shape:{}'.format(a.shape,b.shape))

    # test iter
    iteror = create_iter()
    for x_text, x_digital, y in iteror:
        print('X_text = {}, X_digital = {}, y = {}'.format(x_text.shape, x_digital.shape, y.shape))
        #break

    # test model
##    iteror = create_iter()
##    model, trainer, loss = define_model()
##    run_train(model = model, data = iteror, trainer = trainer, loss = loss, num_epochs = 1000, ctx = cpu())

    # test open_file
##    date_list, date_t, data_d = open_file([train_data_url_txt, train_data_url_dig])
##    print(date_list)
