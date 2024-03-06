import requests
import time
import random


def get_team_by_id(team_id):
    base_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{team_id}"
    team_data = dict()
    try:
        overall_results = requests.get(base_url).json()['team']
    except KeyError:
        overall_results = {'displayName': "Failed to get league Teams Summary"}
    try:
        team_data['rank'] = overall_results['rank']
        team_data['color'] = overall_results['color']
        team_data['alt_color'] = overall_results['alternateColor']
        team_data['name'] = overall_results['displayName']
        team_data['abbreviation'] = overall_results['abbreviation']
        team_data['overall_stats'] = overall_results['record']['items'][0]
        team_data['away_stats'] = overall_results['record']['items'][2]
        return True, team_data
    except KeyError:
        name = overall_results['displayName']
        return False, name


def get_algorithm_variables(team_data):
    overall_ot_weight = int(
        (team_data['overall_stats']['stats'][1]['value'] - team_data['overall_stats']['stats'][0]['value']) * 100)
    away_ot_weight = int(
        (team_data['away_stats']['stats'][1]['value'] - team_data['away_stats']['stats'][0]['value']) * 100)
    ot_weight = away_ot_weight * 2 - overall_ot_weight
    win_percentage = ("leagueWinPercent", 0)
    games_behind = ("gamesBehind", 0)
    overall_point_differential = ("pointDifferential", 0)
    overall_wins = ("wins", 0)

    away_point_diff = ("pointDifferential", 0)
    away_win_percentage = ("leagueWinPercent", 0)
    away_games_behind = ("gamesBehind", 0)
    away_wins = ("wins", 0)
    overall_check_variables_list = [win_percentage, games_behind, overall_point_differential, overall_wins]
    away_check_variables_list = [away_wins, away_win_percentage, away_games_behind, away_point_diff]
    overall_check_variables_list = get_values_from_stat_list(team_data['overall_stats']['stats'],
                                                             overall_check_variables_list)
    away_check_variables_list = get_values_from_stat_list(team_data['away_stats']['stats'], away_check_variables_list)

    combined_color_num = int(combine_hex_values({team_data['color']: 1.0, team_data['alt_color']: 0.5}), 16)
    random.seed(combined_color_num)
    disperse = random.randint(0, 100)

    return ot_weight, away_ot_weight, disperse, overall_check_variables_list, away_check_variables_list


def get_values_from_stat_list(stat_list, check_variables):
    input_var_list = dict()
    for i in stat_list:
        for check_var, input_var in check_variables:
            if i['name'] == check_var:
                input_var_list[check_var] = int(i['value'])
    return input_var_list


def calculate_win_weight(team_data):
    ot_weight, away_ot_weight, color_disperse, overall_stats, away_stats = get_algorithm_variables(team_data)
    return THE_ALGORITHM(overall_stats, away_stats, color_disperse, ot_weight, away_ot_weight)


def THE_ALGORITHM(overall_stats, away_stats, disperse, ot_weight, away_ot_weight):
    win_weight = (((overall_stats['gamesBehind'] / overall_stats['wins']) + ot_weight + overall_stats['leagueWinPercent'] +
                   overall_stats['pointDifferential']) * ((away_stats['pointDifferential'] + away_stats['leagueWinPercent']
                                                           + away_stats['gamesBehind'] + away_stats[
                                                            'wins']) ^ away_ot_weight) / disperse)
    random.seed(win_weight)
    win_weight = random.randint(0, 1000) + win_weight
    return win_weight


def calc_winner(team1, team2):
    print(team1, team2)
    random.seed(team1 + team2 / team1 - team2 * team1)
    team1_percent = random.randint(0, int(team1 + team2)) + team1
    team2_percent = random.randint(0, int(team1 + team2)) + team2

    if team1_percent > team2_percent:
        print("Team1 Winner")
        return team1
    print("Team2 Winner")
    return team2


def combine_hex_values(d):
    d_items = sorted(d.items())
    tot_weight = sum(d.values())
    red = int(sum([int(k[:2], 16) * v for k, v in d_items]) / tot_weight)
    green = int(sum([int(k[2:4], 16) * v for k, v in d_items]) / tot_weight)
    blue = int(sum([int(k[4:6], 16) * v for k, v in d_items]) / tot_weight)
    zpad = lambda x: x if len(x) == 2 else '0' + x
    return zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])


if __name__ == '__main__':
    start_time = time.time()
    ranked_teams = list()
    amount = 2990
    for i in range(1, 50):
        result_code, team_data = get_team_by_id(i)
        if result_code:
            ranked_teams.append(team_data)
    end_time = time.time()
    if ranked_teams:
        for i in range(0, len(ranked_teams), 2):
            print(ranked_teams[i]['name'])
            print(ranked_teams[i+1]['name'])
            team1 = calculate_win_weight(ranked_teams[i])
            team2 = calculate_win_weight(ranked_teams[i+1])
            print(calc_winner(team1, team2))
