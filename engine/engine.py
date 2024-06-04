import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from bson import ObjectId
import worker
from pymongo import MongoClient

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        task = json.loads(post_data)

        combined_result = process_task(task)

        self._set_response()
        self.wfile.write(json.dumps(combined_result, cls=JSONEncoder).encode('utf-8'))

def distribute_task_to_slave(task):
    slave_url = "http://192.168.2.190:8000/task"
    response = requests.post(slave_url, json=task)
    return response.json()

def process_task(task):
    slave_result = distribute_task_to_slave(task)
    local_result = worker.run_multiprocessing_task(task['url'], task.get('data_types', ['all']))
    combined_result = combine_results(local_result, slave_result)
    store_results(combined_result)
    return combined_result

def make_hashable(d):
    return {k: tuple(v) if isinstance(v, list) else v for k, v in d.items()}

def combine_results(local_result, slave_result):
    combined_subpages = []

    for subpage in local_result.get('subpages', []):
        combined_subpages.append(frozenset(make_hashable(subpage).items()))

    for subpage in slave_result.get('subpages', []):
        combined_subpages.append(frozenset(make_hashable(subpage).items()))

    unique_subpages_set = set(combined_subpages)
    unique_subpages = [dict(item) for item in unique_subpages_set]

    combined_result = {
        'url': local_result['url'],
        'emails': list(set(local_result.get('emails', []) + slave_result.get('emails', []))),
        'phone_numbers': list(set(local_result.get('phone_numbers', []) + slave_result.get('phone_numbers', []))),
        'images': list(set(local_result.get('images', []) + slave_result.get('images', []))),
        'videos': list(set(local_result.get('videos', []) + slave_result.get('videos', []))),
        'nips': list(set(local_result.get('nips', []) + slave_result.get('nips', []))),
        'subpages': unique_subpages
    }

    return combined_result

def store_results(results):
    client = MongoClient('mongodb://mongodb:27017')
    db = client['web_scraper']
    collection = db['data']

    combined_subpages = [frozenset(subpage.items()) for subpage in results.get('subpages', [])]
    unique_subpages_set = set(combined_subpages)
    unique_subpages = [dict(item) for item in unique_subpages_set]

    unique_data = {
        'url': results['url'],
        'emails': list(set(results.get('emails', []))),
        'phone_numbers': list(set(results.get('phone_numbers', []))),
        'images': list(set(results.get('images', []))),
        'videos': list(set(results.get('videos', []))),
        'nips': list(set(results.get('nips', []))),
        'subpages': unique_subpages
    }

    collection.insert_one(unique_data)

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
