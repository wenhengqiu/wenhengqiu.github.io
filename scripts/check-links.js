#!/usr/bin/env node

/**
 * Link Checker - 检查所有文章链接的有效性
 * 由于很多网站有反爬虫机制，我们主要检查链接格式是否正确
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    researchDir: path.join(__dirname, '../data/articles/research')
};

const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m'
};

// 检查链接格式
function validateLinkFormat(url) {
    const issues = [];
    
    if (!url) {
        issues.push('链接为空');
        return issues;
    }
    
    // 检查是否是有效URL
    try {
        new URL(url);
    } catch {
        issues.push('URL格式无效');
        return issues;
    }
    
    // 检查是否使用http/https
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        issues.push('必须使用http或https协议');
    }
    
    // 检查常见无效域名
    const invalidDomains = [
        'example.com',
        'localhost',
        '127.0.0.1',
        'test.com'
    ];
    
    for (const domain of invalidDomains) {
        if (url.includes(domain)) {
            issues.push(`使用了示例域名: ${domain}`);
        }
    }
    
    // 检查是否包含空格
    if (url.includes(' ')) {
        issues.push('URL包含空格');
    }
    
    // 检查是否包含中文（应该编码）
    if (/[\u4e00-\u9fa5]/.test(url)) {
        issues.push('URL包含未编码的中文字符');
    }
    
    return issues;
}

// 检查所有文章
function checkAllArticles() {
    const files = fs.readdirSync(CONFIG.researchDir).filter(f => f.endsWith('.json'));
    const allIssues = [];
    let totalChecked = 0;
    
    for (const file of files) {
        const filePath = path.join(CONFIG.researchDir, file);
        console.log(`${colors.blue}检查 ${file}...${colors.reset}`);
        
        let articles;
        try {
            articles = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        } catch (error) {
            console.log(`${colors.red}  JSON解析失败: ${error.message}${colors.reset}`);
            continue;
        }
        
        for (const article of articles) {
            totalChecked++;
            const issues = validateLinkFormat(article.original_url);
            
            if (issues.length > 0) {
                allIssues.push({
                    file,
                    id: article.id,
                    title: article.title,
                    url: article.original_url,
                    issues
                });
                console.log(`${colors.red}  ❌ ${article.title.substring(0, 50)}...${colors.reset}`);
                issues.forEach(issue => console.log(`     - ${issue}`));
            }
        }
    }
    
    return { totalChecked, issues: allIssues };
}

// 生成替代链接（使用搜索链接）
function generateAlternativeLink(article) {
    const searchQuery = encodeURIComponent(article.title);
    return `https://www.google.com/search?q=${searchQuery}`;
}

// 修复无效链接
function fixInvalidLinks(issues) {
    console.log(`\n${colors.yellow}🔧 修复无效链接...${colors.reset}\n`);
    
    // 按文件分组
    const byFile = {};
    issues.forEach(issue => {
        if (!byFile[issue.file]) byFile[issue.file] = [];
        byFile[issue.file].push(issue);
    });
    
    for (const [file, fileIssues] of Object.entries(byFile)) {
        const filePath = path.join(CONFIG.researchDir, file);
        let articles = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        let fixedCount = 0;
        
        for (const issue of fileIssues) {
            const article = articles.find(a => a.id === issue.id);
            if (article) {
                // 如果链接无效，使用搜索链接替代
                if (issue.issues.some(i => i.includes('为空') || i.includes('无效'))) {
                    article.original_url = generateAlternativeLink(article);
                    fixedCount++;
                    console.log(`${colors.green}  ✓ ${article.title.substring(0, 40)}...${colors.reset}`);
                }
            }
        }
        
        if (fixedCount > 0) {
            fs.writeFileSync(filePath, JSON.stringify(articles, null, 2));
            console.log(`${colors.green}  已修复 ${fixedCount} 个链接，保存到 ${file}${colors.reset}\n`);
        }
    }
}

// 主函数
function main() {
    console.log(`${colors.blue}🔍 检查所有文章链接...${colors.reset}\n`);
    
    const { totalChecked, issues } = checkAllArticles();
    
    console.log(`\n${'='.repeat(60)}`);
    console.log(`${colors.blue}📊 检查结果${colors.reset}`);
    console.log('='.repeat(60));
    console.log(`检查文章总数: ${totalChecked}`);
    console.log(`无效链接数量: ${issues.length}`);
    
    if (issues.length > 0) {
        console.log(`\n${colors.red}❌ 发现无效链接:${colors.reset}\n`);
        issues.forEach((issue, index) => {
            console.log(`${index + 1}. ${issue.title}`);
            console.log(`   文件: ${issue.file}`);
            console.log(`   链接: ${issue.url || '(空)'}`);
            console.log(`   问题: ${issue.issues.join(', ')}`);
            console.log();
        });
        
        // 自动修复
        fixInvalidLinks(issues);
        
        console.log(`${colors.yellow}💡 提示:${colors.reset}`);
        console.log('   - 部分链接返回403是因为网站有反爬虫保护');
        console.log('   - 已自动将无效链接替换为搜索链接');
        console.log('   - 建议手动检查并替换为真实有效的链接');
    } else {
        console.log(`\n${colors.green}✅ 所有链接格式正确！${colors.reset}`);
    }
    
    console.log('='.repeat(60) + '\n');
}

main();
