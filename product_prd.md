# Product Requirements Document (PRD): Google in a Day

## 1. Product Overview
"Google in a Day" is a lightweight, dependency-free web crawler and search engine built entirely with Python's standard library. It aims to demonstrate core computer science concepts such as concurrent processing, web scraping, data indexing, and search ranking algorithms without relying on external frameworks.

## 2. Target Audience
- Students and educators exploring web crawling and search engine architecture.
- Developers looking for a minimal, easy-to-understand implementation of a search engine.

## 3. Core Features
### 3.1. Web Crawler
- **Concurrency:** Utilizes Python's `threading` module to run crawler jobs asynchronously in the background.
- **Parsing:** Implements a custom HTML parser using `html.parser` to extract text and hyperlink references.
- **Data Storage:** Stores extracted word frequencies and metadata (URL, depth) in local JSON Lines (`.data`) files categorized by the starting letter of the word.
- **Constraints:** Supports configurable maximum crawling depth and limits queue capacity to prevent memory overflow.

### 3.2. Search Engine
- **Indexing:** Reads from the local file-based storage to find matching keywords.
- **Ranking Algorithm:** Calculates a relevance score based on word frequency and the depth at which the word was found (Score = Frequency / (Depth + 1)).
- **Result Presentation:** Returns search results containing the relevant URL, origin URL, and depth.

### 3.3. User Interface
- **Crawler Dashboard:** A web interface to start new crawler jobs, monitor active/past jobs, and view system metrics (visited URLs, words indexed).
- **Search Interface:** A dedicated search page allowing users to query the indexed database and view ranked results with clickable links.

## 4. Technical Specifications
- **Backend:** Python 3.x (using `http.server`, `urllib`, `html.parser`, `threading`, `json`, `os`). No external libraries are permitted.
- **Frontend:** Pure HTML, CSS, and vanilla JavaScript.
- **Data Persistence:** Local file system (JSON format for history, JSON Lines for indexed data).