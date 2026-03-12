// ========================================
// Daily News Module - Load from JSON
// ========================================

let currentArticles = [];
let currentFilter = 'all';
let currentSearch = '';
let currentDate = getTodayString();

// Get today date string
function getTodayString() {
    return new Date().toISOString().split('T')[0];
}

// Format date for display
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
    return date.toLocaleDateString('zh-CN', options);
}

// Get category name
function getCategoryName(category) {
    const names = {
        'llm': '大模型',
        'autonomous': '自动驾驶',
        'robotics': '具身智能',
        'company': '公司动态',
        'product': '产品发布',
        'research': '技术研究',
        'investment': '投资动态',
        'policy': '政策法规'
    };
    return names[category] || category;
}

// Get source icon
function getSourceIcon(sourceType) {
    const icons = {
        'research_papers': '📄',
        'official': '🏢',
        'tech_media': '📰',
        'investment': '💰',
        'opensource': '🌟',
        'policy': '⚖️'
    };
    return icons[sourceType] || '📰';
}

// Load articles from JSON file
async function loadArticles(date = null) {
    const targetDate = date || getTodayString();
    currentDate = targetDate;
    
    // Update date display
    const dateEl = $('#current-date');
    if (dateEl) {
        dateEl.textContent = formatDate(targetDate);
    }
    
    // Update date picker
    const datePicker = $('#date-picker');
    if (datePicker) {
        datePicker.value = targetDate;
    }
    
    try {
        // Try to load from JSON file
        const year = targetDate.slice(0, 4);
        const month = targetDate.slice(5, 7);
        const response = await fetch(`data/articles/daily/${year}/${month}/${targetDate}.json`);
        
        if (response.ok) {
            currentArticles = await response.json();
        } else {
            // Fallback to sample data if file not found
            console.log('No data file found, using fallback');
            currentArticles = getFallbackData(targetDate);
        }
    } catch (error) {
        console.error('Error loading articles:', error);
        currentArticles = getFallbackData(targetDate);
    }
    
    // Update stats
    updateStats();
    
    // Update today count
    updateTodayCount(currentArticles.length);
    
    // Render highlights
    renderHighlights();
    
    // Render articles
    renderArticles();
    
    // Update last update time
    const lastUpdateEl = $('#last-update');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = new Date().toLocaleString('zh-CN');
    }
}

// Fallback data when JSON file not found
function getFallbackData(date) {
    // Return empty array or sample data based on date
    if (date === '2026-03-13') {
        return [
            {
                id: "2026-03-13-001",
                title: "GPT-5.4 系列模型发布，强化专业工作与智能体能力",
                summary: "OpenAI 正式推出 GPT-5.4 及 GPT-5.4 Pro 模型，面向 ChatGPT、API 及 Codex 平台同步上线。",
                content: "<p>OpenAI 今日正式推出 GPT-5.4 及 GPT-5.4 Pro 模型...</p>",
                source: { name: "品玩", type: "tech_media" },
                original_url: "https://www.pingwest.com/w/311850",
                publish_date: "2026-03-13",
                display_date: "3月13日",
                category: "llm",
                tags: ["OpenAI", "GPT-5.4"],
                importance: "high",
                is_featured: true
            }
        ];
    }
    return [];
}

// Update statistics
function updateStats() {
    const stats = {
        total: currentArticles.length,
        llm: currentArticles.filter(a => a.category === 'llm').length,
        autonomous: currentArticles.filter(a => a.category === 'autonomous').length,
        robotics: currentArticles.filter(a => a.category === 'robotics').length
    };
    
    const statTotal = $('#stat-total');
    const statLlm = $('#stat-llm');
    const statAutonomous = $('#stat-autonomous');
    const statRobotics = $('#stat-robotics');
    
    if (statTotal) statTotal.textContent = stats.total;
    if (statLlm) statLlm.textContent = stats.llm;
    if (statAutonomous) statAutonomous.textContent = stats.autonomous;
    if (statRobotics) statRobotics.textContent = stats.robotics;
}

// Render highlights
function renderHighlights() {
    const highlights = currentArticles.filter(a => a.is_featured).slice(0, 3);
    const container = $('#daily-highlights');
    
    if (!container) return;
    
    if (highlights.length === 0) {
        container.innerHTML = '<p>今日暂无精选内容</p>';
        return;
    }
    
    container.innerHTML = highlights.map((article, index) => {
        const icons = ['🔥', '🔄', '🚗', '🤖', '🧠'];
        const icon = icons[index % icons.length];
        return `<p>${icon} <strong>${article.title}</strong></p>`;
    }).join('');
}

// Generate news card HTML
function generateNewsCard(article) {
    const isBookmarked = Storage.isBookmarked(article.id);
    const sourceIcon = getSourceIcon(article.source?.type);
    
    return `
        <article class="news-card" data-id="${article.id}" data-category="${article.category}">
            <div class="card-header">
                <div class="card-tags">
                    <span class="tag ${article.category}">${getCategoryName(article.category)}</span>
                    ${article.importance === 'high' ? '<span class="tag" style="background:#ff6b6b;color:white">重要</span>' : ''}
                </div>
                <div class="card-time">${article.display_date}</div>
            </div>
            <div class="card-body">
                <h3 class="card-title">${article.title}</h3>
                <p class="card-summary">${article.summary}</p>
            </div>
            <div class="card-footer">
                <div class="card-source">
                    <div class="source-icon">${sourceIcon}</div>
                    <span>${article.source?.name || '未知来源'}</span>
                </div>
                <div class="card-actions">
                    <button class="btn-icon bookmark-btn ${isBookmarked ? 'active' : ''}" 
                            data-id="${article.id}"
                            onclick="event.stopPropagation(); toggleBookmark('${article.id}')">
                        ${isBookmarked ? '★' : '☆'}
                    </button>
                    <a href="${article.original_url || article.url}" target="_blank" class="btn btn-primary" onclick="event.stopPropagation()">阅读</a>
                </div>
            </div>
        </article>
    `;
}

// Render articles
function renderArticles() {
    const grid = $('#news-grid');
    if (!grid) return;
    
    // Filter articles
    const filtered = currentArticles.filter(article => {
        const matchFilter = currentFilter === 'all' || article.category === currentFilter;
        const matchSearch = !currentSearch || 
            article.title.toLowerCase().includes(currentSearch.toLowerCase()) ||
            article.summary.toLowerCase().includes(currentSearch.toLowerCase()) ||
            article.tags?.some(tag => tag.toLowerCase().includes(currentSearch.toLowerCase()));
        return matchFilter && matchSearch;
    });
    
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-title">暂无相关内容</div>
                <p>尝试切换分类或搜索其他关键词</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filtered.map(article => generateNewsCard(article)).join('');
    
    // Add click handlers
    grid.querySelectorAll('.news-card').forEach(card => {
        card.addEventListener('click', () => {
            const articleId = card.dataset.id;
            const article = currentArticles.find(a => a.id === articleId);
            if (article) {
                window.currentArticles = currentArticles;
                openModal(generateArticleDetail(article));
            }
        });
    });
}

// Generate article detail HTML
function generateArticleDetail(article) {
    const isBookmarked = Storage.isBookmarked(article.id);
    const sourceIcon = getSourceIcon(article.source?.type);
    
    return `
        <div class="article-header">
            <div class="article-tags" style="margin-bottom: 12px;">
                <span class="tag ${article.category}">${getCategoryName(article.category)}</span>
                ${article.tags?.map(tag => `<span class="tag" style="background:#f0f0f0;color:#666">${tag}</span>`).join('') || ''}
            </div>
            <h1 class="article-title">${article.title}</h1>
            <div class="article-meta">
                <div class="article-meta-item">
                    <span>${sourceIcon}</span>
                    <span>${article.source?.name || '未知来源'}</span>
                </div>
                <div class="article-meta-item">
                    <span>📅</span>
                    <span>${article.display_date}</span>
                </div>
                ${article.companies?.length ? `
                <div class="article-meta-item">
                    <span>🏢</span>
                    <span>${article.companies.join(', ')}</span>
                </div>
                ` : ''}
            </div>
        </div>
        <div class="article-body">
            ${article.content || `<p>${article.summary}</p>`}
        </div>
        <div class="article-actions">
            <a href="${article.original_url || article.url}" target="_blank" class="btn btn-primary">阅读原文</a>
            <button class="btn btn-secondary" onclick="toggleBookmarkFromModal('${article.id}')">
                <span id="modal-bookmark-icon">${isBookmarked ? '★' : '☆'}</span>
                <span id="modal-bookmark-text">${isBookmarked ? '已收藏' : '收藏'}</span>
            </button>
        </div>
    `;
}

// Initialize filter buttons
function initFilters() {
    $$('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderArticles();
        });
    });
}

// Initialize search
function initSearch() {
    const searchInput = $('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value;
            renderArticles();
        });
    }
}

// Initialize date picker
function initDatePicker() {
    const datePicker = $('#date-picker');
    if (datePicker) {
        // Set max date to today
        datePicker.max = getTodayString();
        
        datePicker.addEventListener('change', (e) => {
            if (e.target.value) {
                loadArticles(e.target.value);
            }
        });
    }
}

// Initialize load more
function initLoadMore() {
    const btn = $('#load-more-btn');
    if (btn) {
        btn.addEventListener('click', () => {
            showToast('历史数据加载功能开发中...');
        });
    }
}

// Initialize daily module
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    initFilters();
    initSearch();
    initDatePicker();
    initLoadMore();
});
