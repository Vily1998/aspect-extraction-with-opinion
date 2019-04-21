import numpy as np
from nltk import ngrams
import nltk
import string
import os
import random
import json

def replace(sent):
    nsent=''+sent[0]
    for i in (1,len(sent)-1):
        if sent[i]=='-' and sent[i-1].isalpha() and sent[i+1].isalpha() :
            nsent+=" - "
        else:
            nsent+=sent[i]

    return nsent



def read_data(path, opi_path):
    """
    construct dataset with aspect tags and opinion tags
    :param path: path of data file
    :param opi_path: path of data file
    :return:
    """
    # load opinion annotations


    with open('../data/prep_data/word_idx.json') as f:
        word_idx=json.load(f)

    #print(word_idx['keeps'])


    opinions = []
    with open(opi_path) as fp:
        for line in fp:
            opi_record = {}
            items = line.strip().split(', ')
            #print(items)
            for item in items:
                eles = item.split()
                polarity = eles[-1]
                word = ' '.join(eles[:-1])
                opi_record[word] = polarity
            opinions.append(opi_record)
    #print(opinions)
    dataset = []
    idx = 0
    j=0
    fp = open(path, 'r', encoding='utf-8')
    for line in fp:
        record = {}
        flag = 0
        opi_flag = 0
        opi_record = opinions[idx]
        sent, tag_string = line.strip().split("####")
        record['sentence'] = sent
        tag_sequence = tag_string.split(' ')
        words, tags, opi_tags = [], [], []

        asp_record = {}
        for item in tag_sequence:
            #print("********")
            eles = item.split('=')
            #print(eles[0])
            tag = eles[-1]

            asp_tokens=eles[0].replace('-',' - ')
            asp_tokens=nltk.word_tokenize(asp_tokens)

            for asp_token in asp_tokens:
                asp_record[asp_token] = tag
        #print(idx)
        #print(asp_record)


        sent=sent.replace('-',' - ')
        #print(sent)
        tokens = nltk.word_tokenize(sent)
        j+=1
        #print(j)
        #print(tokens)
        for token in tokens:
            if token in word_idx:
                words.append(word_idx[token])
            else:
                words.append(0)

            if token in opi_record:
                if opi_flag == 0:
                    opi_tags.append(1)
                else:
                    opi_tags.append(2)
                opi_flag = 1
            else:
                opi_tags.append(0)
                opi_flag = 0

            if token in asp_record:
                if asp_record[token]=='T':
                    if flag == 0:
                        tags.append(1)
                    else:
                        tags.append(2)
                    flag = 1
                else:
                    tags.append(0)
                    flag = 0
            else:
                tags.append(0)
                flag = 0


        '''
        for item in tag_sequence:
            eles = item.split('=')
            #print(eles)
            if len(eles) == 2:
                word, tag = eles
            else:
                n_ele = len(eles)
                tag = eles[-1]

                word = ''
                for k in range(n_ele):
                    ele = eles[k]
                    if ele == '' and k == 0:
                        continue
                    elif ele == '':
                        word += '='
                    else:
                        word += ele
            #words.append(word.lower())
        
            if word not in string.punctuation:
                words.append(word.lower())
            else:
                words.append('PUNCT')
            

            if word in word_idx:
                words.append(word_idx[word])
            else:
                words.append(0)
            #tags.append(tag)
        
            if tag == 'T':
                if flag==0:
                    tags.append(1)
                else:
                    tags.append(2)
                flag=1
            else:
                tags.append(0)
                flag=0
            # opinion tagging schema: OT
          
            if word in opi_record:
                if opi_flag == 0:
                    opi_tags.append(1)
                else:
                    opi_tags.append(2)
                opi_flag = 1
            else:
                opi_tags.append(0)
                opi_flag = 0
            '''
        while len(words)<83:
            words.append(0)
        while len(tags)<83:
            tags.append(0)
        while len(opi_tags)<83:
            opi_tags.append(0)
        record['sent'] = np.array(words)
        # origin aspect tags
        record['aspect_tags'] = np.array(tags)
        record['opinion_tags'] = np.array(opi_tags)

        dataset.append(record)
        idx += 1
    #print(type(data['opinion_tags']))
    #z=dataset[1]
    #print(z['sent'])
    sentences,aspect_tags,opinion_tags=[],[],[]
    for data in dataset:
        sentences.append(data['sent'])
        aspect_tags.append(data['aspect_tags'])
        opinion_tags.append(data['opinion_tags'])
    #print(type(opinion_tags[1][2]))
    #print(type(opinion_tags[1][2]))


    ae_data = np.load("../data/prep_data/restaurant.npz")
    X = ae_data['train_X']
    y = ae_data['train_y']

    zero= np.zeros((1, 83),dtype=np.int32)
    #print(type(zero[0][2]))
    new_opinion_tags=[]

    flag=0
    for i in range(0, 2000):
        flag=0
        for j in range(0, 2000):
            if (X[i] == sentences[j]).all():  # and (y[i]==ny[j]).all():
                # print(i,"match",j)
                new_opinion_tags.append(opinion_tags[j])
                flag=1
                break;
        if flag==0:
            new_opinion_tags.append(zero[0])

    print(type(new_opinion_tags[1][1]))

    for i in range(0,5):
        print(i)
        print(X[i])
        print(y[i])
        print(new_opinion_tags[i])

    np.savez('../data/prep_data/restaurant_data.npz', sentences=X, aspect_tags=y, opinion_tags=new_opinion_tags)



    print("N opinion:", len(new_opinion_tags))
    print("N dataset:", len(dataset))
    assert len(opinions) == len(dataset)
    return dataset

if __name__ == "__main__":

    # dataset for the task of aspect term extraction
    train_path = '../data/prep_data/restaurant_train.txt'
    #test_path = './dataset/%s_test.txt' % ds_name

    # dataset for the task of opinion word detection, we do not use gold standard labels
    # but distant supervision from existing opinion lexicon
    train_opi_path = '../data/prep_data/restaurant_train_opi.txt'
    #test_opi_path = './dataset/%s_test_opi_ds.txt' % ds_name

    train_set = read_data(train_path, train_opi_path)