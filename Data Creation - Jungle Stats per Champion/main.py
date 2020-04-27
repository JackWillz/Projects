# Imports
import requests
import time as t
import get_match_ids
import match_data
import champ_parse


def main(regions, tiers, yyyy, mm, dd, key, session):
    start = t.time()
    print("Starting process")
    print("Getting match IDs..")
    match_ids, regions, tiers = get_match_ids.get_match_ids(regions, tiers, yyyy, mm, dd, key, session)
    print(str(len(match_ids)), " match IDs found")
    print("Building match data")
    data = match_data.all_runs(match_ids, regions, tiers, key, session)
    print("Match data built, saving progress")
    data.to_pickle('match_data2.pkl')
    print("Aggregating champion level information")
    champ_stats = champ_parse.champ_parse(data)
    print("Data aggregated, saving progress")
    champ_stats.to_pickle('champ_stats2.pkl')
    champ_stats.to_csv('champ_stats2.csv')
    finish = t.time()
    run_time = finish - start
    print("Process complete, total run time: "+ str(int(run_time / 60)) + " minutes")
    return data, champ_stats


if __name__ == '__main__':
    regions = ['EUW1',
               #'KR',
               #'NA1'
               ]
    tiers = [
        ['CHALLENGER', 'I'],
        ['GRANDMASTER', 'I'],
        #['MASTER', 'I'],
        #['DIAMOND', 'II'],
        #['PLATINUM', 'II'],
        #['GOLD', 'II'],
        #['SILVER', 'II'],
        #['BRONZE', 'II'],
        #['IRON', 'II']
    ]
    yyyy = 2020
    mm = 4
    dd = 19
    key = 'SECURE-KEY'
    session = requests.Session()
    main(regions, tiers, yyyy, mm, dd, key, session)

