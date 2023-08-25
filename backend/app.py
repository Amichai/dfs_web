from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import source.scraper as scraper


app = Flask(__name__)
CORS(app)

DB_ROOT = 'DBs/'

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

@app.route('/runscraper', methods=['POST'])
def run_scraper():
    print("AA")
    sport = request.args.get('sport', '')
    scraper_name = request.args.get('scraper', '')
    print(sport, scraper_name)
    scrape_results = scraper.scrape(sport, scraper_name)

    print(scrape_results)
    table_name = "{}_{}".format(scraper_name, sport)
    # diff scrape results

    query = Query()
    db = TinyDB(DB_ROOT + table_name)

    # write this to our db
    for result in scrape_results:
        results = db.search((query['line_id'] == result['line_id']))
        import pdb; pdb.set_trace()
        # diff the most recent result with the current value
        # log this diff
        # update if diff exists
        write_to_db(table_name, result)

    return jsonify('success')

if __name__ == '__main__':
    app.run(debug=True)
