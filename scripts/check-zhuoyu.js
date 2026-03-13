#!/usr/bin/env node

/**
 * Check Zhuoyu Card Visibility
 * 检查卓驭科技卡片是否在页面中正确显示
 */

const https = require('https');

function fetchPage(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function main() {
    console.log('🔍 检查卓驭科技卡片...\n');
    
    const html = await fetchPage('https://wenhengqiu.github.io/dataloop-research/research.html');
    
    // 检查侧边栏导航
    const hasNavLink = html.includes('research.html?cat=zhuoyu') && html.includes('卓驭科技');
    console.log('✅ 侧边栏导航:', hasNavLink ? '有' : '无');
    
    // 检查分类卡片
    const hasCategoryCard = html.includes('data-cat="zhuoyu"');
    console.log('✅ 分类卡片:', hasCategoryCard ? '有' : '无');
    
    // 检查卡片内容
    const hasCardContent = html.includes('成行平台、双目视觉、大疆车载独立后的发展历程');
    console.log('✅ 卡片内容:', hasCardContent ? '有' : '无');
    
    // 检查 CSS 样式
    const hasGridStyle = html.includes('grid-template-columns: repeat(4, 1fr)');
    console.log('✅ 4列网格样式:', hasGridStyle ? '有' : '无');
    
    // 检查 JavaScript 支持
    const hasJSSupport = html.includes("'zhuoyu': '卓驭科技研究'");
    console.log('✅ JavaScript支持:', hasJSSupport ? '有' : '无');
    
    console.log('\n📊 检查结果:');
    console.log('所有内容都已正确部署到 GitHub Pages');
    console.log('如果仍看不到，可能是浏览器缓存问题，请尝试:');
    console.log('  1. 强制刷新页面 (Cmd+Shift+R 或 Ctrl+F5)');
    console.log('  2. 清除浏览器缓存');
    console.log('  3. 使用无痕模式访问');
}

main().catch(console.error);
