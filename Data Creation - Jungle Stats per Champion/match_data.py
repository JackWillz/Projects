# Imports
import pandas as pd
from multiprocessing import Pool


# For any URL, return the JSON
def return_json(URL, session):
    while True:
        response = session.get(URL)
        try:
            # Check for 404 error and quit if received
            if response.json()['status']['status_code'] == 404:
                return "error - status code 404"
            # Check for 429 (too many requests made), sleep if received
            elif response.json()['status']['status_code'] == 429:
                t.sleep(10)
                continue
            else:
                return "error - unknown reason"
        except:
            break
    return response.json()


# Provide the match-id & region, receive the json of match timeline (1 minute interval of match data)
def get_matchTimeline(matchId, region, key, session):
    URL = 'https://' + region + '.api.riotgames.com/lol/match/v4/timelines/by-match/' + str(
        matchId) + '/?api_key=' + key
    json = return_json(URL, session)
    return json


# Provide the match-id & region, receive the match information (game length, participants etc..)
def get_gameInfo(matchId, region, key, session):
    URL = 'https://' + region + '.api.riotgames.com/lol/match/v4/matches/' + str(matchId) + '/?api_key=' + key
    json = return_json(URL, session)
    return json


# Provide the match data json and return the jungler + jungler participant number
def find_jungler(json, side):
    # The most jungle camps cleared so far, starting at none
    mostCamps = 0
    # Limit to blue side participants
    if side == 'Blue':
        min_id = 1
        max_id = 6
    # Limit to red side participants
    if side == 'Red':
        min_id = 6
        max_id = 11
    # For each player, check how much Jungle CS they have at 4 minutes
    for i in range(min_id, max_id):
        jungle_cs = json['frames'][4]['participantFrames'][str(i)]['jungleMinionsKilled']
        # If it's the most so far, make them the jungler and set the new record at their Jungle CS value
        if jungle_cs > mostCamps:
            jungler = i
            # Find their participant ID
            parti_jungler = json['frames'][1]['participantFrames'][str(i)]['participantId']
            mostCamps = jungle_cs
    # If no one has Jungle CS, there's an error
    if mostCamps == 0:
        return "No blue side jungler detected"
    else:
        return jungler, parti_jungler


def find_champion(json, parti_jungler):
    champion = json['participants'][parti_jungler - 1]['championId']
    return champion


def check_team_pos(parti_jungler):
    if parti_jungler <= 5:
        team_pos = 0
    else:
        team_pos = 1
    return team_pos


def check_result(result):
    if result == 'Win' or result == 'True' or result == True:
        result = 1
    else:
        result = 0
    return result


def create_var_list(variable, length, player_data):
    var_list = []
    for i in range(length):
        var_list.append(player_data[variable + str(i)])
    return var_list


def check_parti(variable, player_data):
    try:
        if check_result(player_data[variable + 'Kill']) or check_result(player_data[variable + 'Assist']):
            parti = 1
        else:
            parti = 0
    except:
        parti = 0
    return parti


def total_kd(game_json, parti_jungler):
    kills = []
    deaths = []
    if parti_jungler <= 5:
        for i in range(0, 5):
            kills.append(game_json['participants'][i]['stats']['kills'])
            deaths.append(game_json['participants'][i]['stats']['deaths'])
    else:
        for i in range(5, 10):
            kills.append(game_json['participants'][i]['stats']['kills'])
            deaths.append(game_json['participants'][i]['stats']['deaths'])

    total_kills = sum(kills)
    total_deaths = sum(deaths)
    return total_kills, total_deaths


def game_info(game_json, parti_jungler):
    team_pos = check_team_pos(parti_jungler)
    game_duration = game_json['gameDuration']
    team_data = game_json['teams'][team_pos]
    result = check_result(team_data['win'])
    first_baron = check_result(team_data['firstBaron'])
    first_dragon = check_result(team_data['firstDragon'])
    first_herald = check_result(team_data['firstRiftHerald'])
    total_barons = team_data['baronKills']
    total_dragons = team_data['dragonKills']
    total_rifts = team_data['riftHeraldKills']
    info = [game_duration, result, first_baron, first_dragon, first_herald, total_barons, total_dragons, total_rifts]
    return info


def player_info(game_json, parti_jungler, neutrals):
    spell_data = game_json['participants'][parti_jungler - 1]
    spell1 = spell_data['spell1Id']
    spell2 = spell_data['spell2Id']
    player_data = spell_data['stats']
    items = create_var_list('item', 7, player_data)
    kills = player_data['kills']
    deaths = player_data['deaths']
    assists = player_data['assists']
    total_kills, total_deaths = total_kd(game_json, parti_jungler)
    if kills > 0:
        kp = (kills + assists) / total_kills
    else:
        kp = 0
    if deaths > 0:
        death_perc = deaths / total_deaths
    else:
        death_perc = 0
    damage_dealt = player_data['totalDamageDealtToChampions']
    vision_score = player_data['visionScore']
    damage_taken = player_data['totalDamageTaken']
    gold_earnt = player_data['goldEarned']
    lane_minions = player_data['totalMinionsKilled']
    enemy_jungle = player_data['neutralMinionsKilledEnemyJungle']
    friendly_jungle = player_data['neutralMinionsKilledTeamJungle']
    neutral_jungle = (sum(neutrals) * 0.8) * 4
    scuttles_killed = round((player_data['neutralMinionsKilled'] - enemy_jungle - friendly_jungle - neutral_jungle) / 4)
    vision_wards = player_data['visionWardsBoughtInGame']
    fb_parti = check_parti('firstBlood', player_data)
    ft_parti = check_parti('firstTower', player_data)
    perks = create_var_list('perk', 6, player_data)
    perk_main = player_data['perkPrimaryStyle']
    perk_second = player_data['perkSubStyle']
    runes = create_var_list('statPerk', 3, player_data)
    info = [spell1, spell2, items, kills, deaths, assists, kp, death_perc, damage_dealt, vision_score, damage_taken,
            gold_earnt, lane_minions, enemy_jungle, friendly_jungle, scuttles_killed, vision_wards,
            fb_parti, ft_parti, perks, perk_main, perk_second, runes]
    return info


def find_frame(timeline_json, parti_jungler):
    player_frames = timeline_json['frames'][0]['participantFrames']
    for i in range(1, len(player_frames) + 1):
        if player_frames[str(i)]['participantId'] == parti_jungler:
            frame = str(i)
            return frame
        else:
            continue


def kill_check(event, parti_jungler):
    if event['killerId'] == parti_jungler or parti_jungler in event['assistingParticipantIds']:
        time = event['timestamp']
        jung_inv = True
    else:
        time = 0
        jung_inv = False
    return jung_inv, time


def timeline_info(timeline_json, parti_jungler):
    frame = find_frame(timeline_json, parti_jungler)
    gpm = []
    xpm = []
    cpm = []
    player_events = []
    kp_time = []
    for i in range(len(timeline_json['frames'])):
        gold = timeline_json['frames'][i]['participantFrames'][frame]['totalGold']
        gpm.append(gold)
        xp = timeline_json['frames'][i]['participantFrames'][frame]['xp']
        xpm.append(xp)
        camps = timeline_json['frames'][i]['participantFrames'][frame]['jungleMinionsKilled']
        cpm.append(camps)
        events = timeline_json['frames'][i]['events']
        if len(events) > 0:
            for j in range(0, len(events)):
                try:
                    if events[j]['type'] == 'CHAMPION_KILL':
                        jung_inv, kill_time = kill_check(events[j], parti_jungler)
                        if jung_inv == True:
                            kp_time.append(kill_time)
                    elif events[j]['participantId'] == parti_jungler:
                        player_events.append(events[j])
                    else:
                        continue
                except:
                    continue
    total_early_kills = sum(i < 600000 for i in kp_time)
    return gpm, xpm, cpm, kp_time, total_early_kills, player_events


def parse_player_events(player_events):
    item_purchase = {}
    items = 0
    item_undo = {}
    undos = 0
    skill_up = []
    for i in range(len(player_events)):
        event_type = player_events[i]['type']
        data = player_events[i]
        if event_type == 'ITEM_PURCHASED':
            item_purchase[items] = [data['itemId'], data['timestamp']]
            items += 1
        elif event_type == 'ITEM_UNDO':
            item_undo[undos] = [data['beforeId'], data['timestamp']]
            undos += 1
        elif event_type == 'SKILL_LEVEL_UP':
            skill_up.append(data['skillSlot'])
        else:
            continue
    return item_purchase, item_undo, skill_up


def remove_undos(item_purchase, item_undo):
    to_delete = []
    if len(item_undo) > 0:
        for i in item_undo.keys():
            item = item_undo[i][0]
            time = item_undo[i][1]
            for j in item_purchase.keys():
                if item_purchase[j][0] == item and abs(time - item_purchase[j][1]) < 30000 and j not in to_delete:
                    to_delete.append(j)
                    break
    if len(to_delete) > 0:
        for key in to_delete:
            del item_purchase[key]
    new_item_purchase = []
    for key in item_purchase.keys():
        new_item_purchase.append(item_purchase[key][0])
    return new_item_purchase


def individual_data(gameinfo_json, timeline_json, jungler):
    info = game_info(gameinfo_json, jungler)
    info.extend(player_info(gameinfo_json, jungler, info[-3:]))
    gpm, xpm, cpm, kp_time, total_early_kills, player_events = timeline_info(timeline_json, jungler)
    item_purchase, item_undo, skill_up = parse_player_events(player_events)
    item_purchase = remove_undos(item_purchase, item_undo)
    # remember this will affect the order used in diff_values!!
    new_info = [gpm, xpm, cpm, kp_time, total_early_kills, item_purchase, skill_up]
    for i in new_info:
        info.append(i)
    return info


def diff_values(blue_info, red_info):
    # this is what will change if new_info is changed!
    try:
        cpm_diff_10 = blue_info[-5:-4][0][11] - red_info[-5:-4][0][11]
        gpm_diff_10 = blue_info[-7:-6][0][11] - red_info[-7:-6][0][11]
    except:
        cpm_diff_10 = 0
        gpm_diff_10 = 0
    try:
        cpm_diff_15 = blue_info[-5:-4][0][16] - red_info[-5:-4][0][16]
        gpm_diff_15 = blue_info[-7:-6][0][16] - red_info[-7:-6][0][16]
    except:
        cpm_diff_15 = 0
        gpm_diff_15 = 0

    info = [cpm_diff_10, cpm_diff_15, gpm_diff_10, gpm_diff_15]
    return info


def match_info(gameinfo_json, timeline_json, blue_jungler, red_jungler):
    blue_info = individual_data(gameinfo_json, timeline_json, blue_jungler)
    red_info = individual_data(gameinfo_json, timeline_json, red_jungler)
    diff_info = diff_values(blue_info, red_info)
    for i in range(len(diff_info)):
        blue_info.append(diff_info[i])
        red_info.append(-1 * diff_info[i])
    return blue_info, red_info


def match_run(matchId, region, tier, key, session):
    try:
        timeline_json = get_matchTimeline(matchId, region, key, session)
        gameinfo_json = get_gameInfo(matchId, region, key, session)
        blue_jungler = find_jungler(timeline_json, 'Blue')[1]
        red_jungler = find_jungler(timeline_json, 'Red')[1]
        blue_champ = find_champion(gameinfo_json, blue_jungler)
        red_champ = find_champion(gameinfo_json, red_jungler)
        blue_info, red_info = match_info(gameinfo_json, timeline_json, blue_jungler, red_jungler)
        blue_info.insert(0, blue_champ)
        red_info.insert(0, red_champ)
        blue_info.insert(1, tier)
        red_info.insert(1, tier)
        return [blue_info, red_info], matchId, region
    except:
        return 'Match Error', matchId, region


def create_df(data):
    column_names = ['champ_id', 'tier', 'game_duration', 'result', 'first_baron', 'first_dragon', 'first_herald',
                    'total_barons', 'total_dragons',
                    'total_rifts', 'spell1', 'spell2', 'items', 'kills', 'deaths', 'assists', 'kp', 'death_perc',
                    'damage_dealt',
                    'vision_score', 'damage_taken', 'gold_earnt', 'lane_minions', 'enemy_jungle', 'friendly_jungle',
                    'scuttles_killed', 'vision_wards', 'fb_parti', 'ft_parti', 'perks', 'perk_main', 'perk_second',
                    'runes',
                    'gpm', 'xpm', 'cpm', 'kp_time', 'total_early_kills', 'item_purchase', 'skill_up',
                    'cpm_diff_10', 'cpm_diff_15', 'gpm_diff_10', 'gpm_diff_15']

    df = pd.DataFrame(data, columns=column_names)
    return df

def get_args(matchIds, regions, tiers, key, session):
    keys = [key] * len(matchIds)
    sessions = [session] * len(matchIds)
    args = zip(matchIds, regions, tiers, keys, sessions)
    return args


def all_runs(matchIds, regions, tiers, key, session):
    args = get_args(matchIds, regions, tiers, key, session)
    data, fail_id, fail_region = [], [], []
    with Pool(processes=8) as p:
        for info, matchId, region in p.starmap(match_run, args):
            if info == 'Match Error':
                fail_id.append(matchId)
                fail_region.append(region)
            else:
                for i in info:
                    data.append(i)
    df = create_df(data)
    return df

