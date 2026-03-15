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
    
    // Show loading
    const grid = document.getElementById('news-grid');
    if (grid) {
        grid.innerHTML = '<div style="text-align:center;padding:40px;"><p>加载中...</p></div>';
    }
    
    let articles = [];
    const categories = ['llm', 'autonomous', 'robotics', 'zhuoyu'];
    
    for (const cat of categories) {
        try {
            // Try absolute path
            const url = `/data/articles/research/${cat}.json?t=${Date.now()}`;
            console.log('Fetching:', url);
            const response = await fetch(url);
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
    
    // If no articles, show error
    if (articles.length === 0) {
        if (grid) {
            grid.innerHTML = `
                <div style="text-align:center;padding:40px;color:#ff6b6b;">
                    <p>无法加载文章数据</p>
                    <p style="font-size:12px;color:#999;">请检查网络连接或刷新页面</p>
                </div>
            `;
        }
        return;
    }
    
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
        const title = article.title || '无标题';
        const summary = article.summary || '';
        
        // 处理source字段（可能是字符串或对象）
        let sourceName = '未知';
        if (article.source) {
            if (typeof article.source === 'object') {
                sourceName = article.source.name || article.source.toString();
            } else {
                sourceName = String(article.source);
            }
        }
        
        // 处理日期
        let dateStr = '';
        if (article.published_at) {
            dateStr = article.published_at.split('T')[0];
        } else if (article.publish_date) {
            dateStr = article.publish_date;
        }
        
        // 如果URL为空，使用百度搜索
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
                <span style="font-size:13px;color:#999;">${sourceName} · ${dateStr}</span>
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
