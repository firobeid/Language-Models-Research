import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, GRU, Embedding, Bidirectional, TimeDistributed, BatchNormalization, Flatten
import numpy as np
import psutil
# Prepare News headlines
def clean_text(df, column):
    import re 
    #("".join(headline)).strip()
    headline = []
    for i in df[column].apply(lambda x: '<s>'+x+'<\s>'):
        headline.append(i)
    return headline

# Encode to integers by using ascii 128
def encode2bytes(text):
    #text = tf.strings.unicode_split(text, 'UTF-8').to_list()
    final_list = []
    for sent in text:
        temp_list = []
        for char in sent:
            if ord(char) < 128 :
                temp_list.append(ord(char))
        final_list.append(temp_list)
    return final_list

#Tokenizer
def tokenize():
    import json
    with open('../CharModelDev/CharModel-v2/Tokenizer.json', encoding='utf-8') as f:
        data = json.load(f)
        tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(data)
    with open('../CharModelDev/CharModel-v2/index2char.json', encoding='utf-8') as f:
        index2char = json.load(f)
    char2index = dict((int(v),int(k)) for k,v in index2char.items())
    tokenizer.word_index = char2index
    return tokenizer

#get sequences of equal length to ensure <\s is at the end
def extract_end(char_seq, seq_len):
    if len(char_seq) > seq_len:
        char_seq = char_seq[:seq_len] + "..." + char_seq[-seq_len:]
    return char_seq

def memory()->str:
    return print('used: {}% free: {:.2f}GB'.format(psutil.virtual_memory().percent, float(psutil.virtual_memory().free)/1024**3))#@ 

def pct_change(df):
    return (df.close.shift(-1) - df.close)/ df.close

if __name__ == '__main__':
    clean_text(df, column)
    encode2bytes(text)
    tokenizer()
    memory()
    pct_change(df)