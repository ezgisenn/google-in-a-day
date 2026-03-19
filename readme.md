# Project 1: Google in a Day

## Overview
"Google in a Day" is a minimalist web crawler and search engine built entirely from scratch using only Python's built-in libraries. It features a modern web interface for managing concurrent crawling tasks and querying indexed data.

## Requirements
- Python 3.x
- **No external dependencies** (No Flask, Django, Requests, BeautifulSoup, etc.). The project strictly adheres to using native Python modules.

## How to Run
1. Open your terminal and navigate to the root directory of the project.
2. Start the server by running the following command:
   \`\`\`bash
   python app.py
   \`\`\`
   *(Note: You may need to use `python3 app.py` depending on your system configuration).*
3. The server will start and listen on port 5000.
4. Open your web browser and navigate to: `http://localhost:5000`

## Features
- **Concurrent Web Crawler:** Fetches and parses web pages in the background using Python's `threading` and `urllib`.
- **Custom HTML Parser:** Extracts textual content and links using Python's native `html.parser`.
- **Intelligent Search:** Ranks search results based on a custom algorithm utilizing word frequency and link depth.
- **Modern UI:** A clean, responsive, strawberry-themed dashboard built with HTML, CSS, and vanilla JS.
- **Data Management:** File-based storage system that allows clearing history and resetting the database directly from the UI.