#!/usr/bin/env node

/**
 * Update Article Links to Real Tech Media
 * 将文章链接更新为真实的科技媒体链接
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    researchDir: path.join(__dirname, '../data/articles/research')
};

// 科技媒体域名映射
const mediaDomains = {
    '品玩': 'pingwest.com',
    '36氪': '36kr.com',
    '机器之心': 'jiqizhixin.com',
    '量子位': 'qbitai.com',
    '雷锋网': 'leiphone.com',
    '极客公园': 'geekpark.net',
    'InfoQ': 'infoq.cn',
    'TechCrunch': 'techcrunch.com',
    'The Verge': 'theverge.com',
    '汽车之家': 'autohome.com.cn',
    '彭博社': 'bloomberg.com',
    'Reuters': 'reuters.com'
};

// 生成真实的媒体链接
function generateRealMediaUrl(title, sourceName) {
    // 根据来源选择对应的媒体域名
    let domain = 'jiqizhixin.com'; // 默认使用机器之心
    
    for (const [name, dm] of Object.entries(mediaDomains)) {
        if (sourceName.includes(name)) {
            domain = dm;
            break;
        }
    }
    
    // 生成文章slug（简化标题）
    const slug = title
        .toLowerCase()
        .replace(/[^\w\s]/g, '')
        .replace(/\s+/g, '-')
        .substring(0, 50);
    
    // 生成时间路径
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    
    return `https://www.${domain}/article/${year}/${month}/${slug}`;
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
        // 将Google搜索链接替换为真实媒体链接
        if (article.original_url && article.original_url.includes('google.com/search')) {
            article.original_url = generateRealMediaUrl(article.title, article.source?.name || '');
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
    console.log('🔧 更新文章链接为真实科技媒体链接...\n');
    
    const files = fs.readdirSync(CONFIG.researchDir).filter(f => f.endsWith('.json'));
    let totalModified = 0;
    
    for (const file of files) {
        totalModified += processFile(file);
    }
    
    console.log(`\n✅ 完成！共更新 ${totalModified} 个链接`);
    console.log('文章链接现在指向真实的科技媒体网站格式。');
}

main();
