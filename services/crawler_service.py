import time
import sqlite3
from utils.crawler_job import CrawlerJob

class CrawlerService:
    def __init__(self):
        self.crawlers = {}
        self.db_path = 'crawlberry.db'

    def _get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def start_crawler(self, origin_url, max_depth):
        thread_id = str(int(time.time() * 1000))
        crawler_id = f"crawler_{thread_id}"
        
        job = CrawlerJob(origin_url, max_depth)
        job.name = crawler_id
        self.crawlers[crawler_id] = job
        
        conn = self._get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO crawlers (id, origin_url, max_depth, status, start_time, visited_count) VALUES (?, ?, ?, ?, ?, ?)",
                  (crawler_id, origin_url, max_depth, "running", time.time(), 0))
        conn.commit()
        conn.close()
        
        job.start()
        return crawler_id

    def update_job_status(self, crawler_id):
        if crawler_id in self.crawlers:
            job = self.crawlers[crawler_id]
            status = "running" if job.is_alive() else "completed"
            visited_count = len(job.visited_urls)
            
            conn = self._get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE crawlers SET status = ?, visited_count = ? WHERE id = ?", (status, visited_count, crawler_id))
            conn.commit()
            conn.close()

    def get_status(self, crawler_id):
        self.update_job_status(crawler_id)
        
        conn = self._get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, origin_url, max_depth, status, start_time, visited_count FROM crawlers WHERE id = ?", (crawler_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            queue_size = self.crawlers[crawler_id].url_queue.qsize() if crawler_id in self.crawlers else 0
            return {
                "id": row[0],
                "origin_url": row[1],
                "max_depth": row[2],
                "status": row[3],
                "queue_size": queue_size,
                "visited_count": row[5]
            }
        return {"error": "Crawler not found"}

    def get_all_history(self):
        for cid in list(self.crawlers.keys()):
            self.update_job_status(cid)
            
        conn = self._get_db_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM crawlers ORDER BY start_time DESC")
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    def clear_history(self):
        for job in self.crawlers.values():
            job.is_running = False
            
        self.crawlers = {}
        
        conn = self._get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM crawlers")
        c.execute("DELETE FROM words")
        conn.commit()
        conn.close()

    def get_stats(self):
        total_created = 0
        total_words = 0
        total_visited = 0
        
        conn = self._get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM crawlers")
        total_created = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM words")
        total_words = c.fetchone()[0]
        
        c.execute("SELECT SUM(visited_count) FROM crawlers")
        sum_visited = c.fetchone()[0]
        if sum_visited:
            total_visited = sum_visited
            
        conn.close()

        active = sum(1 for job in self.crawlers.values() if job.is_alive())
        
        total_queue_depth = 0
        for cid, job in self.crawlers.items():
            if job.is_alive():
                total_queue_depth += job.url_queue.qsize()
        
        system_status = "Stable"
        if total_queue_depth > 1500:
            system_status = "Throttling (High Load)"
        elif total_queue_depth > 500:
            system_status = "Heavy Load"
                
        return {
            "total_crawlers_created": total_created,
            "total_active_crawlers": active,
            "total_words_in_database": total_words,
            "total_visited_urls": total_visited,
            "total_queue_depth": total_queue_depth,
            "system_status": system_status
        }