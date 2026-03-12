#!/usr/bin/env node
/**
 * 文章采集脚本
 * 从多个信息源采集 AI 行业资讯
 * 
 * 使用方法:
 * node scripts/fetch-news.js [--date=YYYY-MM-DD] [--source=source_id]
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { parseString } = require('xml2js');

// 配置
const CONFIG = {
  dataDir: path.join(__dirname, '../data/articles/daily'),
  sourcesFile: path.join(__dirname, '../data/sources/sources.json'),
  userAgent: 'DataLoopBot/1.0 (Research Purpose)'
};

// 工具函数
function fetchRSS(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'User-Agent': CONFIG.userAgent
      }
    };
    
    https.get(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

function parseRSS(xml) {
  return new Promise((resolve, reject) => {
    parseString(xml, (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function generateId(date, index) {
  return `${date}-${String(index).padStart(3, '0')}`;
}

function categorizeArticle(title, content) {
  const keywords = {
    'llm': ['GPT', 'LLM', '大模型', '语言模型', 'Claude', 'Gemini', 'Kimi', '通义千问', 'ChatGPT'],
    'autonomous': ['自动驾驶', 'FSD', '智驾', '无人车', 'Waymo', '特斯拉', '小鹏', '华为 ADS'],
    'robotics': ['机器人', '具身智能', 'Optimus', 'Figure AI', '人形机器人', '机械臂'],
    'company': ['融资', '收购', 'IPO', '上市', '估值', '投资'],
    'product': ['发布', '新品', '上线', '推出', '更新'],
    'research': ['论文', '研究', '算法', '模型', '训练', 'arXiv']
  };
  
  const text = (title + ' ' + content).toLowerCase();
  
  for (const [category, words] of Object.entries(keywords)) {
    if (words.some(word => text.includes(word.toLowerCase()))) {
      return category;
    }
  }
  
  return 'research';
}

function extractTags(title, content) {
  const companies = [
    'OpenAI', 'Google', 'Meta', 'Microsoft', 'Amazon', 'Apple',
    'Tesla', 'Waymo', 'Cruise', '小鹏', '华为', '百度', '蔚来',
    '智谱', '月之暗面', 'MiniMax', '字节', '阿里', '腾讯',
    'Figure AI', '波士顿动力', '宇树', '智元'
  ];
  
  const technologies = [
    'GPT', 'LLM', 'Transformer', 'Diffusion', 'RLHF',
    '端到端', '多模态', 'Agent', 'RAG', '向量数据库'
  ];
  
  const text = title + ' ' + content;
  const tags = [];
  
  companies.forEach(c => {
    if (text.includes(c)) tags.push(c);
  });
  
  technologies.forEach(t => {
    if (text.includes(t)) tags.push(t);
  });
  
  return [...new Set(tags)].slice(0, 5);
}

// 从 RSS 源采集
async function fetchFromRSS(source) {
  try {
    console.log(`📡 采集: ${source.name}`);
    const xml = await fetchRSS(source.rss_url);
    const feed = await parseRSS(xml);
    
    const items = feed.rss?.channel?.[0]?.item || [];
    const articles = [];
    
    for (const item of items.slice(0, 10)) {
      const title = item.title?.[0] || '';
      const link = item.link?.[0] || '';
      const description = item.description?.[0] || '';
      const pubDate = item.pubDate?.[0] || new Date().toISOString();
      
      articles.push({
        title: title.replace(/<[^>]*>/g, ''),
        summary: description.replace(/<[^>]*>/g, '').slice(0, 200) + '...',
        content: description,
        url: link,
        publishDate: new Date(pubDate).toISOString().split('T')[0],
        displayDate: new Date(pubDate).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
        source: {
          name: source.name,
          type: source.category,
          url: source.url
        },
        category: categorizeArticle(title, description),
        tags: extractTags(title, description),
        importance: 'medium'
      });
    }
    
    console.log(`✅ ${source.name}: ${articles.length} 篇文章`);
    return articles;
  } catch (error) {
    console.error(`❌ ${source.name}: ${error.message}`);
    return [];
  }
}

// 保存文章到文件
function saveArticles(date, articles) {
  const year = date.slice(0, 4);
  const month = date.slice(5, 7);
  const dir = path.join(CONFIG.dataDir, year, month);
  
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  const filePath = path.join(dir, `${date}.json`);
  
  // 添加 ID
  const articlesWithId = articles.map((article, index) => ({
    id: generateId(date, index + 1),
    ...article,
    isFeatured: index < 3
  }));
  
  fs.writeFileSync(filePath, JSON.stringify(articlesWithId, null, 2));
  console.log(`💾 已保存: ${filePath} (${articlesWithId.length} 篇文章)`);
  
  return articlesWithId;
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const dateArg = args.find(a => a.startsWith('--date='))?.split('=')[1];
  const sourceArg = args.find(a => a.startsWith('--source='))?.split('=')[1];
  
  const date = dateArg || new Date().toISOString().split('T')[0];
  
  console.log(`\n🤖 数据闭环文章中心 - 资讯采集\n`);
  console.log(`📅 日期: ${date}\n`);
  
  // 加载信息源配置
  const sourcesConfig = JSON.parse(fs.readFileSync(CONFIG.sourcesFile, 'utf8'));
  let sources = sourcesConfig.sources.filter(s => s.active && s.type === 'rss');
  
  if (sourceArg) {
    sources = sources.filter(s => s.id === sourceArg);
  }
  
  console.log(`📡 信息源数量: ${sources.length}\n`);
  
  // 采集文章
  const allArticles = [];
  
  for (const source of sources) {
    const articles = await fetchFromRSS(source);
    allArticles.push(...articles);
    
    // 延迟避免请求过快
    await new Promise(r => setTimeout(r, 1000));
  }
  
  // 去重
  const uniqueArticles = [];
  const seen = new Set();
  
  for (const article of allArticles) {
    const key = article.title.slice(0, 50);
    if (!seen.has(key)) {
      seen.add(key);
      uniqueArticles.push(article);
    }
  }
  
  console.log(`\n📊 采集统计:`);
  console.log(`   总计: ${allArticles.length}`);
  console.log(`   去重后: ${uniqueArticles.length}\n`);
  
  // 保存
  if (uniqueArticles.length > 0) {
    saveArticles(date, uniqueArticles);
  } else {
    console.log('⚠️ 未采集到文章\n');
  }
}

main().catch(console.error);
