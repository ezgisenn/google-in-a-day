import sqlite3

class SearchService:
    def __init__(self, db_path='crawlberry.db'):
        self.db_path = db_path

    def search(self, query):
        words = [w.strip().lower() for w in query.replace(',', ' ').replace('.', ' ').split() if w.strip().isalpha()]
        if not words:
            return []

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        placeholders = ','.join('?' for _ in words)
        sql_query = f"""
            SELECT url, origin_url, depth, frequency 
            FROM words 
            WHERE word IN ({placeholders})
        """
        
        c.execute(sql_query, words)
        rows = c.fetchall()
        conn.close()

        results_map = {}

        for row in rows:
            url, origin_url, depth, frequency = row
            score = frequency / (depth + 1)
            
            if url not in results_map:
                results_map[url] = {
                    'relevant_url': url,
                    'origin_url': origin_url,
                    'depth': depth,
                    'score': 0
                }
            
            results_map[url]['score'] += score

        sorted_results = sorted(results_map.values(), key=lambda x: x['score'], reverse=True)
        
        final_triples = []
        for res in sorted_results:
            final_triples.append((res['relevant_url'], res['origin_url'], res['depth']))
            
        return final_triples