# -*- coding: utf-8 -*-
# 中文文本感情识别的训练模块
import numpy as np 
import sqlite3

pre_trained_vector_files_url = 'c://w2v.txt'
db_url = 'd://github_project//shanghai_index//data//all.db'

# 提取中文向量数据矩阵: 所有关键词提取300d向量到内存变量暂存
def load_vec_to_memory():
    embeddings_index = {}
    f = open(pre_trained_vector_files_url, 'r', encoding = 'utf-8')
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
    f = open(pre_trained_vector_files_url, 'r', encoding = 'utf-8')
    i = 0
    for line in f:
        i += 1
        values = line.split()
        word = values[0]
        #print(u'{}:{}'.format(i,word))
        cur.execute('insert into w2v values(?,?,?)',(i, word, str(values[1:])))
        if i >= 506310:
            break
    cur.execute('create index if not exists word_idx on w2v(word)')
    sql_db.commit()
    cur.close()
    f.close()
    return True
# create word index 
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
        print(w)
        cur.execute("select vectors from w2v where word='%s'"%(w))
        for v in cur:
##            print(v)
##            print(type(v))
            v = np.asarray(eval(v[0]), dtype='float32')
            result.append(v)
    cur.close()
    sql_db.close()
    return result

# 实现词语转换成向量
def one_word_to_vec(dest_word, embeddings_index):
    return embeddings_index[dest_word]


# 载入训练集



# 载入模型



# 初始化参数




# 实施训练



if __name__ == '__main__':
##    embeddings_index = load_vec_to_memory()
##    dest_word = '上证指数'
##    vector = one_word_to_vec(dest_word = dest_word, embeddings_index = embeddings_index)
##    print(u'词语：{}的向量值是:{}'.format(dest_word, vector))
##    text_to_sql()
##    create_word_index()
    v = one_word_to_vector(words = ["女排", "hi"])
    print(v)



