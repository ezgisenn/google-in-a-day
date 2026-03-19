import os
import json

class SearchService:
    def __init__(self, storage_dir='storage'):
        self.storage_dir = storage_dir

    def search(self, query):
        words = [w.strip().lower() for w in query.replace(',', ' ').replace('.', ' ').split() if w.strip().isalpha()]
        if not words:
            return []

        results_map = {}

        for word in words:
            first_letter = word[0]
            file_path = os.path.join(self.storage_dir, f"{first_letter}.data")
            
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                            
                        try:
                            data = json.loads(line)
                            if data.get('word') == word:
                                url = data.get('url')
                                frequency = data.get('frequency', 0)
                                depth = data.get('depth', 0)
                                origin_url = data.get('origin_url')
                                
                                score = frequency / (depth + 1)
                                
                                if url not in results_map:
                                    results_map[url] = {
                                        'relevant_url': url,
                                        'origin_url': origin_url,
                                        'depth': depth,
                                        'score': 0
                                    }
                                
                                results_map[url]['score'] += score
                        except json.JSONDecodeError:
                            continue
            except IOError as e:
                print(f"Error reading file {file_path}: {e}")

        sorted_results = sorted(results_map.values(), key=lambda x: x['score'], reverse=True)
        
        final_triples = []
        for res in sorted_results:
            final_triples.append((res['relevant_url'], res['origin_url'], res['depth']))
            
        return final_triples