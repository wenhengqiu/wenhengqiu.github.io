// 简化版 daily.js - 直接显示研究模块文章

// 页面加载时执行
// 显示加载状态
const grid = document.getElementById('news-grid');
if (grid) {
    grid.innerHTML = `
        <div style="text-align:center;padding:60px 40px;">
            <div style="font-size:48px;margin-bottom:20px;animation:spin 1s linear infinite;">⏳</div>
            <p style="color:#666;">正在加载文章...</p>
        </div>
        <style>@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }</style>
    `;
}

// 加载TOP10和文章
loadTop10();
loadArticles();

// 加载TOP10
async function loadTop10() {
    try {
        // 加载所有文章
        const categories = ['llm', 'autonomous', 'robotics', 'zhuoyu'];
        let allArticles = [];
        
        for (const cat of categories) {
            try {
                const response = await fetch(`data/articles/research/${cat}.json`);
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
        
        // 按质量分排序取前10
        const top10 = allArticles
            .sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0))
            .slice(0, 10);
        
        renderTop10(top10);
    } catch (e) {
        console.error('Error loading TOP10:', e);
    }
}

// 渲染TOP10
function renderTop10(articles) {
    const container = document.getElementById('top10-list');
    if (!container) return;
    
    if (articles.length === 0) {
        container.innerHTML = '<p class="top10-empty">暂无文章</p>';
        return;
    }
    
    const categoryNames = {
        'llm': 'AI',
        'autonomous': '自动驾驶',
        'robotics': '具身智能',
        'zhuoyu': '卓驭科技'
    };
    
    const categoryColors = {
        'llm': '#1890ff',
        'autonomous': '#52c41a',
        'robotics': '#722ed1',
        'zhuoyu': '#fa8c16'
    };
    
    container.innerHTML = articles.map((article, index) => {
        const rank = index + 1;
        const title = article.title_zh || article.title || '无标题';
        const summary = article.summary_zh || article.summary || '';
        const shortSummary = summary.length > 60 ? summary.slice(0, 60) + '...' : summary;
        const score = (article.quality_score || 0).toFixed(1);
        const category = article.category || 'llm';
        const categoryName = categoryNames[category] || category;
        const categoryColor = categoryColors[category] || '#1890ff';
        
        return `
            <div class="top10-item" onclick="window.open('${article.url}', '_blank')" style="cursor:pointer;">
                <div class="top10-rank">${rank}</div>
                <div class="top10-content">
                    <div class="top10-meta">
                        <span class="top10-category" style="background:${categoryColor}20;color:${categoryColor};padding:2px 8px;border-radius:4px;font-size:12px;margin-right:8px;">${categoryName}</span>
                        <span class="top10-score" style="color:#ff6b6b;font-weight:600;">🔥${score}</span>
                    </div>
                    <h3 class="top10-title" style="margin:8px 0;font-size:16px;color:#333;">${title}</h3>
                    <p class="top10-summary" style="margin:0;font-size:13px;color:#666;line-height:1.5;">${shortSummary}</p>
                </div>
            </div>
        `;
    }).join('');
}

// TOP10折叠/展开
function toggleTop10() {
    const section = document.getElementById('top10-section');
    const content = document.getElementById('top10-content');
    const toggleText = document.querySelector('.toggle-text');
    const toggleIcon = document.querySelector('.toggle-icon');
    
    if (section.classList.contains('collapsed')) {
        section.classList.remove('collapsed');
        content.style.display = 'block';
        toggleText.textContent = '收起';
        toggleIcon.textContent = '▲';
        localStorage.setItem('top10-collapsed', 'false');
    } else {
        section.classList.add('collapsed');
        content.style.display = 'none';
        toggleText.textContent = '展开';
        toggleIcon.textContent = '▼';
        localStorage.setItem('top10-collapsed', 'true');
    }
}

// 页面加载时恢复折叠状态
document.addEventListener('DOMContentLoaded', () => {
    const isCollapsed = localStorage.getItem('top10-collapsed') === 'true';
    if (isCollapsed) {
        const section = document.getElementById('top10-section');
        const content = document.getElementById('top10-content');
        const toggleText = document.querySelector('.toggle-text');
        const toggleIcon = document.querySelector('.toggle-icon');
        
        if (section && content) {
            section.classList.add('collapsed');
            content.style.display = 'none';
            if (toggleText) toggleText.textContent = '展开';
            if (toggleIcon) toggleIcon.textContent = '▼';
        }
    }
});

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
        grid.innerHTML = `
            <div style="text-align:center;padding:60px 40px;">
                <div style="font-size:48px;margin-bottom:20px;">📭</div>
                <h3 style="color:#333;margin-bottom:10px;">暂无相关文章</h3>
                <p style="color:#666;">该分类暂时没有文章，去看看其他分类吧</p>
                <button onclick="filterByCategory('all')" style="margin-top:20px;padding:10px 20px;background:#1890ff;color:white;border:none;border-radius:4px;cursor:pointer;">查看全部文章</button>
            </div>
        `;
        return;
    }
    
    // 数据已保存在 loadArticles 中
    
    // 渲染文章
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
