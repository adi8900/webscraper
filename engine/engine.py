import json
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
        data = json.loads(post_data)
        url = data['url']
        data_types = data.get('data_type', ['all'])
        result = worker.run_multiprocessing_task(url, data_types)

        client = MongoClient('mongodb://mongodb:27017')
        db = client['web_scraper']
        collection = db['data']

        unique_data = {
            'url': result['url'],
            'emails': list(set(result.get('emails', []))),
            'phone_numbers': list(set(result.get('phone_numbers', []))),
            'images': list(set(result.get('images', []))),
            'videos': list(set(result.get('videos', []))),
            'nips': list(set(result.get('nips', []))),
            'subpages': result.get('subpages', [])
        }

        collection.insert_one(unique_data)

        self._set_response()
        self.wfile.write(json.dumps(unique_data, cls=JSONEncoder).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()