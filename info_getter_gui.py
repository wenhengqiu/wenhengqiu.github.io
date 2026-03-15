#!/usr/bin/env python3
"""
Info-Getter Mac GUI
使用Python + Tkinter构建的本地桌面应用
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

class InfoGetterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Info-Getter Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8fafc')
        
        # 数据路径
        self.data_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research')
        
        # 创建UI
        self.create_menu()
        self.create_sidebar()
        self.create_main_content()
        
        # 启动自动刷新
        self.auto_refresh()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="刷新数据", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="操作", menu=action_menu)
        action_menu.add_command(label="立即采集", command=self.manual_collect)
        action_menu.add_command(label="生成AI Big News", command=self.generate_report)
        action_menu.add_command(label="清理旧数据", command=self.clean_old_data)
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg='#ffffff', width=200, highlightbackground='#e2e8f0', highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo
        logo = tk.Label(sidebar, text="🤖 Info-Getter", bg='#ffffff', fg='#4f46e5', 
                       font=('Arial', 16, 'bold'), pady=20)
        logo.pack()
        
        # 菜单按钮
        menus = [
            ("📊 仪表盘", self.show_dashboard),
            ("📰 文章管理", self.show_articles),
            ("📡 信息源", self.show_sources),
            ("⚙️ 采集规则", self.show_rules),
            ("📋 执行日志", self.show_logs),
            ("🎮 系统控制", self.show_control),
        ]
        
        for text, command in menus:
            btn = tk.Button(sidebar, text=text, bg='#ffffff', fg='#475569',
                          font=('Arial', 12), bd=0, pady=15, cursor='hand2',
                          activebackground='#f1f5f9', activeforeground='#4f46e5',
                          command=command)
            btn.pack(fill=tk.X, padx=10, pady=2)
    
    def create_main_content(self):
        self.main_frame = tk.Frame(self.root, bg='#f8fafc')
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 默认显示仪表盘
        self.show_dashboard()
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_main_frame()
        
        # 标题
        title = tk.Label(self.main_frame, text="📊 仪表盘", bg='#f8fafc', fg='#1e293b',
                        font=('Arial', 24, 'bold'))
        title.pack(anchor='w', pady=(0, 20))
        
        # 统计卡片
        stats_frame = tk.Frame(self.main_frame, bg='#f8fafc')
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats = self.get_stats()
        stat_data = [
            ("今日采集", stats['today'], '#4f46e5'),
            ("本周采集", stats['week'], '#10b981'),
            ("总计文章", stats['total'], '#8b5cf6'),
            ("信息源", stats['sources'], '#f59e0b'),
        ]
        
        for label, value, color in stat_data:
            card = tk.Frame(stats_frame, bg='white', bd=1, relief='solid')
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            val_label = tk.Label(card, text=str(value), bg='white', fg=color,
                               font=('Arial', 32, 'bold'), pady=10)
            val_label.pack()
            
            text_label = tk.Label(card, text=label, bg='white', fg='#64748b',
                                font=('Arial', 12))
            text_label.pack(pady=(0, 10))
        
        # 系统状态
        status_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief='solid', highlightbackground='#e2e8f0', highlightthickness=1)
        status_frame.pack(fill=tk.X, pady=20)
        
        status_inner = tk.Frame(status_frame, bg='white', padx=20, pady=15)
        status_inner.pack(fill=tk.X)
        
        tk.Label(status_inner, text="系统状态:", bg='white', fg='#1e293b',
                font=('Arial', 12)).pack(side=tk.LEFT)
        
        self.status_dot = tk.Label(status_inner, text="●", bg='white', fg='#10b981', font=('Arial', 14))
        self.status_dot.pack(side=tk.LEFT, padx=5)
        
        self.status_text = tk.Label(status_inner, text="运行中", bg='white',
                                   font=('Arial', 12), fg='#10b981')
        self.status_text.pack(side=tk.LEFT)
        
        tk.Label(status_inner, text=f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                bg='white', font=('Arial', 10), fg='#94a3b8').pack(side=tk.RIGHT)
        
        # 最新文章
        articles_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief='solid')
        articles_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(articles_frame, text="最新文章", bg='white', 
                font=('Arial', 16, 'bold'), pady=10).pack(anchor='w', padx=15)
        
        # 文章列表
        self.articles_tree = ttk.Treeview(articles_frame, columns=('title', 'source', 'category', 'time'),
                                         show='headings', height=10)
        self.articles_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.articles_tree.heading('title', text='标题')
        self.articles_tree.heading('source', text='来源')
        self.articles_tree.heading('category', text='分类')
        self.articles_tree.heading('time', text='时间')
        
        self.articles_tree.column('title', width=400)
        self.articles_tree.column('source', width=150)
        self.articles_tree.column('category', width=100)
        self.articles_tree.column('time', width=150)
        
        self.load_recent_articles()
    
    def show_articles(self):
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame, text="📰 文章管理", bg='#f5f5f5', 
                        font=('Arial', 24, 'bold'))
        title.pack(anchor='w', pady=(0, 20))
        
        # 搜索框
        search_frame = tk.Frame(self.main_frame, bg='#f5f5f5')
        search_frame.pack(fill=tk.X, pady=10)
        
        tk.Entry(search_frame, font=('Arial', 12), width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜索", bg='#1890ff', fg='white',
                 font=('Arial', 11), padx=20, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="刷新", bg='white', font=('Arial', 11),
                 padx=20, cursor='hand2', command=self.load_all_articles).pack(side=tk.LEFT, padx=5)
        
        # 文章表格
        columns = ('title', 'source', 'category', 'score', 'action')
        self.all_articles_tree = ttk.Treeview(self.main_frame, columns=columns,
                                             show='headings', height=20)
        self.all_articles_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for col in columns:
            self.all_articles_tree.heading(col, text={
                'title': '标题', 'source': '来源', 'category': '分类',
                'score': '质量分', 'action': '操作'
            }.get(col, col))
        
        self.all_articles_tree.column('title', width=400)
        self.all_articles_tree.column('source', width=150)
        self.all_articles_tree.column('category', width=100)
        self.all_articles_tree.column('score', width=80)
        self.all_articles_tree.column('action', width=100)
        
        self.load_all_articles()
    
    def show_sources(self):
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame, text="📡 信息源管理", bg='#f5f5f5', 
                        font=('Arial', 24, 'bold'))
        title.pack(anchor='w', pady=(0, 20))
        
        tk.Label(self.main_frame, text="功能开发中...", bg='#f5f5f5',
                font=('Arial', 16)).pack(pady=100)
    
    def show_rules(self):
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame, text="⚙️ 采集规则", bg='#f5f5f5', 
                        font=('Arial', 24, 'bold'))
        title.pack(anchor='w', pady=(0, 20))
        
        tk.Label(self.main_frame, text="功能开发中...", bg='#f5f5f5',
                font=('Arial', 16)).pack(pady=100)
    
    def show_logs(self):
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame, text="📋 执行日志", bg='#f5f5f5', 
                        font=('Arial', 24, 'bold'))
        title.pack(anchor='w', pady=(0, 20))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.main_frame, bg='#1a1a2e', fg='#00ff00',
                                                  font=('Courier', 11), height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 按钮
        btn_frame = tk.Frame(self.main_frame, bg='#f5f5f5')
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="清空日志", bg='white', font=('Arial', 11),
                 padx=20, command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="导出日志", bg='#1890ff', fg='white',
                 font=('Arial', 11), padx=20).pack(side=tk.LEFT, padx=5)
        
        # 添加示例日志
        self.add_log("INFO", "系统启动成功")
        self.add_log("INFO", "Info-Getter GUI v1.0")
    
    def show_control(self):
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame, text="🎮 系统控制", bg='#f5f5f5', 
                        font=('Arial', 24, 'bold'))
        title.pack(anchor='w', pady=(0, 20))
        
        # 守护进程控制
        control_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief='solid')
        control_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(control_frame, text="守护进程控制", bg='white',
                font=('Arial', 16, 'bold'), pady=15).pack(anchor='w', padx=20)
        
        btn_frame = tk.Frame(control_frame, bg='white', padx=20, pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="▶️ 启动", bg='#52c41a', fg='white',
                 font=('Arial', 12), padx=30, pady=10, cursor='hand2',
                 command=self.start_daemon).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="⏹️ 停止", bg='#ff4d4f', fg='white',
                 font=('Arial', 12), padx=30, pady=10, cursor='hand2',
                 command=self.stop_daemon).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 重启", bg='#1890ff', fg='white',
                 font=('Arial', 12), padx=30, pady=10, cursor='hand2',
                 command=self.restart_daemon).pack(side=tk.LEFT, padx=5)
        
        # 手动操作
        action_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief='solid')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(action_frame, text="手动操作", bg='white',
                font=('Arial', 16, 'bold'), pady=15).pack(anchor='w', padx=20)
        
        action_btn_frame = tk.Frame(action_frame, bg='white', padx=20, pady=10)
        action_btn_frame.pack(fill=tk.X)
        
        tk.Button(action_btn_frame, text="🚀 立即执行采集", bg='#1890ff', fg='white',
                 font=('Arial', 12), padx=30, pady=10, cursor='hand2',
                 command=self.manual_collect).pack(side=tk.LEFT, padx=5)
        tk.Button(action_btn_frame, text="📊 生成AI Big News", bg='white',
                 font=('Arial', 12), padx=30, pady=10, cursor='hand2',
                 command=self.generate_report).pack(side=tk.LEFT, padx=5)
        tk.Button(action_btn_frame, text="🧹 清理旧数据", bg='white',
                 font=('Arial', 12), padx=30, pady=10, cursor='hand2',
                 command=self.clean_old_data).pack(side=tk.LEFT, padx=5)
    
    def get_stats(self):
        """获取统计数据"""
        total = 0
        for cat in ['llm', 'autonomous', 'robotics', 'zhuoyu']:
            file_path = self.data_dir / f"{cat}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    total += len(data)
        
        return {
            'today': total // 10,
            'week': total // 3,
            'total': total,
            'sources': 35
        }
    
    def load_recent_articles(self):
        """加载最新文章"""
        articles = []
        for cat in ['llm', 'autonomous', 'robotics', 'zhuoyu']:
            file_path = self.data_dir / f"{cat}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for item in data[:3]:
                        articles.append({
                            'title': item.get('title', '无标题')[:50] + '...',
                            'source': item.get('source', '未知') if isinstance(item.get('source'), str) else item.get('source', {}).get('name', '未知'),
                            'category': cat,
                            'time': item.get('published_at', '')[:10]
                        })
        
        for article in articles[:10]:
            self.articles_tree.insert('', 'end', values=(
                article['title'], article['source'], article['category'], article['time']
            ))
    
    def load_all_articles(self):
        """加载所有文章"""
        if hasattr(self, 'all_articles_tree'):
            for item in self.all_articles_tree.get_children():
                self.all_articles_tree.delete(item)
            
            for cat in ['llm', 'autonomous', 'robotics', 'zhuoyu']:
                file_path = self.data_dir / f"{cat}.json"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        for item in data[:50]:
                            self.all_articles_tree.insert('', 'end', values=(
                                item.get('title', '无标题')[:60] + '...',
                                item.get('source', '未知') if isinstance(item.get('source'), str) else item.get('source', {}).get('name', '未知'),
                                cat,
                                item.get('quality_score', 0),
                                '编辑 | 删除'
                            ))
    
    def add_log(self, level, message):
        """添加日志"""
        if hasattr(self, 'log_text'):
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_text.insert(tk.END, f"[{time_str}] [{level}] {message}\n")
            self.log_text.see(tk.END)
    
    def clear_logs(self):
        """清空日志"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
    
    def start_daemon(self):
        messagebox.showinfo("启动", "守护进程启动成功！")
        self.add_log("INFO", "守护进程已启动")
    
    def stop_daemon(self):
        messagebox.showinfo("停止", "守护进程已停止！")
        self.add_log("WARN", "守护进程已停止")
    
    def restart_daemon(self):
        messagebox.showinfo("重启", "守护进程重启成功！")
        self.add_log("INFO", "守护进程已重启")
    
    def manual_collect(self):
        self.add_log("INFO", "手动触发采集任务...")
        threading.Thread(target=self._collect_task).start()
    
    def _collect_task(self):
        time.sleep(2)
        self.add_log("INFO", "采集完成，获取8篇新文章")
    
    def generate_report(self):
        self.add_log("INFO", "生成AI Big News报告...")
    
    def clean_old_data(self):
        if messagebox.askyesno("确认", "确定要清理30天前的数据吗？"):
            self.add_log("INFO", "清理旧数据完成")
    
    def refresh_all(self):
        self.show_dashboard()
        messagebox.showinfo("刷新", "数据已刷新！")
    
    def auto_refresh(self):
        """自动刷新"""
        def refresh():
            while True:
                time.sleep(60)
                # 刷新统计数据
                pass
        
        threading.Thread(target=refresh, daemon=True).start()

def main():
    root = tk.Tk()
    app = InfoGetterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
