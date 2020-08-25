# Import Packages
import json
import time
import requests
import pandas as pd


# Set API key, retrieve 'encryptedAccountId' using summoner name
def retrieve_accountid(apikey, summonername):
    acct_r = requests.get(
        'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonername + '?api_key=' + apikey)
    if acct_r.status_code != 200:
        return print('Received error: ' + str(acct_r.status_code))
    response = json.loads(acct_r.text)
    accountid = response['accountId']
    return accountid



# Retrieve match list by account. RIOT API only provides 100 matches at a time. Loop 'paginates' matches by
# increasing match index number by 101 each request. End loop if number of matches retrieved is 0.
def retrieve_account_matches(apikey, accountid, beginindex=0, limit=None, server='na1', **filters):
    full_matches_list = []
    champion = ''
    queue = ''
    endtime = ''
    begintime = ''
    if filters.get('champion') is not None:
        champion = str(filters.get('champion'))
    if filters.get('queue') is not None:
        queue = str(filters.get('queue'))
    if filters.get('endtime') is not None:
        endtime = str(filters.get('begintime'))            
    if filters.get('begintime') is not None:
        begintime = str(filters.get('begintime'))
    while True:
        if len(full_matches_list) == limit:
            break
        full_matches_r = requests.get('https://'+server+'.api.riotgames.com/lol/match/v4/matchlists/by-account/' 
                                      + accountid + '?api_key=' + apikey + '&champion=' + champion +
                                      '&queue=' + queue + '&endTime=' + endtime + '&beginTime=' + begintime + 
                                      '&beginIndex=' + str(beginindex))
        if full_matches_r.status_code != 200:
            return print('Received error: ' + str(full_matches_r.status_code))
        if len(json.loads(full_matches_r.text)['matches']) > 0:
            gen = (match for match in json.loads(full_matches_r.text)['matches'])
            for match in gen:
                full_matches_list.append(match)
                if len(full_matches_list) == limit:
                    break
            beginindex += 101
        else:
            break
    matches_df = pd.DataFrame.from_dict(full_matches_list)
    return matches_df



# Match data retrieved above provides unique match ID, but no detail data.
# Loop through match IDs retrieved and request detail data.
# API allows no more than 100 requests every 120 secs. If request is denied (429 or 504), wait 120s and re-try.
def retrieve_match_data(apikey, gameids, server='na1', limit=None):
    raw_match_data_list = []
    total_matches = len(gameids)
    if limit is not None and limit > total_matches:
        print('Given limit is greater than total matches. Retrieving all matches.')
    elif limit is not None:
        total_matches = limit
    print('Collecting ' + str(total_matches) + ' matches.')
    for i, gameid in enumerate(gameids):
        if i == limit:
            break
        indv_match_r = requests.get(
            'https://'+server+'.api.riotgames.com/lol/match/v4/matches/' + str(gameid) + '?api_key=' + apikey)
        if indv_match_r.status_code == 200:
            match = json.loads(indv_match_r.text)
            raw_match_data_list.append(match)
        elif indv_match_r.status_code == 429 or indv_match_r.status_code == 504:
            print('Timeout. \n' + str(len(raw_match_data_list)) + ' out of ' + str(
                total_matches) + ' collected.\nRetrying in 120 secs.')
            time.sleep(120)
            print('Retrying...')
            indv_match_r = requests.get(
                'https://'+server+'.api.riotgames.com/lol/match/v4/matches/' + str(gameid) + '?api_key=' + apikey)
            if indv_match_r.status_code == 200:
                match = json.loads(indv_match_r.text)
                raw_match_data_list.append(match)
            else:
                print('Received second error after waiting: ' + str(indv_match_r.status_code))
                print('Match retrieval cancelled.')
                break
        else:
            print('Received error: ' + str(indv_match_r.status_code))
            skip = input('Skip match ' + str(i) + ' ? (y to skip / n to cancel process)')
            if skip == 'y':
                continue
            elif skip == 'n':
                print('Process cancelled at match ' + str(i))
                return raw_match_data_list
    print(str(len(raw_match_data_list)) + ' matches collected.')
    return raw_match_data_list



# Collect match data.
def parse_match_data(raw_match_data_list):
    match_data_list = []
    player_data_list = []
    team_data_list = []
    for m in raw_match_data_list:
        matchdto = {'gameid': m['gameId'], 'queueid':m['queueId'],
                      'type':m['gameType'], 'duration':m['gameDuration'], 
                      'platformid':m['platformId'], 'creation':m['gameCreation'],
                      'seasonid':m['seasonId'], 'version':m['gameVersion'], 
                      'mapid':m['mapId'], 'mode':m['gameMode']}
        match_data_list.append(matchdto)
        for pi in m['participantIdentities']:
            pid = pi['participantId']
            playername = pi['player']['summonerName']
            champion = m['participants'][pid-1]['championId']
            spell1 = m['participants'][pid-1]['spell1Id']
            spell2 = m['participants'][pid-1]['spell2Id']
            team = m['participants'][pid-1]['teamId']
            player = {'gameid':m['gameId'], 'participantId':pid, 'name':playername,
                      'championid':champion, 'spell1':spell1, 'spell2':spell2, 
                      'teamid':team}
            for stat in m['participants'][pid-1]['stats']:
                player[stat] = m['participants'][pid-1]['stats'][stat]
            player_data_list.append(player)
        for t in m['teams']:
            team = {}
            team['gameid'] = m['gameId']
            for tstat in t:
                team[tstat] = t[tstat]
            team_data_list.append(team)
    match_data_df = pd.DataFrame.from_dict(match_data_list)
    player_data_df = pd.DataFrame.from_dict(player_data_list)
    team_data_df = pd.DataFrame.from_dict(team_data_list)
    return match_data_df, player_data_df, team_data_df



# Get champion specific information.
def retrieve_champ_info():
    champs_r = requests.get('http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json')
    champs = json.loads(champs_r.text)['data']
    champ_data_list = []
    for c in champs:
        champ_data = {'name': c, 'role': champs[c]['tags'][0], 'id': champs[c]['key'],
                      'attack': champs[c]['info']['attack'], 'defense': champs[c]['info']['defense'],
                      'magic': champs[c]['info']['magic'], 'difficulty': champs[c]['info']['difficulty']}
        champ_data_list.append(champ_data)
    champs_df = pd.DataFrame.from_dict(champ_data_list)
    champs_df['id'] = pd.to_numeric(champs_df['id'])
    return champs_df


# Get item specific information
def retrieve_item_info():
    items_r = requests.get('http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/item.json')
    items = json.loads(items_r.text)['data']
    item_data_list = []
    for i in items:
        item_data = {'id':i, 'name':items[i]['name'], 'basecost':items[i]['gold']['base'], 
                      'totalcost':items[i]['gold']['total']}
        item_data_list.append(item_data)
    item_df = pd.DataFrame.from_dict(item_data_list)
    item_df['id'] = pd.to_numeric(item_df['id'])
    return item_df



def retrieve_spell_info():
    spells_r = requests.get('http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/summoner.json')
    spells = json.loads(spells_r.text)['data']
    spells_data_list = []
    for i in spells:
        spells_data = {'name':i, 'id':spells[i]['key']}
        spells_data_list.append(spells_data)
    spells_df = pd.DataFrame.from_dict(spells_data_list)
    spells_df['id'] = pd.to_numeric(spells_df['id'])
    spells_df['name'] = spells_df['name'].replace({'Summoner':''}, regex=True)
    return spells_df













