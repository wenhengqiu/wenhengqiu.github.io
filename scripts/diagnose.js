#!/usr/bin/env node

/**
 * Diagnostic script for visibility issues
 */

const https = require('https');

function fetch(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function diagnose() {
    console.log('🔍 诊断网站问题...\n');
    
    const html = await fetch('https://wenhengqiu.github.io/dataloop-research/research.html');
    
    // 1. 检查卓驭科技导航
    const navMatch = html.match(/<a[^>]*href="research\.html\?cat=zhuoyu"[^>]*>/);
    console.log('1. 卓驭科技导航链接:', navMatch ? '✅ 存在' : '❌ 缺失');
    if (navMatch) {
        console.log('   HTML片段:', navMatch[0].substring(0, 100));
    }
    
    // 2. 检查卓驭科技卡片
    const cardMatch = html.match(/data-cat="zhuoyu"/);
    console.log('\n2. 卓驭科技分类卡片:', cardMatch ? '✅ 存在' : '❌ 缺失');
    
    // 3. 检查CSS变量
    const hasPrimary = html.includes('--primary');
    console.log('\n3. CSS变量 --primary:', hasPrimary ? '✅ 定义' : '❌ 未定义');
    
    // 4. 检查文章链接样式
    const articleLinkStyle = html.match(/\.article-link\s*{[^}]+}/);
    console.log('\n4. 文章链接样式:', articleLinkStyle ? '✅ 定义' : '❌ 未定义');
    if (articleLinkStyle) {
        console.log('   样式:', articleLinkStyle[0].substring(0, 150));
    }
    
    // 5. 检查网格布局
    const gridStyle = html.match(/grid-template-columns:\s*repeat\(4[^;]+;/);
    console.log('\n5. 4列网格布局:', gridStyle ? '✅ ' + gridStyle[0] : '❌ 未定义');
    
    console.log('\n📋 排查建议:');
    console.log('   如果所有检查都通过但仍看不到内容，可能是：');
    console.log('   1. 浏览器缓存 - 尝试 Ctrl+F5 强制刷新');
    console.log('   2. 浏览器插件 - 禁用广告拦截器');
    console.log('   3. 深色模式 - 检查对比度设置');
    console.log('   4. 缩放比例 - 检查页面缩放是否为100%');
    console.log('   5. 屏幕分辨率 - 检查显示器缩放设置');
}

diagnose().catch(console.error);
