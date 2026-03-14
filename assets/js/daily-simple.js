// 简化版 daily.js - 直接显示研究模块文章

async function loadArticles() {
    console.log('Loading articles...');
    
    let articles = [];
    
    // 直接从研究模块加载
    const categories = ['llm', 'autonomous', 'robotics', 'zhuoyu'];
    
    for (const cat of categories) {
        try {
            const response = await fetch(`data/articles/research/${cat}.json`);
            if (response.ok) {
                const data = await response.json();
                console.log(`Loaded ${data.length} articles from ${cat}`);
                
                // 处理每篇文章
                data.forEach(article => {
                    // 确保 source 是对象
                    if (typeof article.source === 'string') {
                        article.source = { name: article.source, type: 'tech_media' };
                    }
                    article.category = cat;
                    articles.push(article);
                });
            }
        } catch (e) {
            console.error(`Error loading ${cat}:`, e);
        }
    }
    
    console.log(`Total articles: ${articles.length}`);
    
    // 更新统计
    document.getElementById('stat-total').textContent = articles.length;
    document.getElementById('stat-llm').textContent = articles.filter(a => a.category === 'llm').length;
    document.getElementById('stat-autonomous').textContent = articles.filter(a => a.category === 'autonomous').length;
    document.getElementById('stat-robotics').textContent = articles.filter(a => a.category === 'robotics').length;
    
    // 渲染文章
    renderArticles(articles);
}

function renderArticles(articles) {
    const grid = document.getElementById('news-grid');
    if (!grid) return;
    
    if (articles.length === 0) {
        grid.innerHTML = '<p style="text-align:center;padding:40px;">暂无文章</p>';
        return;
    }
    
    grid.innerHTML = articles.map(article => `
        <div class="news-card" onclick="openArticle('${article.id}')">
            <div class="card-header">
                <span class="tag ${article.category}">${article.category}</span>
                <span>${article.source?.name || '未知来源'}</span>
            </div>
            <h3 class="card-title">${article.title || '无标题'}</h3>
            <p class="card-summary">${article.summary || ''}</p>
        </div>
    `).join('');
}

// 页面加载时执行
loadArticles();
