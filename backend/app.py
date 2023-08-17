from tinydb import TinyDB, Query, where
import json

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return jsonify(message='Hello, World!')

@app.route('/write', methods=['POST'])
def write_data():
    data = request.json

    table = data['table']
    data = data['data']

    db = TinyDB(table)
    db.insert(data)

    return jsonify(message='success')

@app.route('/query', methods=['POST'])
def query_data():
    data = request.json
    table = data['table']
    key = data['key']
    value = data['value']

    query = Query()
    db = TinyDB(table)
    results = db.search((query[key] == value))
    print(results)
    return jsonify(results)

@app.route('/search')
def search_data():
    table = request.args.get('table')
    key = request.args.get('key')
    queryString = request.args.get('query')
    
    query = Query()
    db = TinyDB(table)

    def search_func(value):
        return queryString in value

    results = db.search((query[key].test(search_func)))
    print(results)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
