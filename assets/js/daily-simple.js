// Daily Simple JS - Show articles by selected date

// Current selected date (default: today)
let currentDate = new Date().toISOString().split('T')[0];
let allArticles = [];

// Show loading state
const grid = document.getElementById('news-grid');
if (grid) {
    grid.innerHTML = `
        <div style="text-align:center;padding:60px 40px;">
            <div style="font-size:48px;margin-bottom:20px;">⏳</div>
            <p style="color:#666;">正在加载文章...</p>
        </div>
    `;
}

// Load everything when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM ready, loading data...');
    
    // Bind date navigation buttons with alert
    const prevBtn = document.getElementById('prev-date');
    const nextBtn = document.getElementById('next-date');
    const todayBtn = document.getElementById('today-btn');
    
    const showAlert = function() {
        alert('AI行业发展以月为单位，每日必读仅展示临近最新文档。');
    };
    
    if (prevBtn) prevBtn.addEventListener('click', showAlert);
    if (nextBtn) nextBtn.addEventListener('click', showAlert);
    if (todayBtn) todayBtn.addEventListener('click', showAlert);
    
    // Load all articles
    await loadAllArticles();
    updateDisplay();
});

// Load all articles from all categories
async function loadAllArticles() {
    console.log('Loading all articles...');
    
    allArticles = [];
    const categories = ['llm', 'autonomous', 'robotics', 'zhuoyu'];
    
    for (const cat of categories) {
        try {
            const url = `/data/articles/research/${cat}.json?t=${Date.now()}`;
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                data.forEach(article => {
                    article.category = cat;
                    allArticles.push(article);
                });
            }
        } catch (e) {
            console.error(`Error loading ${cat}:`, e);
        }
    }
    
    console.log(`Total loaded: ${allArticles.length} articles`);
}

// Filter articles by current date
function getArticlesByDate(date) {
    return allArticles.filter(article => {
        const articleDate = (article.published_at || '').split('T')[0];
        return articleDate === date;
    });
}

// Update display based on current date
function updateDisplay() {
    const todayArticles = getArticlesByDate(currentDate);
    
    // Update stats (only count today's articles)
    updateStats(todayArticles);
    
    // Render articles
    renderArticles(todayArticles);
    
    // Update header date
    const dateDisplay = document.getElementById('current-date');
    if (dateDisplay) {
        dateDisplay.textContent = currentDate;
    }
}

// Store total counts
let totalCounts = {
    total: 0,
    llm: 0,
    autonomous: 0,
    robotics: 0
};

// Update statistics
function updateStats(articles) {
    const statTotal = document.getElementById('stat-total');
    const statLlm = document.getElementById('stat-llm');
    const statAuto = document.getElementById('stat-autonomous');
    const statRobo = document.getElementById('stat-robotics');
    
    // Calculate counts
    totalCounts = {
        total: articles.length,
        llm: articles.filter(a => a.category === 'llm').length,
        autonomous: articles.filter(a => a.category === 'autonomous').length,
        robotics: articles.filter(a => a.category === 'robotics').length
    };
    
    // Display counts (今日资讯始终显示总数)
    if (statTotal) statTotal.textContent = totalCounts.total;
    if (statLlm) statLlm.textContent = totalCounts.llm;
    if (statAuto) statAuto.textContent = totalCounts.autonomous;
    if (statRobo) statRobo.textContent = totalCounts.robotics;
}

// Render articles
function renderArticles(articles) {
    const grid = document.getElementById('news-grid');
    if (!grid) return;
    
    if (articles.length === 0) {
        grid.innerHTML = `
            <div style="text-align:center;padding:60px;">
                <div style="font-size:48px;margin-bottom:20px;">📭</div>
                <h3>${currentDate} 暂无文章</h3>
                <p style="color:#999;">请选择其他日期</p>
            </div>
        `;
        return;
    }
    
    // Sort by quality score
    articles.sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0));
    
    grid.innerHTML = articles.map(article => {
        const title = article.title || '无标题';
        const summary = article.summary || '';
        const source = typeof article.source === 'object' ? article.source?.name : (article.source || '未知');
        let url = article.url;
        if (!url || url === '') {
            const searchQuery = encodeURIComponent(title);
            url = `https://www.baidu.com/s?wd=${searchQuery}`;
        }
        
        const categoryNames = {llm: 'AI', autonomous: '自动驾驶', robotics: '具身智能', zhuoyu: '卓驭科技'};
        const catName = categoryNames[article.category] || article.category;
        
        return `
        <div class="news-card" onclick="window.open('${url}', '_blank')">
            <div class="card-header">
                <span class="tag ${article.category}">${catName}</span>
                <span style="font-size:13px;color:#999;">${source}</span>
            </div>
            <h3 class="card-title">${title}</h3>
            <p class="card-summary">${summary}</p>
            <div style="text-align:right;">
                <span style="color:#667eea;font-size:13px;font-weight:500;">阅读全文 →</span>
            </div>
        </div>
        `;
    }).join('');
}

// Filter by category (from stat cards)
function filterByCategory(category) {
    const todayArticles = getArticlesByDate(currentDate);
    let filtered = todayArticles;
    
    if (category !== 'all') {
        filtered = todayArticles.filter(a => a.category === category);
    }
    
    renderArticles(filtered);
    
    // Update active state for stat cards
    document.querySelectorAll('.stat-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Add active class to clicked card
    const cardMap = {
        'all': 0,
        'llm': 1,
        'autonomous': 2,
        'robotics': 3
    };
    const cards = document.querySelectorAll('.stat-card');
    if (cards[cardMap[category]]) {
        cards[cardMap[category]].classList.add('active');
    }
}
