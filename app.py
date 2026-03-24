import json
import os
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from services.crawler_service import CrawlerService
from services.search_service import SearchService

# Initialize Database
def init_db():
    conn = sqlite3.connect('crawlberry.db')
    c = conn.cursor()
    # Crawlers history table
    c.execute('''CREATE TABLE IF NOT EXISTS crawlers
                 (id TEXT PRIMARY KEY, origin_url TEXT, max_depth INTEGER, status TEXT, start_time REAL, visited_count INTEGER)''')
    # Indexed words table
    c.execute('''CREATE TABLE IF NOT EXISTS words
                 (word TEXT, frequency INTEGER, url TEXT, origin_url TEXT, depth INTEGER)''')
    # Index for faster searching
    c.execute('''CREATE INDEX IF NOT EXISTS idx_word ON words(word)''')
    conn.commit()
    conn.close()

init_db()

crawler_service = CrawlerService()
search_service = SearchService()

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.path = '/demo/crawler.html'
            return super().do_GET()
        elif parsed_path.path.startswith('/demo/'):
            return super().do_GET()
            
        elif parsed_path.path == '/api/status':
            query = parse_qs(parsed_path.query)
            crawler_id = query.get('id', [None])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if crawler_id:
                status = crawler_service.get_status(crawler_id)
            else:
                status = crawler_service.get_all_history()
                
            self.wfile.write(json.dumps(status).encode())
            
        elif parsed_path.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            stats = crawler_service.get_stats()
            self.wfile.write(json.dumps(stats).encode())
            
        elif parsed_path.path == '/api/search':
            query = parse_qs(parsed_path.query)
            q = query.get('query', query.get('q', ['']))[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            results = search_service.search(q)
            self.wfile.write(json.dumps({"results": results}).encode())
            
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/crawl':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            origin_url = data.get('url')
            max_depth = int(data.get('depth', 1))
            
            crawler_id = crawler_service.start_crawler(origin_url, max_depth)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": crawler_id, "status": "started"}).encode())
            
        elif parsed_path.path == '/api/clear':
            crawler_service.clear_history()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "cleared"}).encode())
            
        else:
            self.send_error(404, "Not Found")

def run_server(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server is running on port {port}...")
    print(f"Open http://localhost:{port} in your browser to view the UI.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    run_server(3600)