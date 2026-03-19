class CrawlerApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCrawlerStats();
        this.loadRecentCrawlers();
        
        setInterval(() => {
            this.loadCrawlerStats();
            this.loadRecentCrawlers();
        }, 5000);
    }

    bindEvents() {
        document.getElementById('crawlerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createCrawler();
        });

        document.getElementById('clearDataBtn').addEventListener('click', () => {
            this.clearAllData();
        });

        document.getElementById('refreshStatsBtn').addEventListener('click', () => {
            this.loadCrawlerStats();
            this.loadRecentCrawlers();
        });
    }

    async createCrawler() {
        const url = document.getElementById('origin').value.trim();
        const depth = parseInt(document.getElementById('maxDepth').value);

        this.showLoading(true);
        this.hideMessages();
        this.disableForm(true);

        try {
            const response = await fetch('/api/crawl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, depth: depth })
            });

            if (!response.ok) throw new Error("Failed to start crawler");

            const data = await response.json();
            
            this.showSuccess(`🎉 Crawler created successfully!<br><strong>ID:</strong> ${data.id}`);
            document.getElementById('origin').value = '';

            setTimeout(() => {
                this.loadRecentCrawlers();
                this.loadCrawlerStats();
                this.hideMessages();
            }, 2000);

        } catch (error) {
            this.showError(`Failed to create crawler: ${error.message}`);
        } finally {
            this.showLoading(false);
            this.disableForm(false);
        }
    }

    async loadRecentCrawlers() {
        const container = document.getElementById('recentCrawlers');
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 2rem; color: #5f6368;"><p>No crawlers found. Create your first crawler above!</p></div>';
                return;
            }

            const crawlersHTML = data.reverse().map(crawler => {
                const statusClass = crawler.status === 'running' ? 'status-active' : 'status-finished';
                return `
                    <div class="result-item">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <div>
                                <span style="font-weight: 600;">🍓 ${crawler.id.replace('crawler_', '')}</span>
                                <span class="status-badge ${statusClass}" style="margin-left: 1rem;">${crawler.status}</span>
                            </div>
                        </div>
                        <div class="result-meta">
                            <strong>Origin:</strong> <a href="${crawler.origin_url}" target="_blank">${crawler.origin_url}</a><br>
                            <strong>Max Depth:</strong> ${crawler.max_depth} | <strong>URLs Visited:</strong> ${crawler.visited_count || 0}
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = crawlersHTML;
        } catch (error) {
            container.innerHTML = `<div class="error">Failed to load recent crawlers.</div>`;
        }
    }

    async loadCrawlerStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            document.getElementById('statVisitedUrls').textContent = data.total_visited_urls;
            document.getElementById('statWordsInDb').textContent = data.total_words_in_database;
            document.getElementById('statActiveCrawlers').textContent = data.total_active_crawlers;
            document.getElementById('statTotalCrawlers').textContent = data.total_crawlers_created;

            document.getElementById('statQueueDepth').textContent = data.total_queue_depth || 0;
            
            const statusEl = document.getElementById('statSystemStatus');
            const statusText = data.system_status || "Stable";
            statusEl.textContent = statusText;

            if (statusText === "Stable") {
                statusEl.className = "stat-value status-ok";
            } else if (statusText === "Heavy Load") {
                statusEl.className = "stat-value status-warning";
            } else {
                statusEl.className = "stat-value status-danger";
            }

            const activeCrawlersElement = document.getElementById('statActiveCrawlers');
            if (data.total_active_crawlers > 0) {
                activeCrawlersElement.style.backgroundColor = '#28a745';
                activeCrawlersElement.style.color = 'white';
            } else {
                activeCrawlersElement.style.backgroundColor = '#e8f0fe';
                activeCrawlersElement.style.color = '#1a73e8';
            }
        } catch (error) {
            document.getElementById('statVisitedUrls').textContent = '!';
            document.getElementById('statWordsInDb').textContent = '!';
            document.getElementById('statActiveCrawlers').textContent = '!';
            document.getElementById('statTotalCrawlers').textContent = '!';
            document.getElementById('statQueueDepth').textContent = '!';
            document.getElementById('statSystemStatus').textContent = 'Error';
        }
    }

    async clearAllData() {
        if (!confirm('Are you sure you want to clear all history and stop running jobs?')) return;

        try {
            await fetch('/api/clear', { method: 'POST' });
            this.loadCrawlerStats();
            this.loadRecentCrawlers();
        } catch (error) {
            alert("Failed to clear data.");
        }
    }

    showLoading(show) { document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none'; }
    showSuccess(message) { 
        const div = document.getElementById('successMessage');
        div.innerHTML = message;
        div.style.display = 'block';
    }
    showError(message) {
        const div = document.getElementById('errorMessage');
        div.textContent = message;
        div.style.display = 'block';
    }
    hideMessages() {
        document.getElementById('successMessage').style.display = 'none';
        document.getElementById('errorMessage').style.display = 'none';
    }
    disableForm(disabled) {
        const inputs = document.getElementById('crawlerForm').querySelectorAll('input, button');
        inputs.forEach(input => input.disabled = disabled);
    }
}

const crawlerApp = new CrawlerApp();