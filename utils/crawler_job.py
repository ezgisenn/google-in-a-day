import threading
import queue
import urllib.request
import urllib.error
import time
import json
import os
from urllib.parse import urljoin
from html.parser import HTMLParser

# Global lock to prevent conflicts during file write operations
file_lock = threading.Lock()

class SimpleHTMLParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []
        self.text_content = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    full_url = urljoin(self.base_url, value)
                    if full_url.startswith('http'):
                        self.links.append(full_url)

    def handle_data(self, data):
        clean_data = data.strip()
        if clean_data:
            self.text_content.append(clean_data)

class CrawlerJob(threading.Thread):
    def __init__(self, origin_url, max_depth, max_queue_capacity=1000):
        super().__init__()
        self.origin_url = origin_url
        self.max_depth = max_depth
        self.max_queue_capacity = max_queue_capacity
        self.url_queue = queue.Queue()
        self.url_queue.put((origin_url, 0))
        self.visited_urls = set()
        self.is_running = True
        
        os.makedirs('storage', exist_ok=True)

    def fetch_url(self, url, retries=1):
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.getcode() == 200:
                        return response.read().decode('utf-8', errors='ignore')
            except (urllib.error.URLError, Exception) as e:
                if attempt < retries:
                    print(f"[{self.name}] Error occurred, retrying: {url} (Error: {e})")
                    time.sleep(2)
                else:
                    print(f"[{self.name}] URL skipped, unreachable: {url} (Error: {e})")
        return None

    def extract_words(self, text_list):
        words = {}
        for text in text_list:
            for word in text.replace(',', ' ').replace('.', ' ').split():
                clean_word = word.strip().lower()
                if clean_word.isalpha():
                    words[clean_word] = words.get(clean_word, 0) + 1
        return words

    def save_words_jsonl(self, words, url, depth):
        with file_lock:
            for word, frequency in words.items():
                first_letter = word[0]
                filename = f"storage/{first_letter}.data"
                data = {
                    "word": word,
                    "frequency": frequency,
                    "url": url,
                    "origin_url": self.origin_url,
                    "depth": depth
                }
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + "\n")

    def run(self):
        print(f"[{self.name}] Crawl started: {self.origin_url} (Max Depth: {self.max_depth})")
        
        while self.is_running and not self.url_queue.empty():
            url, current_depth = self.url_queue.get()
            
            if url in self.visited_urls:
                self.url_queue.task_done()
                continue
                
            if current_depth > self.max_depth:
                self.url_queue.task_done()
                continue

            print(f"[{self.name}] Crawling: {url} (Depth: {current_depth})")
            self.visited_urls.add(url)
            
            html_content = self.fetch_url(url)
            if html_content:
                parser = SimpleHTMLParser(url)
                parser.feed(html_content)
                
                words = self.extract_words(parser.text_content)
                self.save_words_jsonl(words, url, current_depth)
                
                for link in parser.links:
                    if link not in self.visited_urls:
                        while self.url_queue.qsize() >= self.max_queue_capacity:
                            print(f"[{self.name}] Queue capacity full ({self.max_queue_capacity}). Waiting for 5 seconds...")
                            time.sleep(5)
                        
                        self.url_queue.put((link, current_depth + 1))
                        
            self.url_queue.task_done()
            time.sleep(1)
            
        print(f"[{self.name}] Crawl completed.")