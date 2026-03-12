// ========================================
// Daily News Module
// ========================================

// Sample data for demonstration
const sampleArticles = [
    {
        id: "2026-03-13-001",
        title: "GPT-5.4 系列模型发布，强化专业工作与智能体能力",
        summary: "OpenAI 正式推出 GPT-5.4 及 GPT-5.4 Pro 模型，面向 ChatGPT、API 及 Codex 平台同步上线。新模型在专业工作场景和智能体能力方面有显著提升。",
        content: "<p>OpenAI 今日正式推出 GPT-5.4 及 GPT-5.4 Pro 模型，面向 ChatGPT、API 及 Codex 平台同步上线。</p><p>新模型的主要特点包括：</p><ul><li>强化专业工作场景的表现</li><li>智能体能力显著提升</li><li>更好的代码理解和生成能力</li><li>多模态交互能力增强</li></ul><p>此次发布标志着 OpenAI 在企业级 AI 应用领域的进一步布局。</p>",
        category: "llm",
        publishDate: "3月13日",
        source: "品玩",
        url: "https://www.pingwest.com/w/311850",
        isFeatured: true
    },
    {
        id: "2026-03-13-002",
        title: "阿里通义千问核心开发者林俊旸宣布离开",
        summary: "林俊旸（Qwen 核心开发者）宣布离开阿里，阿里重整了 Qwen、阿里云和千问产品的关系。开源社区最活跃的中国模型开发者个人变动引发广泛关注。",
        content: "<p>开源社区最活跃的中国模型开发者林俊旸宣布离开阿里，引发业界广泛关注。</p><p>此次变动涉及：</p><ul><li>阿里重整 Qwen、阿里云和千问产品的关系</li><li>开源社区对 Qwen 后续发展的关注</li><li>国内大模型人才流动的新趋势</li></ul><p>林俊旸在 Qwen 系列模型的开发中发挥了重要作用，其离职被视为中国 AI 领域的重要人事变动。</p>",
        category: "company",
        publishDate: "3月13日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311763",
        isFeatured: true
    },
    {
        id: "2026-03-13-003",
        title: "腾讯混元-WU：让模型每次任务都生成个新大脑",
        summary: "腾讯混元团队提出新架构，让模型每次任务都生成个新大脑，与其让用户选模型，不如让模型自己选。这一创新可能改变大模型的使用方式。",
        content: "<p>腾讯混元团队发布最新研究成果 HY-WU，提出了一种全新的大模型架构思路。</p><p>核心创新点：</p><ul><li>每次任务动态生成专用子网络</li><li>模型自主选择最适合的处理路径</li><li>显著提升特定任务的执行效率</li></ul><p>这一研究为大模型的效率优化提供了新方向。</p>",
        category: "research",
        publishDate: "3月12日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311879",
        isFeatured: true
    },
    {
        id: "2026-03-13-004",
        title: "OpenClaw 席卷中国科技与创业版图",
        summary: "AI Agent 平台 OpenClaw 在中国快速普及，闲鱼和小红书成为主要推手。每一次 AI 刷屏，闲鱼上的卖铲人都比你先到。",
        content: "<p>OpenClaw 作为 AI Agent 平台在中国快速普及，成为科技创业领域的新热点。</p><p>关键数据：</p><ul><li>闲鱼和小红书成为主要传播渠道</li><li>大量开发者加入 OpenClaw 生态</li><li>应用场景不断扩展</li></ul><p>这一现象反映了国内对 AI Agent 技术的强烈需求。</p>",
        category: "product",
        publishDate: "3月12日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311826"
    },
    {
        id: "2026-03-13-005",
        title: "小鹏智驾越过 L3 直达 L4，被称为中国智驾的 DeepSeek",
        summary: "小鹏汽车宣布智驾技术越过 L3 级别，直接实现 L4 能力。从汽车走向基础智能，小鹏正在成为中国智能驾驶领域的领军企业。",
        content: "<p>小鹏汽车在智能驾驶领域取得重大突破，宣布其智驾系统已具备 L4 级能力。</p><p>技术亮点：</p><ul><li>端到端大模型架构</li><li>城市 NOA 全国可用</li><li>从汽车向基础智能平台转型</li></ul><p>业内评价小鹏为\"中国智驾的 DeepSeek\"，意味着其在技术创新和工程实现上的突破。</p>",
        category: "autonomous",
        publishDate: "3月11日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311844"
    },
    {
        id: "2026-03-13-006",
        title: "如何成为顶级 Agentic 工程师",
        summary: "探讨 AI Agent 开发的最佳实践，从架构设计到工程实现，全面解析成为顶级 Agentic 工程师的路径。",
        content: "<p>随着 AI Agent 技术的快速发展，Agentic 工程师成为最热门的新兴岗位之一。</p><p>核心能力要求：</p><ul><li>深入理解 LLM 原理和能力边界</li><li>掌握 Agent 架构设计模式</li><li>具备系统工程思维</li><li>持续学习和实践能力</li></ul><p>本文从理论和实践两个维度，为想成为顶级 Agentic 工程师的开发者提供指导。</p>",
        category: "research",
        publishDate: "3月11日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311831"
    },
    {
        id: "2026-03-13-007",
        title: "AI 手机路线之争：字节、谷歌、阿里走的根本不是同一条路",
        summary: "都说自己是 AI 手机，但字节、谷歌、阿里走的根本不是同一条路。国内手机生态乱成一锅粥了，谁的 AI 也不好使。",
        content: "<p>AI 手机成为 2026 年最热门的概念之一，但不同厂商的技术路线差异巨大。</p><p>主要路线对比：</p><ul><li>字节：端侧大模型 + 云服务协同</li><li>谷歌：原生 Android AI 集成</li><li>阿里：通义千问全栈赋能</li></ul><p>文章深入分析了各家的技术选择和生态策略。</p>",
        category: "product",
        publishDate: "3月10日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311870"
    },
    {
        id: "2026-03-13-008",
        title: "从 iBeer 到 AI Agent：创造，不曾改变",
        summary: "回顾移动应用到 AI Agent 的演进历程，探讨技术变革背后的创造本质。",
        content: "<p>从 2008 年的 iBeer 到 2026 年的 AI Agent，技术形态发生了巨大变化，但创造的本质从未改变。</p><p>文章要点：</p><ul><li>技术演进的历史脉络</li><li>创造者的核心能力</li><li>AI 时代的新机遇</li></ul><p>这是一篇关于技术人文的深刻思考。</p>",
        category: "research",
        publishDate: "3月10日",
        source: "品玩",
        url: "https://www.pingwest.com/a/311914"
    }
];

// Current articles
let currentArticles = [];
let currentFilter = 'all';
let currentSearch = '';

// Load articles
async function loadArticles(date = null) {
    // In production, this would fetch from /data/articles/daily/YYYY-MM-DD.json
    // For now, use sample data
    currentArticles = sampleArticles;
    
    // Update stats
    updateStats();
    
    // Update today count
    updateTodayCount(currentArticles.length);
    
    // Render highlights
    renderHighlights();
    
    // Render articles
    renderArticles();
}

// Update statistics
function updateStats() {
    const stats = {
        total: currentArticles.length,
        llm: currentArticles.filter(a => a.category === 'llm').length,
        autonomous: currentArticles.filter(a => a.category === 'autonomous').length,
        robotics: currentArticles.filter(a => a.category === 'robotics').length
    };
    
    $('#stat-total').textContent = stats.total;
    $('#stat-llm').textContent = stats.llm;
    $('#stat-autonomous').textContent = stats.autonomous;
    $('#stat-robotics').textContent = stats.robotics;
}

// Render highlights
function renderHighlights() {
    const highlights = currentArticles.filter(a => a.isFeatured).slice(0, 3);
    const container = $('#daily-highlights');
    
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

// Render articles
function renderArticles() {
    const grid = $('#news-grid');
    
    // Filter articles
    const filtered = currentArticles.filter(article => {
        const matchFilter = currentFilter === 'all' || article.category === currentFilter;
        const matchSearch = !currentSearch || 
            article.title.toLowerCase().includes(currentSearch.toLowerCase()) ||
            article.summary.toLowerCase().includes(currentSearch.toLowerCase());
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
        datePicker.addEventListener('change', (e) => {
            loadArticles(e.target.value);
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
