from tinydb import TinyDB, Query, where
import itertools
import requests
import json
import time


import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')

from optimizer_library import NFL_Optimizer
import optimizer
import utils


DB_ROOT = 'DBs/'

# BACKTESTER
# OPTIMIZE AND REOPTIMIZE OVER THE COURSE OF A NIGHT
# EXPLORE DIFFERENT PROJECTION NORMALIZATION TECHNIQUES


def optimize():
    sport = 'NBA'
    site = 'fd'
    slate_id = '96674'
    roster_count = 50
    iter_count = 11
    
    results, name_to_id = optimizer.optimize_historical(sport, site, slate_id, roster_count, iter_count, [], '2023-11-28')
    
    print(results)


def get_stats():
    url = "https://api-nba-v1.p.rapidapi.com/games"

    date = "2023-11-28"
    querystring = {"date":date}

    headers = {
        "X-RapidAPI-Key": "180328e9admsh876015c8399ed57p1be573jsnc0b7d2bb42ac",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
          
    print(response.json())
    return
    
    all_game_ids = [a['id'] for a in response.json()['response']]
    
    player_to_fantasy_points = {}
    
    for game_id in all_game_ids:
        print(game_id)
        url = "https://api-nba-v1.p.rapidapi.com/players/statistics"

        querystring = {"game": game_id}

        headers = {
            "X-RapidAPI-Key": "180328e9admsh876015c8399ed57p1be573jsnc0b7d2bb42ac",
            "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
        }
        
        time.sleep(10)

        response = requests.get(url, headers=headers, params=querystring)
        
        response_json = response.json()
  
        if not 'response' in response_json:
            print(response_json)
            continue
        for result in response_json['response']:
            name = result['player']['firstname'] + ' ' + result['player']['lastname']
            points = result['points']
            rebounds = result['totReb']
            assists = result['assists']
            steals = result['steals']
            blocks = result['blocks']
            turnovers = result['turnovers']
            
            if points == None or rebounds == None or assists == None or steals == None or blocks == None or turnovers == None:
                import pdb; pdb.set_trace()
                continue
            fdp = points + rebounds * 1.2 + assists * 1.5 + steals * 3 + blocks * 3 - turnovers
            player_to_fantasy_points[name] = fdp
            
            print(name, fdp)
        
    path = 'DBs/NBA/results/{}.json'.format(date)
    file  = open(path, 'a')
    file.write(json.dumps(player_to_fantasy_points))
        
get_stats()