#import dependencies
import pandas as pd
import numpy as np
import nltk
import csv
import json
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

ITEM_LIST.columns = ['item']

ITEM_LIST['item'] = ITEM_LIST['item'].str.lower()
ITEM_LIST['item'] = ITEM_LIST['item'].apply(tokenizer.tokenize)

#search the rows in antibiotic list for substrings in item list
tp1 = ()
np1 = ()
tp2 = ()
np2 = ()

new_stack = ()
new_list = []
exception_list = ['apex', 'virbac', 'combo', 'special', 'dbl', 'sodium', 'vetafarm', \
                  'vetfarm', 'promo', 'novafil', 'pharmachem', 'cyclosporine', 'sd']

i = 0
d={}
new_dict = {}
stringdistance = 0



#load the json file into dictionary
json1_file = open('vic_dict.json')
json1_str = json1_file.read()
d = json.loads(json1_str)


string_list = []
for item_line in ITEM_LIST['item']:
    edit_matched = 0
    matched = 0
    signal = 0
    sd_list = []
    dc = []
    medication = []
    ing = []
    

    for drug_class, ingredient, med in zip(ABLIST_NEW.CLASS, ABLIST_NEW.Antimicrobial, ABLIST_NEW.Medication):
        if signal == 0 and matched == 0 and edit_matched == 0:
            if med == []:
                med = ['xxxxx']
            if ingredient == []:
                ingredient = ['xxxxx']
    
            if (ingredient[0] in item_line) or (med[0] in item_line):
                if (len(ingredient[0]) <3) or (len(med[0]) < 3) and (med[0] and med[-1] not in item_line):
#                    debug what is being matched if you get too many false positives
#                    medication = med
#                    ing = ingredient
                    continue
                

                if (med[0] or ingredient[0] in exception_list) and (med[0] and med[-1] not in item_line):
#                    debug what is being matched if you get too many false positives
#                    medication = med
#                    ing = ingredient
                    continue
   
                    
                else:
                    medication =med
                    ing = ingredient
                    dc = [drug_class]                          

                    matched = 1
                    


    if matched == 0 and edit_matched == 0:
        for item_token in item_line:
            tokens_found = 0

            totaldist = 1000
            ratiolist = []
            for drug_class, ingredient, med in zip(ABLIST_NEW.CLASS, ABLIST_NEW.Antimicrobial, ABLIST_NEW.Medication):
                
                if tokens_found == 0 and matched == 0 and edit_matched == 0:
                   
                    #create list of string distances
                    sd_list = []
                


                    for ab_token in med:
                        if matched == 0 and edit_matched == 0:
                            stringdistance = d[ab_token][item_token]
                            sd_list.append(stringdistance)
                    
#                            stringdistance = editDistDP(ab_token, item_token, len(ab_token), len(item_token))
                            
                            if med[0] == ab_token and (ab_token not in exception_list) \
                            and len(ab_token) > 3 \
                            and (item_token not in exception_list) and (stringdistance < 0.25):
        #                        matched(med, item_line, how_matched=['first_token', stringdistance])
#                                edit_matched = 1
                                medication = med
                                ing = ingredient
                                dc = [drug_class]                           

                                tokens_found +=1
                                edit_matched = 1

                                
                            elif stringdistance < 0.2:
                                medication =med
                                ing = ingredient
                                dc = [drug_class]                         

                                tokens_found +=1
                                if totaldist == 1000:
                                    totaldist = stringdistance
                                else:
                                    totaldist += stringdistance
                                    
                    if tokens_found > 1:
                        sd_list.sort()
                        print('sorted', sd_list)
                        if (sd_list[0] + sd_list[1]) < 0.8:
                            edit_matched = 1
                            medication =med
                            ing = ingredient
                            dc = [drug_class]                    
                       
                            
                                
        

#                        if tokens_found > 1 and totaldist < 0.6:
#                            edit_matched = 1
#                            medication = med
#                            ing = ingredient
    
    ####  fix for creating same column for rest of scripts
    if edit_matched == 1:
        matched = edit_matched
    
    if matched == 0 and edit_matched == 0:
        dc = []
        medication = []
        ing = []
        
    
    
    string_list.append([matched, edit_matched, sd_list, item_line, medication, ing, dc])

col_list = ['re_matched', 'edit_matched', 'string_distance_list', 'Item Label', 'Medication', 'Ingredient', 'Drug Class']
df2 = pd.DataFrame(string_list, columns=col_list)

df2.to_csv('reg_char_dist.csv', index=False)

