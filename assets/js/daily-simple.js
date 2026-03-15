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

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Page loaded, starting...');
    try {
        await loadAIBigNews();
    } catch (e) {
        console.error('AI Big News error:', e);
    }
    try {
        await loadArticles();
    } catch (e) {
        console.error('Articles error:', e);
    }
});

// 加载AI Big News - 简化版，直接显示静态内容
async function loadAIBigNews() {
    console.log('Loading AI Big News...');
    // AI Big News 内容已直接写在HTML中，无需JS加载
    console.log('AI Big News loaded from HTML');
}

// 渲染AI Big News
function renderAIBigNews(markdown) {
    console.log('Rendering AI Big News...');
    
    const briefContainer = document.getElementById('ai-big-news-brief');
    const listContainer = document.getElementById('ai-big-news-list');
    
    if (!briefContainer || !listContainer) {
        console.error('Containers not found!');
        return;
    }
    
    // 提取核心动态 - 更宽松的正则
    let coreText = '';
    const coreStart = markdown.indexOf('## 📋 核心动态');
    const trendStart = markdown.indexOf('## 🔮 趋势判断');
    if (coreStart >= 0 && trendStart > coreStart) {
        coreText = markdown.substring(coreStart + 20, trendStart).trim();
    }
    
    // 提取趋势判断
    let trendText = '';
    const focusStart = markdown.indexOf('## 📌 重点关注');
    if (trendStart >= 0 && focusStart > trendStart) {
        trendText = markdown.substring(trendStart + 20, focusStart).trim();
    }
    
    // 提取重点关注
    let focusText = '';
    const endStart = markdown.indexOf('---', focusStart);
    if (focusStart >= 0) {
        const endPos = endStart > focusStart ? endStart : markdown.length;
        focusText = markdown.substring(focusStart + 20, endPos).trim();
    }
    
    console.log('Extracted:', {core: coreText.length, trend: trendText.length, focus: focusText.length});
    
    // 渲染简报
    let briefHTML = '';
    if (coreText) {
        briefHTML += `<div class="ai-big-news-core"><h4>📋 核心动态</h4><p>${coreText.replace(/\n/g, '<br>')}</p></div>`;
    }
    if (trendText) {
        briefHTML += `<div class="ai-big-news-trend"><h4>🔮 趋势判断</h4><p><strong>${trendText}</strong></p></div>`;
    }
    briefContainer.innerHTML = briefHTML || '<p>暂无简报内容</p>';
    
    // 渲染重点关注（简化版）
    if (focusText) {
        // 简单按行分割显示
        const lines = focusText.split('\n').filter(l => l.trim());
        let focusHTML = '<div class="ai-big-news-focus">';
        lines.forEach((line, idx) => {
            if (line.match(/^\d+\./)) {
                focusHTML += `<div class="ai-big-news-item"><div class="ai-big-news-rank">${idx + 1}</div><div class="ai-big-news-content">${line.replace(/^\d+\.\s*/, '')}</div></div>`;
            }
        });
        focusHTML += '</div>';
        listContainer.innerHTML = focusHTML || '<p>暂无重点关注</p>';
    } else {
        listContainer.innerHTML = '<p>暂无重点关注</p>';
    }
    
    console.log('Rendered successfully');
}

function renderFocusItem(item) {
    return `
        <div class="ai-big-news-item">
            <div class="ai-big-news-rank">${item.rank}</div>
            <div class="ai-big-news-content">
                <div class="ai-big-news-meta">
                    <span class="ai-big-news-source">${item.source}</span>
                </div>
                <h3 class="ai-big-news-title">${item.title}</h3>
                ${item.summary ? `<p class="ai-big-news-summary">${item.summary}</p>` : ''}
            </div>
        </div>
    `;
}

// 回退到TOP10
async function loadTop10Fallback() {
    try {
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
        
        const top10 = allArticles
            .sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0))
            .slice(0, 10);
        
        renderTop10Fallback(top10);
    } catch (e) {
        console.error('Error loading TOP10 fallback:', e);
    }
}

function renderTop10Fallback(articles) {
    const briefContainer = document.getElementById('ai-big-news-brief');
    const listContainer = document.getElementById('ai-big-news-list');
    
    if (briefContainer) {
        briefContainer.innerHTML = `
            <div class="ai-big-news-core">
                <h4>📋 今日精选</h4>
                <p>今日共收录 ${articles.length} 篇高质量AI行业资讯，涵盖大模型、自动驾驶、具身智能等领域。</p>
            </div>
        `;
    }
    
    if (listContainer) {
        listContainer.innerHTML = articles.map((article, index) => {
            const title = article.title_zh || article.title || '无标题';
            const summary = article.summary_zh || article.summary || '';
            const shortSummary = summary.length > 60 ? summary.slice(0, 60) + '...' : summary;
            const score = (article.quality_score || 0).toFixed(1);
            
            return `
                <div class="ai-big-news-item" onclick="window.open('${article.url}', '_blank')" style="cursor:pointer;">
                    <div class="ai-big-news-rank">${index + 1}</div>
                    <div class="ai-big-news-content">
                        <div class="ai-big-news-meta">
                            <span class="ai-big-news-score">🔥${score}</span>
                        </div>
                        <h3 class="ai-big-news-title">${title}</h3>
                        <p class="ai-big-news-summary">${shortSummary}</p>
                    </div>
                </div>
            `;
        }).join('');
    }
}
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
        const url = article.url || '#';
        // 使用标题和摘要（数据中没有title_zh字段）
        const title = article.title || '无标题';
        const summary = article.summary || '';
        const sourceName = typeof article.source === 'object' ? article.source?.name : article.source || '未知来源';
        
        return `
        <div class="news-card" onclick="window.open('${url}', '_blank')" style="cursor:pointer;">
            <div class="card-header">
                <span class="tag ${article.category}">${article.category}</span>
                <span>${sourceName}</span>
            </div>
            <h3 class="card-title">${title}</h3>
            <p class="card-summary">${summary}</p>
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

// AI Big News toggle
function toggleAIBigNews() {
    const content = document.getElementById('ai-big-news-content');
    const toggle = document.getElementById('ai-big-news-toggle');
    
    if (content && toggle) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            toggle.querySelector('.toggle-text').textContent = '收起';
            toggle.querySelector('.toggle-icon').textContent = '▲';
        } else {
            content.style.display = 'none';
            toggle.querySelector('.toggle-text').textContent = '展开';
            toggle.querySelector('.toggle-icon').textContent = '▼';
        }
    }
}

// AI Big News toggle
function toggleAIBigNews() {
    const content = document.getElementById('ai-big-news-content');
    if (content) {
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
}
