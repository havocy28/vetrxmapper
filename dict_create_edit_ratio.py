#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 12:48:35 2018

@author: bhur
"""

#import dependencies
import json
import pandas as pd
import numpy as np
import nltk
import csv
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

#read in files
#must have ABLIST_NEW.csv in working folder with columns 'Medication' and 'Antimicrobial'
#where Antimicrobial is ingredient and Medication is medication name
ABLIST_NEW = pd.read_csv('ABLIST_NEW.csv', skip_blank_lines=True).fillna('')
ITEM_LIST = pd.read_csv('is_ab.csv')
ABLIST_NEW['Antimicrobial'] = ABLIST_NEW['Antimicrobial'].str.lower().replace({r'\W' : " "}, regex=True)
ABLIST_NEW['Antimicrobial'] = ABLIST_NEW['Antimicrobial'].apply(tokenizer.tokenize)
ABLIST_NEW['Medication'] = ABLIST_NEW['Medication'].str.lower()
ABLIST_NEW['Medication'] = ABLIST_NEW['Medication'].apply(tokenizer.tokenize)
#
##switch column name to match item
#ITEM_LIST['Item Name'] = ITEM_LIST['item']
ITEM_LIST.columns = ['item']

#create ratio of edit distance between two strings / length of string1
def editRatio(string1, string2):
    l1 = len(string1) 
    l2 = len(string2)

#create a table matching length of strings
    table = [[0 for x in range(l2+ 1)] for x in range(l1 + 1)]

#fill table with minium amount of changes necessary for each character
    for i in range(l1 + 1):
        for j in range(l2 + 1):
          
            if i == 0:
                table[i][j] = j  

            elif j == 0:
                table[i][j] = i  

            elif string1[i - 1] == string2[j - 1]:
                table[i][j] = table[i - 1][j - 1]

            else:
                table[i][j] = 1 + min(table[i][j - 1],  # Insert
                                   table[i - 1][j],  # Remove
                                   table[i - 1][j - 1])  # Replace

#return ratio of edit distance divided by length of string
                
    return (table[l1][l2] / l1)

d = {}

#make strings lowercased

ITEM_LIST['item'] = ITEM_LIST['item'].str.lower()
ITEM_LIST['item'] = ITEM_LIST['item'].apply(tokenizer.tokenize)


#create edit distance dictionary between all ab and item tokens

for item_line in ITEM_LIST['item']:
    for item_token in item_line:
        for ingredient, med in zip(ABLIST_NEW.Antimicrobial, ABLIST_NEW.Medication):
            for ab_token in med:
                 if ab_token not in d:
                     d[ab_token] = {}
                 if item_token not in d[ab_token]:
                     
                     ratio = editRatio(ab_token, item_token)
                     d[ab_token][item_token] = ratio 
#store dictionary 
                     
js = json.dumps(d)

# Open new json file if not exist it will create
fp = open('new_vic_dict.json', 'a')

# write to json file
fp.write(js)

# close the connection
fp.close()


#load the json file into dictionary
json1_file = open('vic_dict.json')
json1_str = json1_file.read()
d = json.loads(json1_str)



