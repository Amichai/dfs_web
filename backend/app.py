from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import source.scraper as scraper
import time
import optimizer
import random
import datetime

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
    _get_scraped_lines_with_history(scraper)
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

    if site == 'FD':
        db = TinyDB(DB_ROOT + "FDSlatePlayers_" + sport)
    if site == 'DK':
        db = TinyDB(DB_ROOT + "DKSlatePlayers_" + sport)

    query = Query()
    slate_players = db.search((query['slateId'] == slateId))

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
    results, original_rosters, name_to_id = optimizer.reoptimize(sport, site, slate_id, rosters)

    for i in range(len(results)):
        result = results[i]
        if result == None:
            # roster is fully locked.
            import pdb; pdb.set_trace()
            results[i] = original_rosters[i]

    print(results)
    roster_data = []
    idx = 0
    for result in results:
        to_print = ["{}:{}".format(name_to_id[a.name], a.name) for a in result.players]
        print(",".join(to_print) + "," + str(result.value))
        roster_data.append({
            'players': to_print,
            'value': result.value,
            'cost': result.cost
        })

        idx += 1

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
    
    
    # read player prices/positions
    # get player projections
    # run optimizer

    query = Query()
    if sport == 'FIBA' and site == 'DK':
        db = TinyDB(DB_ROOT + "DKSlatePlayers_FIBA")
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_FIBA')
        slate_players = db.search((query['slateId'] == slate_id))

        results = optimizer.optimize_FIBA_dk(slate_players, scraped_lines)
    elif sport == "NFL" and site == 'fd' and game_type == 'single_game':

        db = TinyDB(DB_ROOT + "FDSlatePlayers_" + sport)
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_' + sport)

        query = Query()
        slate_players = db.search((query['slateId'] == slate_id))

        player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'fd')
        
        name_to_id = utils.name_to_player_id(slate_players)
        name_to_id = utils.map_pp_defense_to_fd_defense_name(name_to_id)

        # db = TinyDB(DB_ROOT + "slates")
        # query = Query()
        # upcoming_slates = db.search(query['sport'] == sport)
        # print(upcoming_slates[-1])

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
        db = TinyDB(DB_ROOT + "DKSlatePlayers_" + sport)
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_' + sport)
        query = Query()
        slate_players = db.search((query['slateId'] == slate_id))

        player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'dk')

        db = TinyDB(DB_ROOT + "slates")
        query = Query()
        upcoming_slates = db.search(query['sport'] == sport)
        # TODO: we should be filtering on slate id here
        print(upcoming_slates[-1])

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
        db = TinyDB(DB_ROOT + "FDSlatePlayers_" + sport)
        scraped_lines = data_utils.get_scraped_lines('PrizePicks_' + sport)

        query = Query()
        slate_players = db.search((query['slateId'] == slate_id))

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
        results, name_to_id = optimizer.optimize(sport, site, slate_id, roster_count, iter_count)

        roster_data = []
        for result in results:
            to_print = ["{}:{}".format(name_to_id[a.name], a.name) for a in result.players]
            print(",".join(to_print) + "," + str(result.value))
            roster_data.append({
                'players': to_print,
                'value': result.value,
                'cost': result.cost
            })


    utils.print_player_exposures(results)
    # return jsonify(roster_data)
    return jsonify([])

@app.route('/runscraper', methods=['POST'])
def run_scraper():
    sport = request.args.get('sport', '')
    scraper_name = request.args.get('scraper', '')
    print(sport, scraper_name)
    scrape_time = int(time.time())
    write_to_db(SCRAPE_OPERATIONS_TABLE, {
        "scrape_time": scrape_time,
        "scraper": "{}_{}".format(scraper_name, sport)
    })

    scrape_results = scraper.scrape(sport, scraper_name, scrape_time)

    table_name = "{}_{}".format(scraper_name, sport)

    query = Query()
    db = TinyDB(DB_ROOT + table_name)

    all_records = db.all()
    line_id_to_records = {}
    for record in all_records:
        line_id = record['line_id']
        if not line_id in line_id_to_records:
            line_id_to_records[line_id] = []
        line_id_to_records[line_id].append(record)

    seen_ids = []
    # write this to our db
    for result in scrape_results:
        line_id = result['line_id']
        existing_results = []
        if line_id in line_id_to_records:
            existing_results = line_id_to_records[line_id]

        if len(existing_results) > 0:        
            sorted_by_time = sorted(existing_results, key=lambda a: a['time'])
            most_recent = sorted_by_time[-1]
            most_recent_line_score = most_recent['line_score']
            line_score = result['line_score']
            name = result['name']
            stat = result['stat']
            if most_recent_line_score != line_score:
                print("{} Updating line score: {} -> {} {}".format(name, most_recent_line_score, stat, line_score))
            else:
                document = Query()
                # db.remove(document['line_id'] == result['line_id'])
                remove_result = db.remove(doc_ids=[most_recent.doc_id])
                # print("removed {}, {} - {}".format(name, most_recent['line_id'], remove_result))
        # if len(existing_results) == 0:
        #     print("New line: {}".format(result))

        # diff the most recent result with the current value
        # log this diff
        # update if diff exists
        line_id = result['line_id']
        if line_id in seen_ids:
            print("Seen this id already: {}".format(line_id))
            continue
        
        seen_ids.append(line_id)
        write_to_db(table_name, result)

    return jsonify('success')

if __name__ == '__main__':
    app.run(debug=True)
