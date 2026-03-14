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
    
    // 保存数据
    window.articlesData = articles;
    
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
    
    // 数据已保存在 loadArticles 中
    
    grid.innerHTML = articles.map(article => {
        const url = article.original_url || article.url || '#';
        return `
        <div class="news-card" onclick="window.open('${url}', '_blank')" style="cursor:pointer;">
            <div class="card-header">
                <span class="tag ${article.category}">${article.category}</span>
                <span>${article.source?.name || '未知来源'}</span>
            </div>
            <h3 class="card-title">${article.title || '无标题'}</h3>
            <p class="card-summary">${article.summary || ''}</p>
            <div style="margin-top:10px;text-align:right;">
                <span style="color:#1890ff;font-size:14px;">阅读原文 →</span>
            </div>
        </div>
    `}).join('');
}

// 页面加载时执行
loadArticles();

// 绑定分类按钮点击事件 - 使用事件委托
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    
    console.log('Filter clicked:', btn.getAttribute('data-filter'));
    
    // 更新按钮状态
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    // 过滤文章
    const filter = btn.getAttribute('data-filter');
    // 如果文章还没加载完，等待一下
    if (!window.articlesData || window.articlesData.length === 0) {
        console.log('Articles not loaded yet, waiting...');
        setTimeout(() => filterByCategory(filter), 1500);
    } else {
        filterByCategory(filter);
    }
});

// 分类过滤功能
function filterByCategory(category) {
    console.log('Filtering by:', category);
    console.log('Articles data:', window.articlesData?.length);
    
    if (!window.articlesData || window.articlesData.length === 0) {
        console.log('No articles data yet');
        // 延迟重试
        setTimeout(() => filterByCategory(category), 500);
        return;
    }
    
    if (category === 'all' || !category) {
        renderArticles(window.articlesData);
    } else {
        const filtered = window.articlesData.filter(a => {
            console.log('Checking article category:', a.category, 'against:', category);
            return a.category === category;
        });
        console.log('Filtered count:', filtered.length);
        renderArticles(filtered);
    }
    
    // 更新标题
    const titles = {
        'llm': '大模型',
        'autonomous': '自动驾驶', 
        'robotics': '具身智能',
        'zhuoyu': '卓驭科技'
    };
    const titleEl = document.querySelector('.header-title h1');
    if (titleEl) {
        titleEl.textContent = titles[category] || '每日必读';
    }
}

// 检查 URL 参数
const urlParams = new URLSearchParams(window.location.search);
const cat = urlParams.get('cat');
if (cat) {
    // 延迟执行，等待文章加载完成
    setTimeout(() => filterByCategory(cat), 1500);
    
    // 更新按钮状态
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-filter') === cat) {
            btn.classList.add('active');
        }
    });
}
