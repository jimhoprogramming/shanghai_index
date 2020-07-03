# -*- coding: utf-8 -*-
# 中文文本感情识别的训练模块
import numpy as np 


pre_trained_vector_files_url = '../data/sgns.target.word-ngram.1-2.dynwin5.thr10.neg5.dim300.iter5'



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


# 实现词语转换成向量
def one_word_to_vec(dest_word, embeddings_index):
    return embeddings_index[dest_word]


# 载入训练集



# 载入模型



# 初始化参数




# 实施训练



if __name__ == '__main__':
    embeddings_index = load_vec_to_memory()
    dest_word = '上证指数'
    vector = one_word_to_vec(dest_word = dest_word, embeddings_index = embeddings_index)
    print(u'词语：{}的向量值是:{}'.format(dest_word, vector))




