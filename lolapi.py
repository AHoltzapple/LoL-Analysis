# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 13:50:02 2020

@author: arshl
"""

import requests
import json
import pandas as pd
import numpy as np
import time


import sklearn
from pylab import rcParams
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_predict
from sklearn.linear_model import LogisticRegression

from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score


apikey = 'RGAPI-86277f2d-fd3a-4fb1-9832-6063ae3917a3'
acct_r = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/erythro25?api_key=' + apikey)

response = json.loads(acct_r.text)
accountid = response['accountId']

begin = 0
matches_list = []

while True:
    matches_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/'+ accountid + '?beginIndex=' + str(begin) + '&api_key=' + apikey)
    if len(json.loads(matches_r.text)['matches']) != 0:
        gen = (match for match in json.loads(matches_r.text)['matches'])
        for match in gen:
            matches_list.append(match)
        begin += 101
    else: break

matches_df = pd.DataFrame.from_dict(matches_list)

matches_df['queue'].value_counts()

arams = matches_df[matches_df['queue']==450]

match_data_list = []

mn=1
for gameid in arams['gameId']:
    print('Processing match: '+ str(mn) + ' / ' + str(gameid))
    match_data = {}
    match_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(gameid) + '?api_key=' + apikey)
    if match_r.status_code == 200:
        match = json.loads(match_r.text)
        match_data['gameid'] = match['gameId']
        for i, p in enumerate(match['participants']):
            champ = 'champ'+str(i+1)
            match_data[champ] = p['championId']
        for i, t in enumerate(match['teams']):
            team = 'team'+str(i+1)+'result'
            match_data[team] = t['win']
        match_data_list.append(match_data)
    elif match_r.status_code == 429 or match_r.status_code == 504:
        for n in range(24):
            print('Timeout. Retrying in ' + str(120-n*5) + ' secs.')
            time.sleep(5)
        match_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(gameid) + '?api_key=' + apikey)
        match = json.loads(match_r.text)
        match_data['gameid'] = match['gameId']
        for i, p in enumerate(match['participants']):
            champ = 'champ'+str(i+1)
            match_data[champ] = p['championId']
        for i, t in enumerate(match['teams']):
            team = 'team'+str(i+1)+'result'
            match_data[team] = t['win']
        match_data_list.append(match_data)
    else: break
    mn += 1
    
match_df = pd.DataFrame.from_dict(match_data_list)

sum(match_df.duplicated('gameid'))

champs_r = requests.get('http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json')

champs = json.loads(champs_r.text)['data']

champ_data_list = []
for key in champs:
    champ_data = {}
    champ_data['name'] = key
    champ_data['role'] = champs[key]['tags'][0]
    champ_data['id'] = champs[key]['key']
    champ_data_list.append(champ_data)

champs_df = pd.DataFrame.from_dict(champ_data_list)

champs_df['id'] = pd.to_numeric(champs_df['id'])

role_dict = champs_df.set_index('id').to_dict()['role']

match_df2 = match_df.replace(role_dict)

match_df2 = match_df2.astype('category')
#######################################

champs_df.role.value_counts()

roles = ['Fighter','Mage','Marksman','Tank','Assassin','Support']

match_df2['t1_fighter'] = np.where((match_df2['champ1']=='Fighter')|(match_df2['champ2']=='Fighter')|(match_df2['champ3']=='Fighter')|(match_df2['champ4']=='Fighter')|(match_df2['champ5']=='Fighter'),1,0)
match_df2['t1_mage'] = np.where((match_df2['champ1']=='Mage')|(match_df2['champ2']=='Mage')|(match_df2['champ3']=='Mage')|(match_df2['champ4']=='Mage')|(match_df2['champ5']=='Mage'),1,0)
match_df2['t1_marksman'] = np.where((match_df2['champ1']=='Marksman')|(match_df2['champ2']=='Marksman')|(match_df2['champ3']=='Marksman')|(match_df2['champ4']=='Marksman')|(match_df2['champ5']=='Marksman'),1,0)
match_df2['t1_tank'] = np.where((match_df2['champ1']=='Tank')|(match_df2['champ2']=='Tank')|(match_df2['champ3']=='Tank')|(match_df2['champ4']=='Tank')|(match_df2['champ5']=='Tank'),1,0)
match_df2['t1_assassin'] = np.where((match_df2['champ1']=='Assassin')|(match_df2['champ2']=='Assassin')|(match_df2['champ3']=='Assassin')|(match_df2['champ4']=='Assassin')|(match_df2['champ5']=='Assassin'),1,0)
match_df2['t1_support'] = np.where((match_df2['champ1']=='Support')|(match_df2['champ2']=='Support')|(match_df2['champ3']=='Support')|(match_df2['champ4']=='Support')|(match_df2['champ5']=='Support'),1,0)

match_df2['t2_fighter'] = np.where((match_df2['champ6']=='Fighter')|(match_df2['champ7']=='Fighter')|(match_df2['champ8']=='Fighter')|(match_df2['champ9']=='Fighter')|(match_df2['champ10']=='Fighter'),1,0)
match_df2['t2_mage'] = np.where((match_df2['champ6']=='Mage')|(match_df2['champ7']=='Mage')|(match_df2['champ8']=='Mage')|(match_df2['champ9']=='Mage')|(match_df2['champ10']=='Mage'),1,0)
match_df2['t2_marksman'] = np.where((match_df2['champ6']=='Marksman')|(match_df2['champ7']=='Marksman')|(match_df2['champ8']=='Marksman')|(match_df2['champ9']=='Marksman')|(match_df2['champ10']=='Marksman'),1,0)
match_df2['t2_tank'] = np.where((match_df2['champ6']=='Tank')|(match_df2['champ7']=='Tank')|(match_df2['champ8']=='Tank')|(match_df2['champ9']=='Tank')|(match_df2['champ10']=='Tank'),1,0)
match_df2['t2_assassin'] = np.where((match_df2['champ6']=='Assassin')|(match_df2['champ7']=='Assassin')|(match_df2['champ8']=='Assassin')|(match_df2['champ9']=='Assassin')|(match_df2['champ10']=='Assassin'),1,0)
match_df2['t2_support'] = np.where((match_df2['champ6']=='Support')|(match_df2['champ7']=='Support')|(match_df2['champ8']=='Support')|(match_df2['champ9']=='Support')|(match_df2['champ10']=='Support'),1,0)

match_df2['team1result'] = np.where(match_df2['team1result']=='Win',1,0)
match_df2['team2result'] = np.where(match_df2['team2result']=='Win',1,0)

predictors = match_df2.drop(match_df2.loc[:,'champ1':'gameid'].columns,axis=1)
predictors = predictors.drop(['team2result'], axis=1)

x_train, x_test, y_train, y_test = train_test_split(predictors.drop('team1result',axis=1),predictors['team1result'], test_size = 0.2)

LogReg = LogisticRegression(solver='liblinear')
LogReg.fit(x_train, y_train)

y_pred = LogReg.predict(x_test)

print(classification_report(y_test, y_pred))

#########################################

match_df3 = match_df2

def count_roles(c1,c2,c3,c4,c5,role):
    total = sum([c1==role,c2==role,c3==role,c4==role,c5==role])
    return total

match_df3['t1_fighters'] = match_df3.apply(lambda row: count_roles(c1=row['champ1'],c2=row['champ2'],c3=row['champ3'],c4=row['champ4'],c5=row['champ5'],role='Fighter'), axis=1)
match_df3['t1_mages'] = match_df3.apply(lambda row: count_roles(c1=row['champ1'],c2=row['champ2'],c3=row['champ3'],c4=row['champ4'],c5=row['champ5'],role='Mage'), axis=1)
match_df3['t1_marksmans'] = match_df3.apply(lambda row: count_roles(c1=row['champ1'],c2=row['champ2'],c3=row['champ3'],c4=row['champ4'],c5=row['champ5'],role='Marksman'), axis=1)
match_df3['t1_tanks'] = match_df3.apply(lambda row: count_roles(c1=row['champ1'],c2=row['champ2'],c3=row['champ3'],c4=row['champ4'],c5=row['champ5'],role='Tank'), axis=1)
match_df3['t1_assassins'] = match_df3.apply(lambda row: count_roles(c1=row['champ1'],c2=row['champ2'],c3=row['champ3'],c4=row['champ4'],c5=row['champ5'],role='Assassin'), axis=1)
match_df3['t1_supports'] = match_df3.apply(lambda row: count_roles(c1=row['champ1'],c2=row['champ2'],c3=row['champ3'],c4=row['champ4'],c5=row['champ5'],role='Support'), axis=1)

match_df3['t2_fighters'] = match_df3.apply(lambda row: count_roles(c1=row['champ6'],c2=row['champ7'],c3=row['champ8'],c4=row['champ9'],c5=row['champ10'],role='Fighter'), axis=1)
match_df3['t2_mages'] = match_df3.apply(lambda row: count_roles(c1=row['champ6'],c2=row['champ7'],c3=row['champ8'],c4=row['champ9'],c5=row['champ10'],role='Mage'), axis=1)
match_df3['t2_marksmans'] = match_df3.apply(lambda row: count_roles(c1=row['champ6'],c2=row['champ7'],c3=row['champ8'],c4=row['champ9'],c5=row['champ10'],role='Marksman'), axis=1)
match_df3['t2_tanks'] = match_df3.apply(lambda row: count_roles(c1=row['champ6'],c2=row['champ7'],c3=row['champ8'],c4=row['champ9'],c5=row['champ10'],role='Tank'), axis=1)
match_df3['t2_assassins'] = match_df3.apply(lambda row: count_roles(c1=row['champ6'],c2=row['champ7'],c3=row['champ8'],c4=row['champ9'],c5=row['champ10'],role='Assassin'), axis=1)
match_df3['t2_supports'] = match_df3.apply(lambda row: count_roles(c1=row['champ6'],c2=row['champ7'],c3=row['champ8'],c4=row['champ9'],c5=row['champ10'],role='Support'), axis=1)

df3preds = match_df3.drop(match_df3.loc[:,'champ1':'gameid'].columns,axis=1)
df3preds = df3preds.drop(match_df3.loc[:,'team2result':'t2_support'].columns,axis=1)

x_train, x_test, y_train, y_test = train_test_split(df3preds.drop('team1result',axis=1),df3preds['team1result'], test_size = 0.2)

LogReg = LogisticRegression(solver='liblinear')
LogReg.fit(x_train, y_train)

y_pred = LogReg.predict(x_test)

print(classification_report(y_test, y_pred))

y_train_pred = cross_val_predict(LogReg, x_train, y_train, cv=5)
confusion_matrix(y_train, y_train_pred)
precision_score(y_train, y_train_pred)


test_team = df3preds[100:101]
test_teams = np.array([1,1,1,1,1,0,0,3,1,0,1,0]).reshape(1,-1)

LogReg.predict(test_teams)
LogReg.predict_proba(test_teams)



