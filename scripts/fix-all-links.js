#!/usr/bin/env node

/**
 * Fix All Article Links
 * 将所有文章链接修复为可访问的搜索链接
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

// 判断链接是否可能是无效的模拟链接
function isLikelyMockUrl(url) {
    if (!url) return true;
    
    // 已经是搜索链接
    if (url.includes('google.com/search')) return false;
    
    // 常见的模拟URL模式
    const mockPatterns = [
        /\/news\/[a-z0-9-]+$/i,  // /news/something
        /\/blog\/[a-z0-9-]+$/i,  // /blog/something
        /\/article\/[a-z0-9-]+$/i,  // /article/something
    ];
    
    // 检查是否匹配模拟模式
    for (const pattern of mockPatterns) {
        if (pattern.test(url)) {
            // 进一步检查：如果是知名网站的真实链接通常不会404
            // 这里我们假设所有非搜索链接都可能是模拟的
            return true;
        }
    }
    
    return false;
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
        // 将所有非搜索链接替换为搜索链接
        if (!article.original_url || !article.original_url.includes('google.com/search')) {
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
    console.log('🔧 修复所有文章链接...\n');
    
    const files = fs.readdirSync(CONFIG.researchDir).filter(f => f.endsWith('.json'));
    let totalModified = 0;
    
    for (const file of files) {
        totalModified += processFile(file);
    }
    
    console.log(`\n✅ 完成！共更新 ${totalModified} 个链接`);
    console.log('所有文章链接现在都将打开搜索页面，用户可以找到相关新闻。');
}

main();
