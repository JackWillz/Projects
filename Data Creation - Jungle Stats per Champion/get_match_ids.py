import random
import time as t
import datetime
from multiprocessing import Pool


# Python code to remove duplicate elements
def remove_duplicates(list1, list2, list3):
    final_list1 = []
    final_list2 = []
    final_list3 = []
    for i in range(len(list1)):
        if list1[i] not in final_list1:
            final_list1.append(list1[i])
            final_list2.append(list2[i])
            final_list3.append(list3[i])
    return final_list1, final_list2, final_list3


def return_json(URL, session):
    while True:
        response = session.get(URL)
        try:
            if response.json()['status']['status_code'] == 404:
                break
            elif response.json()['status']['status_code'] == 429:
                t.sleep(10)
                continue
            else:
                break
        except:
            break
    return response.json()


def set_volume(tier):
    if tier == 'CHALLENGER':
        size = 2
    elif tier == 'GRANDMASTER':
        size = 4
    elif tier == 'MASTER':
        size = 4
    else:
        size = 10
    return size


def get_summoners(fullRegionList, tierList, key, session):
    summonerIds, summonerRegions, summonerTier = [], [], []
    for y in fullRegionList:
        for z in range(len(tierList)):
            size = set_volume(tierList[z][0])
            for x in range(size):
                page = x + 1
                URL_ids = ('https://' + y + '.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/' +
                           tierList[z][0] + '/' + tierList[z][1] + '/?page=' + str(page) + '&api_key=' + key)
                json = return_json(URL_ids, session)
                for x in range(0, len(json)):
                    summonerIds.append(json[x]['summonerId'])
                    summonerRegions.append(y)
                    summonerTier.append(tierList[z][0])
    return summonerIds, summonerRegions, summonerTier


def name_to_id(selectedIds, selectedRegions, selectedTiers,  key, session):
    accountIds, accountRegions, accountTiers = [], [], []
    for i in range(len(selectedIds)):
        URL = 'https://' + selectedRegions[i] + '.api.riotgames.com/lol/summoner/v4/summoners/' + selectedIds[
            i] + '/?api_key=' + key
        json = return_json(URL, session)
        account_id = json['accountId']
        accountIds.append(account_id)
        accountRegions.append(selectedRegions[i])
        accountTiers.append(selectedTiers[i])
    return accountIds, accountRegions, accountTiers


def find_time_interval(yyyy, mm, dd):
    # Set week period prior to given date
    ed = datetime.date(yyyy, mm, dd)
    endTime = t.mktime(ed.timetuple())
    endTime = str(int(endTime)) + "000"
    sd = datetime.date(yyyy, mm, dd) - datetime.timedelta(7)
    startTime = t.mktime(sd.timetuple())
    startTime = str(int(startTime)) + "000"
    return startTime, endTime


def id_to_match(accountIds, accountRegions, accountTiers, yyyy, mm, dd, key, session):
    startTime, endTime = find_time_interval(yyyy, mm, dd)
    gameIds, regions, tiers = [], [], []
    for i in range(len(accountIds)):
        URL = 'https://' + accountRegions[i] + '.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountIds[
            i] + '/?endTime=' + endTime + '&beginTime=' + startTime + '&api_key=' + key
        try:
            json = return_json(URL, session)
            len_matches = len(json['matches'])
            if len_matches > 20:
                len_matches = 20
            for j in range(0, len_matches):
                if json['matches'][j]['queue'] == 420:
                    gameId = json['matches'][j]['gameId']
                    gameIds.append(gameId)
                    regions.append(accountRegions[i])
                    tiers.append(accountTiers[i])
        except:
            pass
    return gameIds, regions, tiers

def create_args(regions, tiers, yyyy, mm, dd, key, session):
    other_vars = [yyyy, mm, dd, key, session]
    all_args = []
    for region in regions:
        for tier in tiers:
            args = []
            args.append([region])
            args.append([tier])
            for other in other_vars:
                args.append(other)
            all_args.append(args)
    return all_args

def single_run(regions, tiers, yyyy, mm, dd, key, session):
    summonerIds, summonerRegions, summonerTiers = get_summoners(regions, tiers, key, session)
    accountIds, accountRegions, accountTiers = name_to_id(summonerIds, summonerRegions, summonerTiers, key, session)
    gameIds, regions, tiers = id_to_match(accountIds, accountRegions, accountTiers, yyyy, mm, dd, key, session)
    return gameIds, regions, tiers


def get_match_ids(regions, tiers, yyyy, mm, dd, key, session):
    args = create_args(regions, tiers, yyyy, mm, dd, key, session)
    k = True
    if k == True:
        with Pool(processes = 8) as p:
            results = p.starmap(single_run, args)
        gameIds, regions, tiers = [], [], []
        for i in range(len(results)):
            gameIds.extend(results[i][0])
            regions.extend(results[i][1])
            tiers.extend(results[i][2])
    else:
        gameIds, regions, tiers = single_run(regions, tiers, yyyy, mm, dd, key, session)
    dedup_gameIds, dedup_regions, dedup_tiers = remove_duplicates(gameIds, regions, tiers)
    return dedup_gameIds, dedup_regions, dedup_tiers
