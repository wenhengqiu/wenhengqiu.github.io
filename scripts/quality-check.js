#!/usr/bin/env node

/**
 * Quality Check Script
 * 检测文章数据的质量，包括链接有效性、JSON格式、必填字段等
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// 配置
const CONFIG = {
    researchDir: path.join(__dirname, '../data/articles/research'),
    dailyDir: path.join(__dirname, '../data/articles/daily'),
    reportDir: path.join(__dirname, '../data/quality'),
    timeout: 5000,
    maxRedirects: 3
};

// 确保报告目录存在
if (!fs.existsSync(CONFIG.reportDir)) {
    fs.mkdirSync(CONFIG.reportDir, { recursive: true });
}

// 颜色输出
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m'
};

// 检查链接有效性
async function checkLink(url) {
    return new Promise((resolve) => {
        if (!url || !url.startsWith('http')) {
            resolve({ valid: false, status: 0, error: 'Invalid URL' });
            return;
        }

        const client = url.startsWith('https') ? https : http;
        const req = client.request(url, { method: 'HEAD', timeout: CONFIG.timeout }, (res) => {
            const status = res.statusCode;
            if (status >= 200 && status < 400) {
                resolve({ valid: true, status });
            } else {
                resolve({ valid: false, status, error: `HTTP ${status}` });
            }
        });

        req.on('error', (error) => {
            resolve({ valid: false, status: 0, error: error.message });
        });

        req.on('timeout', () => {
            req.destroy();
            resolve({ valid: false, status: 0, error: 'Timeout' });
        });

        req.end();
    });
}

// 验证 JSON 格式
function validateJSON(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        JSON.parse(content);
        return { valid: true };
    } catch (error) {
        return { valid: false, error: error.message };
    }
}

// 检查必填字段
function checkRequiredFields(article) {
    const required = ['id', 'title', 'summary', 'original_url', 'publish_date', 'category'];
    const missing = required.filter(field => !article[field]);
    return { valid: missing.length === 0, missing };
}

// 检查重复 ID
function checkDuplicateIds(articles) {
    const ids = articles.map(a => a.id);
    const duplicates = [];
    const seen = new Set();
    
    for (const id of ids) {
        if (seen.has(id)) {
            duplicates.push(id);
        } else {
            seen.add(id);
        }
    }
    
    return { valid: duplicates.length === 0, duplicates };
}

// 检查研究文章
async function checkResearchArticles() {
    console.log(`${colors.blue}🔍 检查研究文章...${colors.reset}`);
    
    const files = fs.readdirSync(CONFIG.researchDir).filter(f => f.endsWith('.json'));
    const results = {
        total: 0,
        valid: 0,
        invalid: 0,
        linkChecks: [],
        fieldChecks: [],
        errors: []
    };

    for (const file of files) {
        const filePath = path.join(CONFIG.researchDir, file);
        console.log(`  检查 ${file}...`);
        
        // 验证 JSON
        const jsonCheck = validateJSON(filePath);
        if (!jsonCheck.valid) {
            results.errors.push({ file, error: `JSON 格式错误: ${jsonCheck.error}` });
            continue;
        }
        
        const articles = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        results.total += articles.length;
        
        // 检查重复 ID
        const dupCheck = checkDuplicateIds(articles);
        if (!dupCheck.valid) {
            results.errors.push({ file, error: `重复 ID: ${dupCheck.duplicates.join(', ')}` });
        }
        
        // 检查每篇文章
        for (const article of articles) {
            // 检查必填字段
            const fieldCheck = checkRequiredFields(article);
            if (!fieldCheck.valid) {
                results.fieldChecks.push({
                    id: article.id,
                    file,
                    missing: fieldCheck.missing
                });
            }
            
            // 检查链接 (只检查前5个链接，避免太慢)
            if (results.linkChecks.length < 5 && article.original_url) {
                const linkResult = await checkLink(article.original_url);
                results.linkChecks.push({
                    id: article.id,
                    title: article.title,
                    url: article.original_url,
                    ...linkResult
                });
            }
        }
    }
    
    return results;
}

// 生成报告
function generateReport(results) {
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            totalArticles: results.total,
            validArticles: results.valid,
            invalidArticles: results.invalid,
            linkCheckCount: results.linkChecks.length,
            fieldErrorCount: results.fieldChecks.length,
            errorCount: results.errors.length
        },
        linkChecks: results.linkChecks,
        fieldChecks: results.fieldChecks,
        errors: results.errors
    };
    
    const reportPath = path.join(CONFIG.reportDir, 'quality-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    return report;
}

// 打印报告
function printReport(report) {
    console.log('\n' + '='.repeat(60));
    console.log(`${colors.blue}📊 质量检测报告${colors.reset}`);
    console.log('='.repeat(60));
    
    console.log(`\n总文章数: ${report.summary.totalArticles}`);
    console.log(`字段错误: ${report.summary.fieldErrorCount}`);
    console.log(`系统错误: ${report.summary.errorCount}`);
    
    if (report.linkChecks.length > 0) {
        console.log(`\n${colors.blue}🔗 链接检测结果 (抽样)${colors.reset}`);
        const validLinks = report.linkChecks.filter(l => l.valid);
        const invalidLinks = report.linkChecks.filter(l => !l.valid);
        
        console.log(`  有效链接: ${validLinks.length}/${report.linkChecks.length}`);
        
        if (invalidLinks.length > 0) {
            console.log(`  ${colors.red}无效链接:${colors.reset}`);
            invalidLinks.forEach(link => {
                console.log(`    - ${link.title}`);
                console.log(`      ${colors.red}${link.url}${colors.reset}`);
                console.log(`      错误: ${link.error}`);
            });
        }
    }
    
    if (report.fieldChecks.length > 0) {
        console.log(`\n${colors.yellow}⚠️ 字段缺失警告${colors.reset}`);
        report.fieldChecks.slice(0, 5).forEach(check => {
            console.log(`  - ${check.id}: 缺少 ${check.missing.join(', ')}`);
        });
        if (report.fieldChecks.length > 5) {
            console.log(`  ... 还有 ${report.fieldChecks.length - 5} 个`);
        }
    }
    
    if (report.errors.length > 0) {
        console.log(`\n${colors.red}❌ 系统错误${colors.reset}`);
        report.errors.forEach(error => {
            console.log(`  - ${error.file}: ${error.error}`);
        });
    }
    
    console.log('\n' + '='.repeat(60));
    console.log(`报告已保存: data/quality/quality-report.json`);
    console.log('='.repeat(60) + '\n');
}

// 主函数
async function main() {
    console.log(`${colors.blue}🚀 开始质量检测...${colors.reset}\n`);
    
    const results = await checkResearchArticles();
    const report = generateReport(results);
    printReport(report);
    
    // 如果有严重错误，退出码非0
    if (report.summary.errorCount > 0 || report.summary.fieldErrorCount > 10) {
        process.exit(1);
    }
}

main().catch(error => {
    console.error(`${colors.red}检测失败:${colors.reset}`, error);
    process.exit(1);
});
