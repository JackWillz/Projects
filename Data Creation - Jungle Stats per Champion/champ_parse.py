import pandas as pd
from math import floor
import numpy as np
import numpy.ma as ma
from itertools import zip_longest


def create_groupby(df):
    champ_stats = df.groupby(['champ_id', 'tier']).mean()
    alt_mean_cols = ['spell1', 'spell2', 'perk_main', 'perk_second']
    champ_stats.drop(alt_mean_cols, axis=1, inplace=True)
    return champ_stats


def count_groupby(df, champ_stats):
    count = df.groupby(['champ_id', 'tier']).count()
    count.reset_index(inplace = True)
    count = count[['champ_id', 'tier', 'game_duration']]
    count.rename(columns={'game_duration': 'count'}, inplace=True)
    champ_stats = pd.merge(champ_stats, count, on=['champ_id', 'tier'])
    return champ_stats


def database_champs(df):
    champs = df['champ_id'].unique()
    return champs


def average(a_list):
    average_list = [np.ma.average(ma.masked_values(temp_list, None)) for temp_list in zip_longest(*a_list)]
    return average_list

def average_list(df, champ_stats, champs, column):
    stat_dict = {}
    for champ in champs:
        champ_lists = df[df['champ_id'] == champ][column]
        stat_dict[champ] = list(average(champ_lists))
    champ_stats[column] = df['champ_id'].map(stat_dict)
    return champ_stats


def average_all_lists(df, champ_stats, champs):
    columns = ['gpm', 'xpm', 'cpm']
    for column in columns:
        champ_stats = average_list(df, champ_stats, champs, column)
    return champ_stats


def popular(df, champ_id, perk_name):
    filtered = df[df['champ_id'] == champ_id]
    pop_id = filtered[perk_name].value_counts().idxmax()
    pop_value = filtered[perk_name].value_counts().max()
    return pop_id, pop_value


def add_popular(df, champ_stats, champs, perk_name):
    id_dict = {}
    value_dict = {}
    for champ in champs:
        pop_id, pop_value = popular(df, champ, perk_name)
        id_dict[champ] = pop_id
        value_dict[champ] = pop_value
    champ_stats[perk_name] = champ_stats['champ_id'].map(id_dict)
    champ_stats[perk_name + '_count'] = champ_stats['champ_id'].map(value_dict)
    return champ_stats


def popular_all(df, champ_stats, champs):
    columns = ['spell1', 'spell2', 'perk_main', 'perk_second', 'perks', 'runes', 'items']
    for column in columns:
        champ_stats = add_popular(df, champ_stats, champs, column)
    return champ_stats


def create_interval_times(min_time, max_time):
    min_times = []
    max_times = []
    for i in range(min_time, max_time + 1, 5):
        max_times.append(i * 60)
        min_times.append((i - 5) * 60)
    max_times.append(120 * 60)
    min_times[0] = 0
    return min_times, max_times


def wr_by_time(df, champ_id, interval_times):
    wrs = []
    for j in range(len(interval_times[0])):
        filtered = df[(df['champ_id'] == champ_id) &
                      (df['game_duration'] <= interval_times[1][j]) &
                      (df['game_duration'] > interval_times[0][j])
                      ]
        wr = filtered['result'].mean()
        wrs.append(wr)
    return wrs


def wr_by_time_all(df, champ_stats, champs):
    wr_dict = {}
    interval_times = create_interval_times(20, 40)
    for champ in champs:
        wrs = wr_by_time(df, champ, interval_times)
        wr_dict[champ] = wrs
    champ_stats['wr_time'] = champ_stats['champ_id'].map(wr_dict)
    return champ_stats


def sec_to_min(num):
    mins = floor(num / 60)
    secs = int(((num / 60) % 1) * 60)
    time = str(mins) + '.' + str(secs)
    return time


def pm_calc(val, secs):
    per_sec = val / secs
    per_min = per_sec * 60
    return per_min


def extra_features(df):
    df['game_minutes'] = df['game_duration'].apply(sec_to_min)
    champ_ids = pd.read_csv('champ_ids.csv')
    df = pd.merge(df, champ_ids[['champ_id', 'champion']], on='champ_id')
    df['kpm'] = pm_calc(df['kills'], df['game_duration'])
    df['depm'] = pm_calc(df['deaths'], df['game_duration'])
    df['apm'] = pm_calc(df['assists'], df['game_duration'])
    df['dapm'] = pm_calc(df['damage_dealt'], df['game_duration'])
    df['vpm'] = pm_calc(df['vision_score'], df['game_duration'])
    df['gold_pm'] = pm_calc(df['gold_earnt'], df['game_duration'])
    df['enemy_jpm'] = pm_calc(df['enemy_jungle'], df['game_duration'])
    df['friendly_jpm'] = pm_calc(df['friendly_jungle'], df['game_duration'])
    df['total_jungle'] = df['enemy_jungle'] + df['friendly_jungle'] + df['scuttles_killed']
    df['total_jpm'] = pm_calc(df['total_jungle'], df['game_duration'])
    return df


def final_tweaks(df):
    # change the order columns appear
    cols = list(df)
    cols.insert(1, cols.pop(cols.index('champion')))
    cols.insert(2, cols.pop(cols.index('count')))
    df = df.loc[:, cols]
    # order by count, remove low counts
    df = df.sort_values('count', ascending= False)
    df = df[df['count'] > 100]
    return df



def champ_parse(df):
    champs = database_champs(df)
    champ_stats = create_groupby(df)
    champ_stats = count_groupby(df, champ_stats)
    champ_stats = average_all_lists(df, champ_stats, champs)
    champ_stats = wr_by_time_all(df, champ_stats, champs)
    champ_stats = popular_all(df, champ_stats, champs)
    champ_stats = extra_features(champ_stats)
    champ_stats = final_tweaks(champ_stats)
    return champ_stats

def read_files():
    data = pd.read_pickle('match_data.pkl')
    return data

df = read_files()
champ_stats = champ_parse(df)
champ_stats.to_pickle('champ_stats2.pkl')
champ_stats.to_csv('champ_stats2.csv')

