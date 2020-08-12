# Import Packages
import json
import time
import requests
import pandas as pd


#Set API key, retrieve 'encryptedAccountId' using summoner name
def retrieve_accountid(apikey, summonername):
    acct_r = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+summonername+'?api_key=' + apikey)
    response = json.loads(acct_r.text)
    accountid = response['accountId']
    return accountid


#Retrieve match list by account.
#RIOT API only provides 100 matches at a time. Loop 'paginates' matches by increasing match index number by 101 each request.
#End loop if number of matches retrived is 0.
def retrieve_account_matches(apikey, accountid, queue=None):
    begin = 0
    full_matches_list = []
    while True:
        if queue==None:
            full_matches_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/'+ accountid + '?beginIndex=' + str(begin) + '&api_key=' + apikey)
        else:
            full_matches_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/'+ accountid + '?beginIndex=' + str(begin) + '&api_key=' + apikey + '&queue=' + str(queue))
        if len(json.loads(full_matches_r.text)['matches']) > 0:
            gen = (match for match in json.loads(full_matches_r.text)['matches'])
            for match in gen:
                full_matches_list.append(match)
            begin += 101
        else: break
    matches_df = pd.DataFrame.from_dict(full_matches_list)
    return matches_df


#Match data retrieved above provides unique match ID, but no detail data.
#Loop through match IDs retrieved and request detail data.
#API allows no more than 100 requests every 120 secs. If request is denied (429 or 504), wait 120s and re-try.
def retrieve_match_data(apikey, gameids):
    raw_match_data_list = []
    total_matches = str(len(gameids))
    print('Processing ' + total_matches + ' matches.')
    for gameid in gameids:
        indv_match_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(gameid) + '?api_key=' + apikey)
        if indv_match_r.status_code == 200:
            match = json.loads(indv_match_r.text)
            raw_match_data_list.append(match)
        elif indv_match_r.status_code == 429 or indv_match_r.status_code == 504:
            print('Timeout. \n' + str(len(raw_match_data_list)) + ' out of ' + total_matches + ' processed.\nRetrying in 120 secs.')
            time.sleep(120)
            print('Retrying...')
            match_r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + str(gameid) + '?api_key=' + apikey)
            if indv_match_r.status_code != 200:
                print('Received second error after waiting: ' + str(indv_match_r.status_code) + ' Cancelleing match data retrieval.')
                break
            elif indv_match_r.status_code == 200:
                match = json.loads(match_r.text)
                raw_match_data_list.append(match)
            else:
                print('Received unexpected code: ' + str(indv_match_r.status_code))
                print('Match retrieval cancelled.')
                break
    return raw_match_data_list


#Collect match data.
def parse_match_data(summonername, raw_match_data_list):
    rel_match_data_list = []
    for m in raw_match_data_list:
        for p in m['participantIdentities']:
            if p['player']['summonerName'] == summonername:
                pid = p['participantId']
        match_data = {}
        match_data['gameId'] = m['gameId']
        match_data['duration'] = m['gameDuration']
        match_data['team'] = m['participants'][pid-1]['teamId']
        stats_dict = m['participants'][pid-1]['stats']
        for key in stats_dict:
                match_data[key] = stats_dict[key]
                rel_match_data_list.append(match_data)
    match_data_df = pd.DataFrame.from_dict(rel_match_data_list)
    return match_data_df


#Get champion specific information.
def retrieve_champ_info():
    champs_r = requests.get('http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json')
    champs = json.loads(champs_r.text)['data']
    champ_data_list = []
    for c in champs:
        champ_data = {}
        champ_data['name'] = c
        champ_data['role'] = champs[c]['tags'][0]
        champ_data['id'] = champs[c]['key']
        champ_data['attack'] = champs[c]['info']['attack']
        champ_data['defense'] = champs[c]['info']['defense']
        champ_data['magic'] = champs[c]['info']['magic']
        champ_data['difficulty'] = champs[c]['info']['difficulty']
        champ_data_list.append(champ_data)
    champs_df = pd.DataFrame.from_dict(champ_data_list)
    champs_df['id'] = pd.to_numeric(champs_df['id'])
    return champs_df