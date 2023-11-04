from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import source.scraper as scraper
import time
import optimizer
import random
import datetime

import pyperclip


import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
import data_utils
import utils

app = Flask(__name__)
CORS(app)

DB_ROOT = 'DBs/'

SCRAPE_OPERATIONS_TABLE = 'scrape_operations'
SLATES_TABLE = 'slates'

def write_to_db(table, data):
    db = TinyDB(DB_ROOT + table)
    db.insert(data)

    return True

@app.route('/')
def hello_world():
    return jsonify(message='Hello, World!')

@app.route('/writeslate', methods=['POST'])
def write_slate():
    data = request.json
    print(data)
    sport = data['sport']
    slate_id = data['slateId']
    site = data['site']
    date = data['date']
    columns = data['columns']
    player_data = data['playerData']
    game_data = data['gameData']

    data_utils.write_slate(sport, slate_id, site, date, columns, player_data, game_data)

    return jsonify(message='success')

@app.route('/write', methods=['POST'])
def write_data():
    data = request.json

    table = data['table']
    data = data['data']

    write_to_db(table, data)

    return jsonify(message='success')

# match on key value
@app.route('/query', methods=['POST'])
def query_data():
    data = request.json
    table = data['table']
    key = data['key']
    value = data['value']

    query = Query()
    db = TinyDB(DB_ROOT + table)
    results = db.search((query[key] == value))

    return jsonify(results)

# check if a string contains
@app.route('/search')
def search_data():
    table = request.args.get('table')
    key = request.args.get('key')
    queryString = request.args.get('query')
    
    query = Query()
    db = TinyDB(DB_ROOT + table)

    def search_func(value):
        return queryString in value

    results = db.search((query[key].test(search_func)))
    print(results)
    return jsonify(results)


def _get_scraped_lines_with_history(scraper):
    query = Query()
    db = TinyDB(DB_ROOT + SCRAPE_OPERATIONS_TABLE)
    results = db.search(query['scraper'] == scraper)

    results_sorted = sorted(results, key=lambda a: a['scrape_time'])
    if len(results_sorted) == 0:
        return []

    most_recent_scrape = results_sorted[-1]

    query = Query()
    db = TinyDB(DB_ROOT + scraper)
    results = db.search(query['time'] == most_recent_scrape['scrape_time'])

    all_start_times = []
    results_with_history = {}
    for result in results:
        start_time = result['start_time']
        if not start_time in all_start_times:
            all_start_times.append(start_time)

        name = result['name']
        stat = result['stat']
        name_stat = "{}_{}".format(name, stat)
        results_with_history[name_stat] = {
            'current': result,
            'changes': []
        }
    
    for start_time in all_start_times:
        query = Query()
        results = db.search(query['start_time'] == start_time)
        for result in results:
            name = result['name']
            stat = result['stat']
            name_stat = "{}_{}".format(name, stat)
            if not name_stat in results_with_history:
                results_with_history[name_stat] = {
                    'current': None,
                    'changes': []
                }
            
            time = result['time']
            val = result['line_score']
            results_with_history[name_stat]['changes'].append((val, time))

    return results_with_history


@app.route('/getscrapedlineswithhistory')
def get_scraped_lines_with_history():
    scraper = request.args.get('scraper', '')

    all_results = _get_scraped_lines_with_history(scraper)
    return jsonify(all_results)


@app.route('/getscrapedlines')
def get_scraped_lines():
    scraper = request.args.get('scraper', '')

    all_results = data_utils.get_scraped_lines(scraper)
    # _get_scraped_lines_with_history(scraper)
    return jsonify(all_results)

@app.route('/getslates')
def get_slates():
    cutoffDate = request.args.get('cutoffDate', '')
    db = TinyDB(DB_ROOT + SLATES_TABLE)
    results = db.all()
    print(cutoffDate)
    print(results)
    filtered_results = [a for a in results if a['date'] >= cutoffDate]

    return jsonify(filtered_results)


@app.route('/getSlatePlayers')
def getSlatePlayers():
    slateId = request.args.get('slateId', '')
    site = request.args.get('site', '')
    sport = request.args.get('sport', '')
    print(slateId)

    slate_players, _ = data_utils.get_slate_players(sport, site, slateId, utils.date_str())

    return jsonify(slate_players)

@app.route('/reoptimize', methods=['POST'])
def reoptimize():
    data = request.json
    sport = data['sport']
    site = data['site']
    game_type = data['type']
    slate_id = data['slateId']
    roster_count = int(data['rosterCount'])
    iter_count = int(data['iterCount'])
    rosters = data['rosters']

    excluded_players = data.get('excludePlayers', '')
    print(excluded_players)
    excluded_names = excluded_players.split(',')
    results, original_rosters, name_to_id = optimizer.reoptimize(sport, site, slate_id, rosters, excluded_names)

    for i in range(len(results)):
        result = results[i]
        if result == None:
            # roster is fully locked.
            results[i] = original_rosters[i]

    print(results)
    roster_data = []
    save_to_clipboard = ''
    idx = 0
    for result in results:
        to_print_data = ["{}".format(name_to_id[a.name], a.name) for a in result.players]
        to_print = ",".join(to_print_data) + "," + str(result.value)
        print(to_print)
        save_to_clipboard += to_print + '\n'
        roster_data.append({
            'players': to_print,
            'value': result.value,
            'cost': result.cost
        })

        idx += 1
    
    print("Copied to clipboard")
    pyperclip.copy(save_to_clipboard)

    utils.print_player_exposures(results)

    return jsonify([])
    


@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    print(data)
    sport = data['sport']
    site = data['site']
    game_type = data['type']
    slate_id = data['slateId']
    roster_count = int(data['rosterCount'])
    iter_count = int(data['iterCount'])

    excluded_players = data.get('excludePlayers', '')
    print(excluded_players)
    excluded_names = excluded_players.split(',')

    # read player prices/positions
    # get player projections
    # run optimizer

    query = Query()
    if sport == 'FIBA' and site == 'DK':
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_FIBA')
        slate_players, _ = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())

        results = optimizer.optimize_FIBA_dk(slate_players, scraped_lines)
    elif sport == "NFL" and site == 'fd' and game_type == 'single_game':
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_' + sport)

        slate_players, _ = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())

        player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'fd')
        
        name_to_id = utils.name_to_player_id(slate_players)
        name_to_id = utils.map_pp_defense_to_fd_defense_name(name_to_id)

        teams = []
        for player in player_pool:
            team = player[4]
            if not team in teams:
                teams.append(team)

        optimizer.print_slate(slate_players, player_pool, 'fd', teams)

        #find a way to validate my player pool!

        print(name_to_id)

        print(player_pool)
        results = optimizer.optimize_for_single_game_fd(player_pool, roster_count)
        for result in results:
            to_print = ["{}:{}".format(name_to_id[a[0]], a[0]) for a in result[0]]
            print(",".join(to_print) + "," + str(result[1]) + "," + str(60000 - result[2]))
    elif sport == "NFL" and site == 'dk' and game_type == 'single_game':
        pass
            # print(result)
        # optimizer.optimize_fd_single_game(slate_players, projection_data)

        # print(scraped_lines)
        # print('----------------')
        # print(slate_players)
    elif sport == "NFL" and site == 'dk' and game_type == '':
        print("DK NFL", slate_id)
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_' + sport)

        slate_players, game_data = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())

        player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'dk')

        # TODO: we should be filtering on slate id here
        print(game_data)

        # optimizer.print_slate_old(slate_players, player_pool, upcoming_slates[-1]['slate'], 'dk')

        name_to_id = utils.name_to_player_id(slate_players)
        name_to_id = utils.map_pp_defense_to_dk_defense_name(name_to_id)


        # print(player_pool)
        results = optimizer.optimize_dk_nfl(player_pool)
        for result in results:
            to_print = ["{}".format(name_to_id[a.name]) for a in result.players]
            print(",".join(to_print) + "," + str(result.value))
        pass
    elif sport == "NFL" and site == 'fd' and game_type == '':
        print("FD NFL", slate_id)
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_' + sport)

        slate_players, _ = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())

        player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'fd')

        db = TinyDB(DB_ROOT + "slates")
        query = Query()
        upcoming_slates = db.search(query['sport'] == sport)
        # # TODO: we should be filtering on slate id here
        # print(upcoming_slates[-1])

        # optimizer.print_slate_old(slate_players, player_pool, upcoming_slates[-1]['slate'], 'fd')
        # optimizer.print_slate(slate_players, player_pool, 'fd', [])
        name_to_id = utils.name_to_player_id(slate_players)
        name_to_id = utils.map_pp_defense_to_fd_defense_name(name_to_id)

        results = optimizer.optimize_fd_nfl(player_pool, roster_count, iter_count)

        roster_data = []
        for result in results:
            to_print = ["{}:{}".format(name_to_id[a.name], a.name) for a in result.players]
            print(",".join(to_print) + "," + str(result.value))
            roster_data.append({
                'players': to_print,
                'value': result.value,
                'cost': result.cost
            })
    elif sport == "NBA" and site == 'fd' and game_type == '':
        results, name_to_id = optimizer.optimize(sport, site, slate_id, roster_count, iter_count, excluded_names)

        roster_data = []
        save_to_clipboard = ''
        for result in results:
            to_print_data = ["{}:{}".format(name_to_id[a.name], a.name) for a in result.players]
            to_print = ",".join(to_print_data) + "," + str(result.value)
            print(to_print)
            save_to_clipboard += to_print + '\n'
            roster_data.append({
                'players': to_print,
                'value': result.value,
                'cost': result.cost
            })
        print("Copied to clipboard")
        pyperclip.copy(save_to_clipboard)

    elif sport == "NBA" and site == 'dk' and game_type == '':
        results, name_to_id = optimizer.optimize(sport, site, slate_id, roster_count, iter_count, excluded_names)

        roster_data = []
        save_to_clipboard = ''
        for result in results:
            to_print_data = ["{}".format(name_to_id[a.name], a.name) for a in result.players]
            to_print = ",".join(to_print_data) + "," + str(result.value)
            print(to_print)
            save_to_clipboard += to_print + '\n'
            roster_data.append({
                'players': to_print,
                'value': result.value,
                'cost': result.cost
            })
        
        print("Copied to clipboard")
        pyperclip.copy(save_to_clipboard)



    utils.print_player_exposures(results)
    return jsonify(roster_data)

@app.route('/runscraper', methods=['POST'])
def run_scraper():
    sport = request.args.get('sport', '')
    scraper_name = request.args.get('scraper', '')

    # TODO reimplement
    initial_projections = data_utils.get_current_projections(sport)

    print(sport, scraper_name)

    today_date =  str(datetime.datetime.now()).split(' ')[0]
    file = open('DBs/{}/{}_{}.txt'.format(sport, scraper_name, today_date), 'a')
    file_most_recent = open('DBs/{}/{}_{}_current.txt'.format(sport, scraper_name, sport), 'w')
    
    scrape_time = str(datetime.datetime.now()).split('.')[0]
    utils.write_to_files('t:' + str(scrape_time) + '\n', file, file_most_recent)

    # })

    scrape_results = scraper.scrape(sport, scraper_name, scrape_time)


    utils.write_to_files(",".join([str(a) for a in scrape_results[0].keys()]) + '\n', file, file_most_recent)

    for result in scrape_results:
        utils.write_to_files(",".join([str(a) for a in result.values()]) + '\n', file, file_most_recent)

        # write_to_db(table_name, result)

    file.close()
    file_most_recent.close()
    
    new_projections = data_utils.get_current_projections(sport)

    for key in set(initial_projections.keys()).union(new_projections.keys()):
        initial_p = initial_projections.get(key)
        new_p = new_projections.get(key)
        if initial_p == None:
            print("New projection: {} – {}".format(key, new_p))
        if new_p == None:
            print("Lost projection: {} - {}".format(key, initial_p))
        if initial_p != None and new_p != None and float(new_p) != float(initial_p) and abs(float(new_p) - float(initial_p)) > 0.6:
            print("Projection diff: {}, initial: {}, new: {}".format(key, initial_p, new_p))


    return jsonify('success')

if __name__ == '__main__':
    app.run(debug=True)
