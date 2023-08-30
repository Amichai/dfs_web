from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import source.scraper as scraper
import time


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


@app.route('/getscrapedlines')
def get_scraped_lines():
    scraper = request.args.get('scraper', '')

    query = Query()
    db = TinyDB(DB_ROOT + SCRAPE_OPERATIONS_TABLE)
    results = db.search(query['scraper'] == scraper)

    results_sorted = sorted(results, key=lambda a: a['scrape_time'])
    most_recent_scrape = results_sorted[-1]

    query2 = Query()
    db2 = TinyDB(DB_ROOT + scraper)

    # filter out any expired lines? 

    all_results = db2.search(query2['time'] == most_recent_scrape['scrape_time'])

    return jsonify(all_results)


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
