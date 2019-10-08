
#import dependencies
import pandas as pd
import numpy as np
import nltk
import csv
from ast import literal_eval

from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')
import re as regex

colnames = [3, 2, 1]

ASTAG_LIST = pd.read_csv('ASTAG_RATINGS_2018.csv', skip_blank_lines=True).fillna('')
df = ASTAG_LIST[['Importance','Ingredient']]
ASTAG_LIST = df.pivot(columns='Importance', values='Ingredient').fillna('')
#ASTAG_LIST.columns = colnames

ab_list = pd.read_csv('reg_char_dist.csv', skip_blank_lines=True).fillna('')

ab_list = ab_list[['re_matched','Item Label', 'Medication', 'Ingredient','Drug Class']]

ab_list['Item Label'] = ab_list.loc[:,'Item Label'].apply(lambda x: literal_eval(x))
ab_list['Medication'] = ab_list.loc[:,'Medication'].apply(lambda x: literal_eval(x))
ab_list['Ingredient'] = ab_list.loc[:,'Ingredient'].apply(lambda x: literal_eval(x))
ab_list['Drug Class'] = ab_list.loc[:,'Drug Class'].apply(lambda x: literal_eval(x))


ASTAG_dict = {}
#
#for i in colnames:
#     ASTAG_LIST[i] = ASTAG_LIST[i].str.lower()
#     for x in ASTAG_LIST[i]:
#         ASTAG_dict[x] = i
#
ASTAG_cat = []
class_1 = ['amoxicillin', 'amoxycillin']
class_3 = ['ticaricillin']

        
for re, found_ing in zip(ab_list.re_matched, ab_list.Ingredient):
    
    
    done = 0
    
    if re == 0:
        ASTAG_cat.append(0)
        continue

    
        
    for i in colnames:
        if done == 1:
            break
        for med_line in ASTAG_LIST[i].str.lower():
            if med_line == []:
                continue
            med_line = regex.sub(r'\W', ' ', med_line)
            med_line = word_tokenize(med_line)
            if done == 1:
                break
            elif found_ing == []:
        
                ASTAG_cat.append(0)
                done = 1
                break
            
            if len(found_ing) == 1 and found_ing[0] in class_1:
                ASTAG_cat.append(1)
                done = 1
                break

            
            
#            if med_line[0] == 'piperacillin':
#                print('found')
            elif (found_ing[0] in med_line) and (found_ing[-1] in med_line):

                
#                print(med_line, ' ',found_ing, ' ', i)
                ASTAG_cat.append(i)
                done = 1
                break

    if done == 0:
        ASTAG_cat.append(0)

ASTAG_cat = np.asarray(ASTAG_cat)
ab_list['ASTAG_RATING'] = ASTAG_cat

colnames = list(ab_list.columns.values)

for i in colnames:
    if ab_list[i].dtype == list:
        ab_list[i] = ab_list[i].apply(' '.join)

ITEM_LIST = pd.read_csv('is_ab.csv')
ab_list['Item Label'] = ITEM_LIST['Item Name']

#
#debugging false negatives
#df_debug = ab_list.loc[(ab_list['re_matched'] == 1)]
#df_debug = df_debug.loc[(ab_list['ASTAG_RATING'] == 0)]

#Save output

ab_list.to_csv('ASTAG_rated_is_ab.csv', index=False)

