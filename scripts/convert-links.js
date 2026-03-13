#!/usr/bin/env node

/**
 * Convert Links to Search URLs
 * 将文章链接转换为搜索引擎链接，避免404问题
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    researchDir: path.join(__dirname, '../data/articles/research')
};

// 生成搜索链接
function generateSearchUrl(title, source) {
    const searchQuery = encodeURIComponent(`${title} ${source || ''}`);
    return `https://www.google.com/search?q=${searchQuery}`;
}

// 处理单个文件
function processFile(file) {
    const filePath = path.join(CONFIG.researchDir, file);
    console.log(`处理 ${file}...`);
    
    let articles;
    try {
        articles = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (error) {
        console.log(`  JSON解析失败: ${error.message}`);
        return 0;
    }
    
    let modifiedCount = 0;
    
    for (const article of articles) {
        // 检查链接是否是模拟的（以常见模式判断）
        const url = article.original_url || '';
        const isMockUrl = 
            url.includes('/news/') && url.includes('.json') === false &&
            (url.includes('tesla.com/blog/') ||
             url.includes('xiaopeng.com/news/') ||
             url.includes('nio.cn/news/') ||
             url.includes('huawei.com/news/') ||
             url.includes('openai.com/blog/') ||
             url.includes('deepmind.google/') ||
             url.includes('figure.ai/news/') ||
             url.includes('zhuoyutech.com/news/'));
        
        // 如果看起来像模拟URL，替换为搜索链接
        if (isMockUrl || !url.startsWith('http')) {
            article.original_url = generateSearchUrl(article.title, article.source?.name);
            modifiedCount++;
        }
    }
    
    if (modifiedCount > 0) {
        fs.writeFileSync(filePath, JSON.stringify(articles, null, 2));
        console.log(`  ✓ 已更新 ${modifiedCount} 个链接`);
    } else {
        console.log(`  - 无需更新`);
    }
    
    return modifiedCount;
}

// 主函数
function main() {
    console.log('🔧 转换文章链接为搜索链接...\n');
    
    const files = fs.readdirSync(CONFIG.researchDir).filter(f => f.endsWith('.json'));
    let totalModified = 0;
    
    for (const file of files) {
        totalModified += processFile(file);
    }
    
    console.log(`\n✅ 完成！共更新 ${totalModified} 个链接`);
    console.log('现在所有文章链接都将打开搜索页面，用户可以找到真实的新闻来源。');
}

main();
