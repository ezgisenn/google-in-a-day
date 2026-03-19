import json
import os
import time
import glob
from utils.crawler_job import CrawlerJob

class CrawlerService:
    def __init__(self, storage_dir='storage', history_file='history.json'):
        self.storage_dir = storage_dir
        self.history_path = os.path.join(storage_dir, history_file)
        self.crawlers = {}
        self.history = {}
        
        os.makedirs(self.storage_dir, exist_ok=True)
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                self.history = {}

    def save_history(self):
        try:
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def start_crawler(self, origin_url, max_depth):
        thread_id = str(int(time.time() * 1000))
        crawler_id = f"crawler_{thread_id}"
        
        job = CrawlerJob(origin_url, max_depth)
        job.name = crawler_id
        self.crawlers[crawler_id] = job
        
        self.history[crawler_id] = {
            "id": crawler_id,
            "origin_url": origin_url,
            "max_depth": max_depth,
            "status": "running",
            "start_time": time.time(),
            "visited_count": 0
        }
        self.save_history()
        
        job.start()
        return crawler_id

    def get_status(self, crawler_id):
        if crawler_id in self.crawlers:
            job = self.crawlers[crawler_id]
            self.history[crawler_id]["visited_count"] = len(job.visited_urls)
            if not job.is_alive():
                self.history[crawler_id]["status"] = "completed"
            self.save_history()
            
            return {
                "id": crawler_id,
                "status": self.history[crawler_id]["status"],
                "queue_size": job.url_queue.qsize(),
                "visited_count": len(job.visited_urls)
            }
        elif crawler_id in self.history:
            return self.history[crawler_id]
        
        return {"error": "Crawler not found"}

    def get_all_history(self):
        for cid, job in self.crawlers.items():
            self.history[cid]["visited_count"] = len(job.visited_urls)
            if not job.is_alive() and self.history[cid]["status"] == "running":
                self.history[cid]["status"] = "completed"
        self.save_history()
        return list(self.history.values())
        
    def clear_history(self):
        for job in self.crawlers.values():
            job.is_running = False
            
        self.history = {}
        self.crawlers = {}
        self.save_history()
        
        for f in glob.glob(os.path.join(self.storage_dir, "*.data")):
            try:
                os.remove(f)
            except:
                pass

    def get_stats(self):
        total_created = len(self.history)
        active = sum(1 for job in self.crawlers.values() if job.is_alive())
        
        total_words = 0
        for f in glob.glob(os.path.join(self.storage_dir, "*.data")):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    total_words += sum(1 for line in file)
            except:
                pass
                
        total_visited = 0
        for cid, info in self.history.items():
            if cid in self.crawlers and self.crawlers[cid].is_alive():
                total_visited += len(self.crawlers[cid].visited_urls)
            else:
                total_visited += info.get('visited_count', 0)
                
        return {
            "total_crawlers_created": total_created,
            "total_active_crawlers": active,
            "total_words_in_database": total_words,
            "total_visited_urls": total_visited
        }