#!/usr/bin/env node

/**
 * Fix article links to use real URLs or search links
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    researchDir: path.join(__dirname, '../data/articles/research')
};

// 真实的文章链接映射（示例）
const realLinks = {
    '特斯拉': 'https://www.jiqizhixin.com/articles/2024-03-13-1',
    '华为': 'https://www.jiqizhixin.com/articles/2024-03-13-2',
    '小鹏': 'https://www.jiqizhixin.com/articles/2024-03-13-3',
    '百度': 'https://www.jiqizhixin.com/articles/2024-03-13-4',
    '蔚来': 'https://www.jiqizhixin.com/articles/2024-03-13-5',
    '理想': 'https://www.jiqizhixin.com/articles/2024-03-13-6',
    'OpenAI': 'https://www.jiqizhixin.com/articles/2024-03-13-7',
    'Google': 'https://www.jiqizhixin.com/articles/2024-03-13-8',
    'Figure': 'https://www.jiqizhixin.com/articles/2024-03-13-9',
    '卓驭': 'https://www.jiqizhixin.com/articles/2024-03-13-10',
};

// 生成搜索链接
function generateSearchLink(title) {
    const searchQuery = encodeURIComponent(title);
    return `https://www.jiqizhixin.com/search?query=${searchQuery}`;
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
        // 检查链接是否是模拟的
        const url = article.original_url || '';
        
        // 如果链接包含模拟格式，替换为搜索链接
        if (url.includes('/article/2026/') || url.includes('/article/2025/')) {
            article.original_url = generateSearchLink(article.title);
            modifiedCount++;
        }
    }
    
    if (modifiedCount > 0) {
        fs.writeFileSync(filePath, JSON.stringify(articles, null, 2));
        console.log(`  ✓ 已更新 ${modifiedCount} 个链接为搜索链接`);
    } else {
        console.log(`  - 无需更新`);
    }
    
    return modifiedCount;
}

// 主函数
function main() {
    console.log('🔧 修复文章链接为搜索链接...\n');
    
    const files = fs.readdirSync(CONFIG.researchDir).filter(f => f.endsWith('.json'));
    let totalModified = 0;
    
    for (const file of files) {
        totalModified += processFile(file);
    }
    
    console.log(`\n✅ 完成！共更新 ${totalModified} 个链接`);
    console.log('现在点击"阅读原文"会跳转到机器之心的搜索页面。');
}

main();
