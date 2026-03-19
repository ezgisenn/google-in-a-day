class SearchApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
    }

    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) return;

        this.showLoading(true);
        this.hideError();
        this.hideResults();

        try {
            const response = await fetch('/api/search?q=' + encodeURIComponent(query));
            const data = await response.json();
            this.displayResults(data);
        } catch (error) {
            this.showError("Search failed to execute.");
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsInfo = document.getElementById('resultsInfo');
        const resultsList = document.getElementById('resultsList');

        if (data.results && data.results.length > 0) {
            resultsInfo.innerHTML = `<div style="margin-bottom: 1rem; color: #5f6368;">Found ${data.results.length} results</div>`;
            
            resultsList.innerHTML = data.results.map(res => `
                <div class="result-item">
                    <a href="${res[0]}" target="_blank" class="result-url">${res[0]}</a>
                    <div class="result-meta">
                        Origin: ${res[1]} | Depth Found: ${res[2]}
                    </div>
                </div>
            `).join('');
        } else {
            resultsInfo.innerHTML = '';
            resultsList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #5f6368;">
                    <h3>No results found</h3>
                    <p>Try different keywords or check if the content has been crawled.</p>
                </div>
            `;
        }
        resultsContainer.style.display = 'block';
    }

    showLoading(show) { document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none'; }
    showError(message) {
        const div = document.getElementById('errorMessage');
        div.textContent = message;
        div.style.display = 'block';
    }
    hideError() { document.getElementById('errorMessage').style.display = 'none'; }
    hideResults() { document.getElementById('resultsContainer').style.display = 'none'; }
}

const searchApp = new SearchApp();