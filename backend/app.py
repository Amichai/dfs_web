from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import source.scraper as scraper
import time
import optimizer
import random
import utils


app = Flask(__name__)
CORS(app)

DB_ROOT = 'DBs/'

SCRAPE_OPERATIONS_TABLE = 'scrape_operations'

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


def _get_scraped_lines(scraper):
    query = Query()
    db = TinyDB(DB_ROOT + SCRAPE_OPERATIONS_TABLE)
    results = db.search(query['scraper'] == scraper)

    results_sorted = sorted(results, key=lambda a: a['scrape_time'])
    if len(results_sorted) == 0:
        return jsonify([])
    most_recent_scrape = results_sorted[-1]

    query2 = Query()
    db2 = TinyDB(DB_ROOT + scraper)

    # filter out any expired lines? 

    all_results = db2.search(query2['time'] == most_recent_scrape['scrape_time'])

    return all_results


@app.route('/getscrapedlines')
def get_scraped_lines():
    scraper = request.args.get('scraper', '')

    all_results = _get_scraped_lines(scraper)
    return jsonify(all_results)


@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    print(data)
    sport = data['sport']
    site = data['site']
    game_type = data['type']
    
    
    # read player prices/positions
    # get player projections
    # run optimizer

    query = Query()
    if sport == 'FIBA' and site == 'DK':
        db = TinyDB(DB_ROOT + "DKSlatePlayers_FIBA")
        scraped_lines = _get_scraped_lines('PrizePicks_FIBA')
        slate_players = db.search((query['slateId'] == '91834'))

        results = optimizer.optimize_FIBA_dk(slate_players, scraped_lines)
    elif sport == "NFL" and site == 'fd' and game_type == 'single_game':
        db = TinyDB(DB_ROOT + "FDSlatePlayers_" + sport)
        scraped_lines = _get_scraped_lines('PrizePicks_' + sport)
        slate_players = db.search((query['slateId'] == '93773'))
        name_stat_to_val, seen_names, seen_stats = optimizer.get_player_projection_data(scraped_lines, ['BUF', 'NYJ'])

        name_to_id = utils.name_to_player_id(slate_players)
        print(name_to_id)

        player_pool = optimizer.get_player_pool(name_stat_to_val, seen_names, slate_players)
        print(player_pool)
        results = optimizer.optimize_for_single_game_fd(player_pool, 10)
        for result in results:
            to_print = ["{}:{}".format(name_to_id[a[0]], a[0]) for a in result[0]]
            print(",".join(to_print) + "," + str(result[1]))
            # print(result)
        # optimizer.optimize_fd_single_game(slate_players, projection_data)

        # print(scraped_lines)
        # print('----------------')
        # print(slate_players)



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

    seen_ids = []
    # write this to our db
    for result in scrape_results:
        existing_results = db.search((query['line_id'] == result['line_id']))

        if len(existing_results) > 0:        
            sorted_by_time = sorted(existing_results, key=lambda a: a['time'])
            most_recent = sorted_by_time[-1]
            if most_recent['line_score'] != result['line_score']:
                print("Updating line score: {} -> {}".format(most_recent['line_score'], result['line_score']))
            else:
                document = Query()
                remove_result = db.remove(document['line_id'] == result['line_id'])
                print("removed document {} - {}".format(result['line_id'], remove_result))
                # figure out a strategy for purging old redudant lines
                pass

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
