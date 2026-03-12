// ========================================
// Data Loop Hub - Main Application
// ========================================

// Utility Functions
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// Show toast notification
function showToast(message, duration = 3000) {
    const toast = $('#toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), duration);
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
    return date.toLocaleDateString('zh-CN', options);
}

// Get today date string
function getTodayString() {
    return new Date().toISOString().split('T')[0];
}

// LocalStorage helpers
const Storage = {
    get(key) {
        try {
            return JSON.parse(localStorage.getItem(key)) || [];
        } catch {
            return [];
        }
    },
    set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },
    addBookmark(article) {
        const bookmarks = this.get('bookmarks');
        if (!bookmarks.find(b => b.id === article.id)) {
            bookmarks.push({ ...article, bookmarkedAt: new Date().toISOString() });
            this.set('bookmarks', bookmarks);
            updateBookmarkCount();
            return true;
        }
        return false;
    },
    removeBookmark(id) {
        const bookmarks = this.get('bookmarks').filter(b => b.id !== id);
        this.set('bookmarks', bookmarks);
        updateBookmarkCount();
    },
    isBookmarked(id) {
        return this.get('bookmarks').some(b => b.id === id);
    }
};

// Update bookmark count in sidebar
function updateBookmarkCount() {
    const count = Storage.get('bookmarks').length;
    const badge = $('#bookmark-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

// Update today count in sidebar
function updateTodayCount(count) {
    const badge = $('#today-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

// Sidebar toggle
function initSidebar() {
    const sidebar = $('#sidebar');
    const toggle = $('#sidebar-toggle');
    const menuToggle = $('#menu-toggle');
    
    if (toggle) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.add('active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024 && 
            !sidebar.contains(e.target) && 
            !menuToggle?.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });
}

// Modal functions
function openModal(content) {
    const modal = $('#article-modal');
    const detail = $('#article-detail');
    detail.innerHTML = content;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = $('#article-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// Generate article detail HTML
function generateArticleDetail(article) {
    const isBookmarked = Storage.isBookmarked(article.id);
    return `
        <div class="article-header">
            <div class="article-tags" style="margin-bottom: 12px;">
                <span class="tag ${article.category}">${getCategoryName(article.category)}</span>
            </div>
            <h1 class="article-title">${article.title}</h1>
            <div class="article-meta">
                <div class="article-meta-item">
                    <span>📅</span>
                    <span>${article.publishDate}</span>
                </div>
                <div class="article-meta-item">
                    <span>📰</span>
                    <span>${article.source}</span>
                </div>
                ${article.author ? `
                <div class="article-meta-item">
                    <span>✍️</span>
                    <span>${article.author}</span>
                </div>
                ` : ''}
            </div>
        </div>
        <div class="article-body">
            ${article.content || `<p>${article.summary}</p>`}
        </div>
        <div class="article-actions">
            <a href="${article.url}" target="_blank" class="btn btn-primary">阅读原文</a>
            <button class="btn btn-secondary" onclick="toggleBookmarkFromModal('${article.id}')">
                <span id="modal-bookmark-icon">${isBookmarked ? '★' : '☆'}</span>
                <span id="modal-bookmark-text">${isBookmarked ? '已收藏' : '收藏'}</span>
            </button>
        </div>
    `;
}

// Toggle bookmark from modal
function toggleBookmarkFromModal(articleId) {
    const article = window.currentArticles?.find(a => a.id === articleId);
    if (!article) return;
    
    if (Storage.isBookmarked(articleId)) {
        Storage.removeBookmark(articleId);
        $('#modal-bookmark-icon').textContent = '☆';
        $('#modal-bookmark-text').textContent = '收藏';
        showToast('已取消收藏');
    } else {
        Storage.addBookmark(article);
        $('#modal-bookmark-icon').textContent = '★';
        $('#modal-bookmark-text').textContent = '已收藏';
        showToast('已添加到收藏夹');
    }
    
    // Update card button if visible
    updateCardBookmarkButton(articleId);
}

// Update bookmark button on card
function updateCardBookmarkButton(articleId) {
    const btn = $(`.bookmark-btn[data-id="${articleId}"]`);
    if (btn) {
        const isBookmarked = Storage.isBookmarked(articleId);
        btn.innerHTML = isBookmarked ? '★' : '☆';
        btn.classList.toggle('active', isBookmarked);
    }
}

// Get category name
function getCategoryName(category) {
    const names = {
        'llm': '大模型',
        'autonomous': '自动驾驶',
        'robotics': '具身智能',
        'company': '公司动态',
        'product': '产品发布',
        'research': '技术研究'
    };
    return names[category] || category;
}

// Generate news card HTML
function generateNewsCard(article) {
    const isBookmarked = Storage.isBookmarked(article.id);
    return `
        <article class="news-card" data-id="${article.id}" data-category="${article.category}">
            <div class="card-header">
                <div class="card-tags">
                    <span class="tag ${article.category}">${getCategoryName(article.category)}</span>
                </div>
                <div class="card-time">${article.publishDate}</div>
            </div>
            <div class="card-body">
                <h3 class="card-title">${article.title}</h3>
                <p class="card-summary">${article.summary}</p>
            </div>
            <div class="card-footer">
                <div class="card-source">
                    <div class="source-icon">${article.source[0]}</div>
                    <span>${article.source}</span>
                </div>
                <div class="card-actions">
                    <button class="btn-icon bookmark-btn ${isBookmarked ? 'active' : ''}" 
                            data-id="${article.id}"
                            onclick="event.stopPropagation(); toggleBookmark('${article.id}')">
                        ${isBookmarked ? '★' : '☆'}
                    </button>
                    <a href="${article.url}" target="_blank" class="btn btn-primary" onclick="event.stopPropagation()">阅读</a>
                </div>
            </div>
        </article>
    `;
}

// Toggle bookmark
function toggleBookmark(articleId) {
    const article = window.currentArticles?.find(a => a.id === articleId);
    if (!article) return;
    
    if (Storage.isBookmarked(articleId)) {
        Storage.removeBookmark(articleId);
        showToast('已取消收藏');
    } else {
        Storage.addBookmark(article);
        showToast('已添加到收藏夹');
    }
    
    updateCardBookmarkButton(articleId);
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    updateBookmarkCount();
    
    // Set current date
    const dateEl = $('#current-date');
    if (dateEl) {
        dateEl.textContent = formatDate(getTodayString());
    }
    
    // Set date picker value
    const datePicker = $('#date-picker');
    if (datePicker) {
        datePicker.value = getTodayString();
    }
});

// Export functions for other modules
window.openModal = openModal;
window.closeModal = closeModal;
window.toggleBookmark = toggleBookmark;
window.toggleBookmarkFromModal = toggleBookmarkFromModal;
window.showToast = showToast;
window.Storage = Storage;
window.generateNewsCard = generateNewsCard;
window.generateArticleDetail = generateArticleDetail;
window.updateTodayCount = updateTodayCount;
window.getCategoryName = getCategoryName;
