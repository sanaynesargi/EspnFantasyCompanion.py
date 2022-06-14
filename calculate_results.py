from math import floor
from re import L
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
import sys

from plot_frame import plot_data, reshape_array
from write_image import draw_stats


if os.path.exists("./cookies.txt"):
    print("File Exists: Loading Values, delete file for new values")
    with open("cookies.txt", "r") as cookie_data:
        lines = cookie_data.readlines()
        lines[0] = lines[0].rstrip()
        swid_cookie, espn_s2_cookie = lines
else:
    with open("cookies.txt", "w") as cookie_data:
        print("Please type in your cookies, you can obtain these from a browsers devtools")
        swid_cookie = input("Please type your espn swid cookie here: ")
        espn_s2_cookie = input("Please type in your (longer) espn_s2 cookie here: ")
            
        cookie_data.write(swid_cookie)
        cookie_data.write("\n")
        cookie_data.write(espn_s2_cookie)
    
def sort_dict(dictionary, rev):
    new_dict = {}
    sorted_values = sorted(list(dictionary.values()), reverse=rev)

    for value in sorted_values:
        for key in dictionary.copy():
            if dictionary[key] == value:
                new_dict[key] = value
                del dictionary[key]

    return new_dict

def sort_list_of_dicts(lst, rev):
    scores = [item["Score"] for item in lst]
    scores = sorted(scores, reverse=rev)
    new_list = []

    for score in scores:
        for item in lst.copy():
            if item["Score"] == score:
                new_list.append(item)
                lst.remove(item)

    return new_list

def reverse_dict(dictionary):
    new_dict = {}
    keys = list(dictionary.keys())

    for i in range(len(keys)-1, 0, -1):
        new_dict[keys[i]] = dictionary[keys[i]]

    return new_dict

def main():
    league_id = 2064864194#410071727
    year = 2022
    url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?seasonId={year}"

    teams_req = requests.get(url, cookies = {
                         "swid": swid_cookie,
                         "espn_s2": espn_s2_cookie          
                     }, params = {
                     })

    stats_req = requests.get(url, cookies = {
                         "swid": swid_cookie,
                         "espn_s2": espn_s2_cookie          
                     }, params = {
                         "view": "mMatchup"
                     })

    raw_teams = teams_req.json()["teams"]
    teams = {}
    for raw_team in raw_teams:
        teams[raw_team["id"]] = raw_team["nickname"]
    # with open("teams.json", "r") as t:
    #     teams = json.load(t)
    #     teams = {int(k):v for k,v in teams.items()}

    data = stats_req.json() 


    dataframe = []
    for game in data["schedule"]:
        try:
            entry = [
                game['matchupPeriodId'],
                game['home']['teamId'], game['home']['totalPoints'],
                game['away']['teamId'], game['away']['totalPoints']
            ]
            dataframe.append(entry)
        except Exception as _:
            continue

    df = pd.DataFrame(dataframe, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2'])
    df['Type'] = ['Regular' if w<=14 else 'Playoff' for w in df['Week']]
    df.head()
    

    avgs = (df
        .filter(['Week', 'Score1', 'Score2'])
        .melt(id_vars=['Week'], value_name='Score')
        .groupby('Week')
        .mean()
        .reset_index()
    )
    avgs.head()

    def calculate_results(tm):

        # grab all games with this team
        df2 = df.query('Team1 == @tm | Team2 == @tm').reset_index(drop=True)

        weeks = df2["Week"].to_list()
        # move the team of interest to "Team1" column
        ix = list(df2['Team2'] == tm)
        df2.loc[ix, ['Team1','Score1','Team2','Score2']] = \
        df2.loc[ix, ['Team2','Score2','Team1','Score1']].values
        
        # add new score and win cols
        df2 = (df2
            .assign(Chg1 = df2['Score1'],
            Chg2 = df2['Score2'],
            Win  = df2['Score1'] > df2['Score2']
            )
        )
        df2.head()

        plt.plot(avgs["Week"].to_list(), avgs["Week"].to_list(), label="a")
        team1_diffs = df2["Chg1"].to_list()
        team_1_wins = df2["Win"].to_list()
        team2_diffs = df2["Chg2"].to_list()

        #print(len(weeks), len(team1_diffs), len(team_1_wins), len(team2_diffs))
        #print(weeks)
        flat_avgs = avgs.to_dict()["Score"]
        wins = 0
        #print(avgs)
        data = {
            "Week": [],
            "League Average": [],
            "Score1": [],
            "Score2": []
        }
        for i in range(len(weeks)):
            diff, win = floor(team1_diffs[i]), team_1_wins[i]
            diff2 = floor(team2_diffs[i])
            week = weeks[i]
            a = floor(flat_avgs[week - 1])
            
            wins += 1 if win else 0
            
            data["Week"].append(week)
            data["League Average"].append(a)
            data["Score1"].append(diff)
            data["Score2"].append(diff2)
        
        data["Team Record"] = f"{wins}-{14-wins}"

        return data

    def plot_score_per_week_graph():  
        all_teams = []
        for team in teams:
            try:
                team_data = pd.DataFrame(calculate_results(team))
                if team_data.empty:
                    continue
                all_teams.append(team_data) 
            except Exception as _:
                continue

        all_scores = []
        mids = all_teams[0]["League Average"].to_list()
        for team in all_teams:
            all_scores.append([])
            for i in range(len(team["Score1"])):
                score = team["Score1"][i]

                all_scores[-1].append(score)
        
        plot_data(all_scores, mids, teams)
        
    def calculate_scoring_stats():
        all_teams = []
        for team in teams:
            try:
                team_data = pd.DataFrame(calculate_results(team))
                if team_data.empty:
                    continue
                all_teams.append(team_data) 
            except Exception as _:
                continue

        all_scores = []
        for team in all_teams:
            all_scores.append([])
            for i in range(len(team["Score1"])):
                score = team["Score1"][i]
                all_scores[-1].append(score)

        shaped_scores = reshape_array(all_scores)
        keys = list(teams.keys())
        top_scorers = []
        bottom_scorers = []
        scores_for_weeks = []
        week = 1
        for scores_in_week in shaped_scores:
            scores_for_week = {}

            top_score = max(scores_in_week)
            bottom_score = min(scores_in_week)
            max_index = scores_in_week.index(top_score)
            min_index = scores_in_week.index(bottom_score)

            top_scorers.append({"Week": week, "Player": teams[keys[max_index]], "Score": top_score})
            bottom_scorers.append({"Week": week, "Player": teams[keys[min_index]], "Score": bottom_score})
            
            player_index = 0
            for score in scores_in_week:
                scores_for_week[teams[keys[player_index]]] = score
                player_index += 1
            

            ordered_scorers = sort_dict(scores_for_week, True)
            ordered_scorers["Week"] = week
            scores_for_weeks.append(ordered_scorers)

            week += 1

        def calculate_high_low_scores():

            sorted_top_scorers = sort_list_of_dicts(top_scorers, True)
            sc = sorted_top_scorers[0]["Score"]
            _high_score = [{"Player": sorted_top_scorers[0]["Player"], "Score": sc, "Week": sorted_top_scorers[0]["Week"]}]
            for s in sorted_top_scorers[1:]:
                if s["Score"] == sc:
                    _high_score.append({
                        "Player": s["Player"],
                        "Score": sc,
                        "Week": s["Week"]
                    })
                else:
                    break
            
            if len(_high_score) > 1:
                highest_score = _high_score
            else:
                highest_score = _high_score

            sorted_bt_scorers = sort_list_of_dicts(bottom_scorers, False)
            sc = sorted_bt_scorers[0]["Score"]
            _bt_score = [{"Player": sorted_bt_scorers[0]["Player"], "Score": sc, "Week": sorted_bt_scorers[0]["Week"]}]
            for s in sorted_bt_scorers[1:]:
                if s["Score"] == sc:
                    _bt_score.append({
                        "Player": s["Player"],
                        "Score": sc,
                        "Week": s["Week"]
                    })
                else:
                    break
            
            if len(_bt_score) > 1:
                lowest_score = _bt_score
            else:
                lowest_score = _bt_score

            return (highest_score, lowest_score)

        def calculate_most_freq_scorers():
            highest_score_apperances = {}
            lowest_score_apperances = {}
            most_frequent_top_scorer = None
            most_frequent_bottom_scorer = None

            for team in teams:
                highest_score_apperances[teams[team]] = 0
                lowest_score_apperances[teams[team]] = 0

            for score in top_scorers:
                person = score["Player"]
                highest_score_apperances[person] += 1

            for score in bottom_scorers:
                person = score["Player"]
                lowest_score_apperances[person] += 1

            sorted_top_apps, sorted_bottom_apps = sort_dict(highest_score_apperances, True), sort_dict(lowest_score_apperances, True)
            keys = list(sorted_top_apps.keys())
            max_apperances = sorted_top_apps[keys[0]]
            _most_freq_top = [keys[0]]
            for person in keys[1:]:
                if sorted_top_apps[person] == max_apperances:
                    _most_freq_top.append(person)
                else:
                    break

            if len(_most_freq_top) > 1:
                most_frequent_top_scorer = _most_freq_top
            else:
                most_frequent_top_scorer = _most_freq_top

            keys = list(sorted_bottom_apps.keys())
            max_apperances = sorted_bottom_apps[keys[0]]
            _most_freq_bt = [keys[0]]
            for person in keys[1:]:
                if sorted_bottom_apps[person] == max_apperances:
                    _most_freq_bt.append(person)
                else:
                    break

            if len(_most_freq_bt) > 1:
                most_frequent_bottom_scorer = _most_freq_bt
            else:
                most_frequent_bottom_scorer = _most_freq_bt

            return most_frequent_top_scorer, most_frequent_bottom_scorer

        def calculate_score_averages():
            player_score_totals = {}
            top_avg_scorers = None
            bottom_avg_scorers = None

            for team in teams:
                player_score_totals[teams[team]] = 0

            for week in scores_for_weeks:
                for person in week:
                    if person == "Week":
                        continue
                    player_score_totals[person] += week[person]

            for person in player_score_totals:
                score = player_score_totals[person]
                player_score_totals[person] = floor(score / 14)

            sorted_averages_top = sort_dict(player_score_totals, True)
            sorted_averages_bottom = reverse_dict(sorted_averages_top)

            keys = list(sorted_averages_top.keys())
            avg = sorted_averages_top[keys[0]]
            _top_avg = []
            for person in sorted_averages_top:
                if sorted_averages_top[person] == avg:
                    _top_avg.append(person)
                else:
                    break
            
            if len(_top_avg) > 1:
                top_avg_scorers = _top_avg
            else:
                top_avg_scorers = _top_avg
            
            keys = list(sorted_averages_bottom.keys())
            avg = sorted_averages_bottom[keys[0]]
            _bt_avg = []
            for person in sorted_averages_bottom:
                if sorted_averages_bottom[person] == avg:
                    _bt_avg.append(person)
                else:
                    break
            
            if len(_bt_avg) > 1:
                bottom_avg_scorers = _bt_avg
            else:
                bottom_avg_scorers = _bt_avg

            return (top_avg_scorers, bottom_avg_scorers, sorted_averages_top)

        def calculate_consistent_scorers(averages):
            most_consistent_scorer = None
            least_consistent_scorer = None
            score_deviations = {}

            for team in teams:
                score_deviations[teams[team]] = 0

            for person in scores_for_weeks[0]:
                if person == 'Week':
                    continue
                person_average = averages[person]
                for week in scores_for_weeks:
                    score = week[person]
                    score_deviations[person] += (score - person_average)

            for person in score_deviations:
                score_deviations[person] = abs(score_deviations[person])

            most_consistent = sort_dict(score_deviations, False)
            least_consistent = reverse_dict(most_consistent)

            keys = list(most_consistent.keys())
            _most_consistent = []
            sc =  most_consistent[keys[0]]
            for person in most_consistent:
                if most_consistent[person] == sc:
                    _most_consistent.append(person)
            
            if len(_most_consistent) > 1:
                most_consistent_scorer = _most_consistent
            else:
                most_consistent_scorer = _most_consistent[0]
            
            keys = list(least_consistent.keys())
            _least_consistent = []
            sc =  least_consistent[keys[0]]
            for person in least_consistent:
                if least_consistent[person] == sc:
                    _least_consistent.append(person)
            
            if len(_least_consistent) > 1:
                least_consistent_scorer = _least_consistent
            else:
                least_consistent_scorer = _least_consistent

            return (most_consistent_scorer, least_consistent_scorer)

        most_frequent_top_scorer, most_frequent_bottom_scorer = calculate_most_freq_scorers()
        highest_score_average, lowest_score_average, averages = calculate_score_averages()
        most_consistent_scorer, least_consistent_scorer = calculate_consistent_scorers(averages)
        highest_score, lowest_score = calculate_high_low_scores()

        return {
            "Most Frequent Top Scorer": most_frequent_top_scorer,
            "Most Frequent Bottom Scorer": most_frequent_bottom_scorer,
            "Highest Score Average": highest_score_average,
            "Lowest Score Average": lowest_score_average,
            "Most Consistent Scorer": most_consistent_scorer,
            "Least Consistent Scorer": least_consistent_scorer,
            "Averages": averages,
            "Highest Score": highest_score,
            "Lowest Score": lowest_score
        }
    
    def parse(game_dict):
        return \
            f"Week 7. {game_dict['Team1']} vs. {game_dict['Team2']} {game_dict['Score1']} - {game_dict['Score2']}"

    def calculate_game_stats():
        closest_game_overall = None
        top_closest_games = None
        games = []
        margins = []
        data = df.to_dict()
        for i in range(len(data["Week"])):
            games.append({
                "Week": data["Week"][i],
                "Team1": teams[data["Team1"][i]],
                "Team2": teams[data["Team2"][i]],
                "Score1": data["Score1"][i],
                "Score2": data["Score2"][i],
                "Margin": abs(data["Score2"][i] - data["Score1"][i])
            })
            margins.append(abs(data["Score2"][i] - data["Score1"][i]))

        sorted_games = []
        sorted_margins = sorted(margins)
        for margin in sorted_margins:
            for game in games[:]:
                if game["Margin"] == margin:
                    sorted_games.append(game)
                    games.remove(game)

        top_closest_games = sorted_games[:11]
        m = top_closest_games[0]["Margin"]
        _top_closest_games = []
        for game in top_closest_games:
            if game["Margin"] == m:
                _top_closest_games.append(game)

        if len(_top_closest_games) > 1:
            closest_game_overall = _top_closest_games
        else:
            closest_game_overall = _top_closest_games

        l_closest_games = sorted_games[-5:]

        return {
            "Closest Game": closest_game_overall, 
            "Top 3 Close Games": sorted_games[:4], 
            "Top 5 Blowouts": l_closest_games,
        }

    def pull_team_records():
        records = {}
        for team in teams:
            data = calculate_results(team)
            records[teams[team]] = data["Team Record"]

        return records

    stats = calculate_scoring_stats()
    records = pull_team_records()
    averages = stats["Averages"]
    
    for person in averages:
        averages[person] = f"{averages[person]} ({records[person]})"
    del stats["Averages"]

    draw_stats(averages, "Player Averages", "output/player_averages.png", 600, 900)
    draw_stats(stats, "League Statistics", "output/league_stats.png")
    #plot_score_per_week_graph()
    game_stats = calculate_game_stats()
    new_game_stats = {}
    for key in game_stats:
        new_game_stats[key] = []
        for game in game_stats[key]:
            new_game_stats[key].append(parse(game))
        
    draw_stats(new_game_stats, "Game Statistics", "output/game_stats.png", nl_on_list=True)

if __name__ == "__main__":
    main()


