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

// 加载AI Big News和文章
loadAIBigNews();
loadArticles();

// 加载AI Big News
async function loadAIBigNews() {
    try {
        // 获取今天的日期
        const today = new Date().toISOString().split('T')[0];
        
        // 尝试加载今天的AI Big News
        const response = await fetch(`data/articles/daily/${today}_executive.md`);
        
        if (response.ok) {
            const markdown = await response.text();
            renderAIBigNews(markdown);
        } else {
            // 如果没有今天的，尝试加载最新的
            const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
            const yResponse = await fetch(`data/articles/daily/${yesterday}_executive.md`);
            
            if (yResponse.ok) {
                const markdown = await yResponse.text();
                renderAIBigNews(markdown);
            } else {
                // 回退到加载高质量文章
                loadTop10Fallback();
            }
        }
    } catch (e) {
        console.error('Error loading AI Big News:', e);
        loadTop10Fallback();
    }
}

// 渲染AI Big News
function renderAIBigNews(markdown) {
    // 解析Markdown
    const lines = markdown.split('\n');
    
    let coreDynamics = '';
    let trendJudgment = '';
    let keyFocus = [];
    
    let inCoreDynamics = false;
    let inTrendJudgment = false;
    let inKeyFocus = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        if (line.includes('## 📋 核心动态')) {
            inCoreDynamics = true;
            inTrendJudgment = false;
            inKeyFocus = false;
            continue;
        }
        if (line.includes('## 🔮 趋势判断')) {
            inCoreDynamics = false;
            inTrendJudgment = true;
            inKeyFocus = false;
            continue;
        }
        if (line.includes('## 📌 重点关注')) {
            inCoreDynamics = false;
            inTrendJudgment = false;
            inKeyFocus = true;
            continue;
        }
        if (line.startsWith('## ') || line.startsWith('---')) {
            inCoreDynamics = false;
            inTrendJudgment = false;
            inKeyFocus = false;
            continue;
        }
        
        if (inCoreDynamics && line.trim()) {
            coreDynamics += line + '\n';
        }
        if (inTrendJudgment && line.trim()) {
            trendJudgment += line + '\n';
        }
        if (inKeyFocus && line.trim().match(/^\d+\./)) {
            // 解析重点关注条目
            const match = line.match(/^\d+\.\s+\*\*(.+?)\*\s*—\s*\*(.+?)\*/);
            if (match) {
                const nextLine = lines[i + 1] || '';
                const summaryMatch = nextLine.match(/^\s*>\s*(.+)/);
                keyFocus.push({
                    title: match[1],
                    source: match[2],
                    summary: summaryMatch ? summaryMatch[1] : ''
                });
            }
        }
    }
    
    // 渲染核心动态和趋势
    const briefContainer = document.getElementById('ai-big-news-brief');
    if (briefContainer) {
        briefContainer.innerHTML = `
            <div class="ai-big-news-core">
                <h4>📋 核心动态</h4>
                <p>${coreDynamics.replace(/\n/g, '<br>')}</p>
            </div>
            <div class="ai-big-news-trend">
                <h4>🔮 趋势判断</h4>
                <p><strong>${trendJudgment.replace(/\n/g, '')}</strong></p>
            </div>
        `;
    }
    
    // 渲染重点关注
    const listContainer = document.getElementById('ai-big-news-list');
    if (listContainer) {
        if (keyFocus.length === 0) {
            // 如果没有解析到，显示简化版
            listContainer.innerHTML = '<p class="ai-big-news-empty">今日暂无重点关注</p>';
        } else {
            listContainer.innerHTML = keyFocus.map((item, index) => `
                <div class="ai-big-news-item">
                    <div class="ai-big-news-rank">${index + 1}</div>
                    <div class="ai-big-news-content">
                        <div class="ai-big-news-meta">
                            <span class="ai-big-news-source">${item.source}</span>
                        </div>
                        <h3 class="ai-big-news-title">${item.title}</h3>
                        ${item.summary ? `<p class="ai-big-news-summary">${item.summary}</p>` : ''}
                    </div>
                </div>
            `).join('');
        }
    }
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
    
    // 渲染文章 - 优先显示中文翻译
    grid.innerHTML = articles.map(article => {
        const url = article.original_url || article.url || '#';
        // 优先使用中文标题和摘要
        const title = article.title_zh || article.title || '无标题';
        const summary = article.summary_zh || article.summary || '';
        const sourceName = article.source?.name || article.source || '未知来源';
        
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

// Keep old function for compatibility
function toggleTop10() {
    toggleAIBigNews();
}
