// Daily Simple JS - Clean Version

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
    await loadArticles();
});

// Load articles
async function loadArticles() {
    console.log('Loading articles...');
    
    let articles = [];
    const categories = ['llm', 'autonomous', 'robotics', 'zhuoyu'];
    
    for (const cat of categories) {
        try {
            const response = await fetch(`data/articles/research/${cat}.json?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`Loaded ${data.length} from ${cat}`);
                data.forEach(article => {
                    article.category = cat;
                    articles.push(article);
                });
            }
        } catch (e) {
            console.error(`Error loading ${cat}:`, e);
        }
    }
    
    console.log(`Total: ${articles.length} articles`);
    
    // Update stats
    const statTotal = document.getElementById('stat-total');
    const statLlm = document.getElementById('stat-llm');
    const statAuto = document.getElementById('stat-autonomous');
    const statRobo = document.getElementById('stat-robotics');
    
    if (statTotal) statTotal.textContent = articles.length;
    if (statLlm) statLlm.textContent = articles.filter(a => a.category === 'llm').length;
    if (statAuto) statAuto.textContent = articles.filter(a => a.category === 'autonomous').length;
    if (statRobo) statRobo.textContent = articles.filter(a => a.category === 'robotics').length;
    
    // Save and render
    window.articlesData = articles;
    renderArticles(articles);
}

// Render articles
function renderArticles(articles) {
    const grid = document.getElementById('news-grid');
    if (!grid) return;
    
    if (articles.length === 0) {
        grid.innerHTML = `
            <div style="text-align:center;padding:60px;">
                <div style="font-size:48px;margin-bottom:20px;">📭</div>
                <h3>暂无文章</h3>
                <p>请稍后再试</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = articles.map(article => {
        const url = article.url || '#';
        const title = article.title || '无标题';
        const summary = article.summary || '';
        const source = typeof article.source === 'object' ? article.source?.name : (article.source || '未知');
        
        return `
        <div class="news-card" onclick="window.open('${url}', '_blank')">
            <div class="card-header">
                <span class="tag ${article.category}">${article.category}</span>
                <span>${source}</span>
            </div>
            <h3 class="card-title">${title}</h3>
            <p class="card-summary">${summary}</p>
            <div style="margin-top:10px;text-align:right;">
                <span style="color:#1890ff;font-size:14px;">阅读原文 →</span>
            </div>
        </div>
        `;
    }).join('');
}

// Filter by category
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    const filter = btn.getAttribute('data-filter');
    if (!window.articlesData) {
        setTimeout(() => filterByCategory(filter), 500);
        return;
    }
    
    if (filter === 'all') {
        renderArticles(window.articlesData);
    } else {
        const filtered = window.articlesData.filter(a => a.category === filter);
        renderArticles(filtered);
    }
});

function filterByCategory(category) {
    if (!window.articlesData) return;
    
    if (category === 'all') {
        renderArticles(window.articlesData);
    } else {
        const filtered = window.articlesData.filter(a => a.category === category);
        renderArticles(filtered);
    }
}

// Toggle AI Big News
function toggleAIBigNews() {
    const content = document.getElementById('ai-big-news-content');
    if (content) {
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
}
