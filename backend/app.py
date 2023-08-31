from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import source.scraper as scraper
import time
import utils
from name_mapper import name_mapper
from optimizer import DK_NBA_Optimizer


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

def normalize_name(name):
    if name in name_mapper:
        name = name_mapper[name]

    return name

def get_player_projection(scraped_lines, name):
    matched_players = [a for a in scraped_lines if a['name'].strip() == name]
    if len(matched_players) == 0:
        print("Missing projection for: ", name)
        return 0

    try:
        pts = [a for a in matched_players if a['stat'] == 'Points'][0]['line_score']
        # rebounds = [a for a in matched_players if a['stat'] == 'Rebounds'][0]['line_score']
    except:
        print("insufficient data for: ", name)
        return 0
    
    return float(pts)
    # return float(pts) + float(rebounds) * 1.5


@app.route('/optimize', methods=['POST'])
def optimize():
    # read player prices/positions
    # get player projections
    # run optimizer

    scraped_lines = _get_scraped_lines('PrizePicks_FIBA')
    # print(scraped_lines)
    print("testing testing 123")

    dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    query = Query()
    db = TinyDB(DB_ROOT + "DKSlatePlayers_FIBA")
    slate_players = db.search((query['slateId'] == '91834'))

    # print(results)
    by_position = {}
    for slate_player in slate_players:
        # print(slate_player)
        name = slate_player['name'].strip()
        name = normalize_name(name)
        positions = slate_player['position'].split('/')
        salary = slate_player['salary']
        team = slate_player['team']
        projection = get_player_projection(scraped_lines, name)
        if projection == 0:
            continue

        all_position = []

        for position in positions:
            # if not position in by_position:
            #     by_position[position] = []
            positions_extended = dk_positions_mapper[position]
            for pos in positions_extended:
                if not pos in all_position:
                    all_position.append(pos)
        
        for pos in all_position:
            if not pos in by_position:
                by_position[pos] = []
            
            by_position[pos].append(utils.Player(name, position, salary, team, projection))

    print(by_position)
    
    optimizer = DK_NBA_Optimizer()

    results = optimizer.optimize(by_position, None)

    print(results)

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
                print("Updating line score: {} -> {}")
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
