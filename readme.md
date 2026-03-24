# Project 1: Google in a Day (CrawlBerry 🍓)

## Overview
"CrawlBerry" is a minimalist, concurrent web crawler and real-time search engine built entirely from scratch using only Python's built-in libraries. It features a modern, strawberry-themed dashboard for managing concurrent crawling tasks, monitoring system health, and querying indexed data.

## Requirements
- Python 3.x
- **No external dependencies** (No Flask, Django, Requests, BeautifulSoup, Scrapy, etc.). The project strictly adheres to using native Python modules (`threading`, `urllib`, `html.parser`, `http.server`, `sqlite3`, `json`).

## How to Run
1. Open your terminal and navigate to the root directory of the project.
2. Start the server by running the following command:
   ```bash
   python app.py
  (Note: You may need to use python3 app.py depending on your system configuration).
3. The server will start and listen on port 5000.
4. Open your web browser and navigate to: http://localhost:5000

## Core Features & Architecture
**Concurrent Web Crawler:** Fetches and parses web pages in the background using Python's native threading and urllib, avoiding duplicate visits using an in-memory visited set.

**System Visibility & Back-Pressure Management:** Features a real-time dashboard monitoring critical metrics such as Queue Depth (Pending URLs), Active Crawlers, and System Load Status (Stable / Heavy Load / Throttling) to manage system load in a controlled way.

**Custom HTML Parser:** Extracts textual content and hyperlinks completely from scratch using Python's native html.parser.

**Live Search Engine:** Ranks search results based on a custom relevancy heuristic utilizing word frequency, exact match bonuses, and link depth penalties (Score = (Frequency * 10) + 1000 - (Depth * 5)). Search can run concurrently while the indexer is actively crawling.

**Modern Dashboard UI:** A clean, full-width responsive dashboard built strictly with pure HTML, CSS, and vanilla JS.

**Data Persistence:** Robust local database storage utilizing Python's built-in sqlite3 module for indexed data and crawler history, replacing flat files to maintain state securely, provide faster search queries, and clear data directly from the UI.