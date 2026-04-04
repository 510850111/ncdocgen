#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ncdocgen GUI界面
提供图形化操作界面，避免命令行
"""

import os
import sys
import threading
import logging
import traceback
import datetime
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# 获取exe所在目录（支持打包后的路径）
# 当程序被打包为exe时，sys.frozen为True，此时使用sys.executable获取exe所在目录
# 当直接运行Python脚本时，使用当前文件所在目录
if getattr(sys, 'frozen', False):
    # 打包后的exe运行
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 直接运行python脚本
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 创建日志目录
# 日志文件保存在程序运行目录下的log文件夹中，按时间命名
LOG_DIR = os.path.join(BASE_DIR, 'log')
os.makedirs(LOG_DIR, exist_ok=True)

# 生成日志文件名（带时间戳）
# 格式：年月日_时分秒.log，例如：20260403_143022.log
log_filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'
LOG_FILE = os.path.join(LOG_DIR, log_filename)

# 配置 logging
# 日志同时输出到文件和控制台（stdout）
# 格式：时间 - [日志级别] - 消息
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 获取模块级logger实例
logger = logging.getLogger(__name__)
logger.info(f"程序启动，日志文件: {LOG_FILE}")
logger.info(f"工作目录: {BASE_DIR}")

# 添加项目路径到sys.path
# 确保可以正确导入visio和common等模块
sys.path.insert(0, BASE_DIR)

# 导入核心功能模块
# CMarddownDoc: Markdown文档生成器
# update_key_file: Key.txt更新器
from visio.cmarkdown import CMarddownDoc
from common.key_generator import update_key_file

# 项目信息常量
PROJECT_VERSION = "1.0.0"
PROJECT_URL = "https://github.com/510850111/ncdocgen"
PROJECT_AUTHOR = "Kuan He (何宽)"
PROJECT_AUTHOR_EMAIL = "hekuan_oscar@qq.com"
ORIGINAL_AUTHOR = "Kaikuo Zhuo"
ORIGINAL_URL = "https://gitee.com/kzhuo/ncdocgen"


class NcdocgenGUI:
    """
    ncdocgen图形界面主类
    
    负责创建和管理所有GUI组件，处理用户交互，协调后台任务。
    使用tkinter的grid布局系统，支持响应式窗口大小调整。
    """
    
    def __init__(self, root):
        """
        初始化GUI界面
        
        Args:
            root: tkinter根窗口实例
        """
        self.root = root
        self.root.title("ncdocgen - C文档生成器 v1.0.0")
        self.root.geometry("800x700")
        self.root.minsize(800, 650)
        
        # 配置样式
        # 定义Title.TLabel、Subtitle.TLabel和Action.TButton三种样式
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('微软雅黑', 14, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('微软雅黑', 10))
        self.style.configure('Action.TButton', font=('微软雅黑', 11))
        
        # 创建所有界面组件
        self._create_widgets()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器框架，带20像素的内边距
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置grid权重，使窗口可缩放
        # columnconfigure(1, weight=1) 使第1列（输入框所在列）可水平扩展
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky=(tk.W, tk.E))
        title_frame.columnconfigure(1, weight=1)  # 让中间区域可扩展
        
        title = ttk.Label(title_frame, text="📄 C文档生成器", style='Title.TLabel')
        title.grid(row=0, column=0, sticky=tk.W)
        
        # 版本号标签（右侧）
        version_label = ttk.Label(title_frame, text=f"v{PROJECT_VERSION}", 
                                  foreground='#0066cc', font=('微软雅黑', 9, 'bold'))
        version_label.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        
        subtitle = ttk.Label(main_frame, text="根据doxygen注释生成详细设计文档和PlantUML流程图", 
                            style='Subtitle.TLabel', foreground='gray')
        subtitle.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # === 输入文件选择 ===
        row = 3
        ttk.Label(main_frame, text="📂 输入文件:", font=('微软雅黑', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        # 输入文件变量和输入框（支持多个文件，用分号分隔）
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_var, font=('Consolas', 10))
        self.input_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(main_frame, text="浏览...", command=self._browse_input).grid(row=row, column=2, padx=5)
        
        # === 输出文件选择 ===
        row += 1
        ttk.Label(main_frame, text="💾 输出文件:", font=('微软雅黑', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        # 输出文件默认为工作目录下的 output.md
        self.output_var = tk.StringVar(value=os.path.join(BASE_DIR, "output.md"))
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_var, font=('Consolas', 10))
        self.output_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(main_frame, text="浏览...", command=self._browse_output).grid(row=row, column=2, padx=5)
        
        # === 项目路径（用于更新Key.txt） ===
        row += 1
        ttk.Label(main_frame, text="📁 项目路径:", font=('微软雅黑', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        # 项目路径默认为空，让用户选择自己的项目目录
        self.project_var = tk.StringVar(value="")
        self.project_entry = ttk.Entry(main_frame, textvariable=self.project_var, font=('Consolas', 10))
        self.project_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 项目路径浏览按钮 + 更新Key按钮（放在一起逻辑更清晰）
        project_btn_frame = ttk.Frame(main_frame)
        project_btn_frame.grid(row=row, column=2, padx=5)
        ttk.Button(project_btn_frame, text="浏览...", command=self._browse_project).pack(side=tk.LEFT, padx=(0, 2))
        # 根据Key.txt是否存在决定按钮文字
        # 如果Key.txt已存在，显示"🔄更新Key"；否则显示"➕生成Key"
        key_exists = os.path.exists(os.path.join(BASE_DIR, "Key.txt"))
        btn_text = "🔄更新Key" if key_exists else "➕生成Key"
        self.update_key_btn = ttk.Button(project_btn_frame, text=btn_text, command=self._update_key, width=10, state=tk.DISABLED)
        self.update_key_btn.pack(side=tk.LEFT)
        
        # 监听项目路径变化，控制更新Key按钮状态
        # 当项目路径变化时，调用_on_project_path_change方法更新按钮状态
        self.project_var.trace_add('write', self._on_project_path_change)
        
        # === Key.txt选择 ===
        row += 1
        ttk.Label(main_frame, text="🔑 key.txt文件:", font=('微软雅黑', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=10)
        
        # Key.txt 默认在工作目录，如果不存在则留空让用户选择
        default_key = os.path.join(BASE_DIR, "Key.txt")
        if not os.path.exists(default_key):
            default_key = ""  # 留空提示用户选择
        self.key_var = tk.StringVar(value=default_key)
        self.key_entry = ttk.Entry(main_frame, textvariable=self.key_var, font=('Consolas', 10))
        self.key_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(main_frame, text="浏览...", command=self._browse_key).grid(row=row, column=2, padx=5)
        
        # === 选项区域 ===
        row += 1
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        # 流程图深度设置
        # 控制流程图绘制的最大深度，默认为10
        self.depth_var = tk.IntVar(value=10)
        ttk.Label(options_frame, text="流程图深度:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Spinbox(options_frame, from_=1, to=50, textvariable=self.depth_var, width=5).pack(side=tk.LEFT, padx=(0, 20))
        
        # 详细日志开关
        # 勾选后切换到DEBUG日志级别，显示更多调试信息
        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="详细日志", variable=self.verbose_var, 
                       command=self._on_verbose_change).pack(side=tk.LEFT, padx=(0, 20))
        
        # 初始化日志级别
        # 根据verbose_var的初始值设置日志级别
        self._update_log_level()
        
        # PlantUML URL嵌入开关
        # 勾选后将PlantUML代码转换为在线图片URL嵌入到Markdown中
        self.embedded_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="嵌入PUML URL", variable=self.embedded_var).pack(side=tk.LEFT)
        
        # === 执行按钮 ===
        row += 1
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        # 开始生成文档按钮
        # 初始状态为禁用，只有当输入文件、输出文件和Key.txt都填写后才启用
        self.run_btn = ttk.Button(btn_frame, text="🚀 开始生成文档", command=self._run, 
                                  style='Action.TButton', padding="15 8", state=tk.DISABLED)
        self.run_btn.pack()
        
        # 监听关键变量变化，控制开始按钮状态
        # 当输入文件、输出文件或Key.txt变化时，检查是否满足启用条件
        self.input_var.trace_add('write', self._update_run_button_state)
        self.output_var.trace_add('write', self._update_run_button_state)
        self.key_var.trace_add('write', self._update_run_button_state)
        
        # === 日志输出区域 ===
        row += 1
        log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 带滚动条的日志文本框
        # 使用Consolas字体显示日志，高度为15行，自动换行
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD,
                                                   font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主frame的row权重，使日志区域可以扩展
        main_frame.rowconfigure(row, weight=1)
        
        # === 状态栏 ===
        row += 1
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)  # 让状态标签可扩展
        
        # 左侧状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, 
                               anchor=tk.W, padding="5 2")
        status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 右侧项目链接和关于按钮
        link_frame = ttk.Frame(status_frame)
        link_frame.grid(row=0, column=1, sticky=tk.E)
        
        # GitHub链接（蓝色下划线样式）
        github_link = tk.Label(link_frame, text="🌟 GitHub", foreground='#0066cc', 
                               cursor='hand2', font=('微软雅黑', 9, 'underline'))
        github_link.pack(side=tk.LEFT, padx=(0, 10))
        github_link.bind('<Button-1>', lambda e: self._open_url(PROJECT_URL))
        github_link.bind('<Enter>', lambda e: github_link.config(foreground='#003d7a'))
        github_link.bind('<Leave>', lambda e: github_link.config(foreground='#0066cc'))
        
        # 关于按钮
        about_btn = ttk.Button(link_frame, text="ℹ️ 关于", command=self._show_about, width=8)
        about_btn.pack(side=tk.LEFT)
        
        # 初始检查按钮状态
        # 根据当前输入值判断是否启用"开始生成文档"按钮
        self._update_run_button_state()
        
    def _log(self, message):
        """添加日志（线程安全）"""
        def update_log():
            """实际执行GUI更新的内部函数"""
            try:
                # 检查文本框是否还存在（窗口可能已关闭）
                if self.log_text and self.log_text.winfo_exists():
                    self.log_text.insert(tk.END, message + "\n")
                    self.log_text.see(tk.END)
            except tk.TclError:
                pass  # 窗口已关闭
        
        # 在主线程中执行 GUI 更新
        # 如果不是主线程，使用root.after(0, ...)将任务调度到主线程
        if threading.current_thread() is threading.main_thread():
            update_log()
        else:
            self.root.after(0, update_log)
        
    def _browse_input(self):
        """浏览输入文件"""
        # 弹出多文件选择对话框，支持选择多个.c/.h文件
        files = filedialog.askopenfilenames(
            title="选择C源文件",
            filetypes=[("C源文件", "*.c"), ("头文件", "*.h"), ("所有文件", "*.*")]
        )
        if files:
            # 多个文件用分号分隔
            self.input_var.set(";".join(files))
            
    def _browse_output(self):
        """浏览输出文件"""
        # 弹出保存文件对话框，默认后缀为.md
        file = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        if file:
            self.output_var.set(file)
            
    def _browse_key(self):
        """浏览Key.txt文件"""
        # Key.txt文件包含C语言关键字定义，用于区分用户标识符和关键字
        file = filedialog.askopenfilename(
            title="选择Key.txt文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file:
            self.key_var.set(file)
            
    def _browse_project(self):
        """浏览项目路径"""
        # 弹出目录选择对话框，选择的目录将用于扫描生成Key.txt
        dir_path = filedialog.askdirectory(title="选择项目目录（用于更新Key.txt）")
        if dir_path:
            self.project_var.set(dir_path)
    
    def _on_project_path_change(self, *args):
        """项目路径变化时更新更新Key按钮状态"""
        project_path = self.project_var.get().strip()
        # 只有路径有效且存在时才启用更新Key按钮
        if project_path and os.path.isdir(project_path):
            self.update_key_btn.config(state=tk.NORMAL)
        else:
            self.update_key_btn.config(state=tk.DISABLED)
        # 项目路径变化也影响开始按钮状态
        self._update_run_button_state()
    
    def _update_run_button_state(self, *args):
        """更新开始生成文档按钮的状态"""
        has_input = bool(self.input_var.get().strip())
        has_output = bool(self.output_var.get().strip())
        has_key = bool(self.key_var.get().strip())
        
        # 三个条件都满足时才启用按钮
        if has_input and has_output and has_key:
            self.run_btn.config(state=tk.NORMAL)
        else:
            self.run_btn.config(state=tk.DISABLED)
    
    def _on_verbose_change(self):
        """详细日志复选框变化时更新日志级别"""
        self._update_log_level()
    
    def _update_log_level(self):
        """根据详细日志选项设置日志级别"""
        # 勾选详细日志: DEBUG级别（显示所有日志）
        # 不勾选详细日志: INFO级别（只显示关键信息）
        if self.verbose_var.get():
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("切换到详细日志模式 (DEBUG)")
        else:
            logging.getLogger().setLevel(logging.INFO)
            logger.info("切换到标准日志模式 (INFO)")
            
    def _update_key(self):
        """更新Key.txt"""
        project_path = self.project_var.get().strip()
        # Key.txt始终生成在exe所在目录（工作目录）
        key_file = os.path.join(BASE_DIR, "Key.txt")
        
        logger.info("=" * 60)
        logger.info("开始更新 Key.txt")
        logger.info(f"项目路径: {project_path}")
        logger.info(f"输出文件: {key_file}")
        
        if not os.path.isdir(project_path):
            logger.error(f"项目路径不存在: {project_path}")
            messagebox.showerror("错误", f"项目路径不存在: {project_path}")
            return
            
        self._log(f"正在更新 Key.txt...")
        self._log(f"项目路径: {project_path}")
        self._log(f"输出文件: {key_file}")
        self.status_var.set("正在更新 Key.txt...")
        self.run_btn.config(state=tk.DISABLED)
        
        def do_update():
            """后台线程执行的更新操作"""
            try:
                logger.info("调用 update_key_file...")
                count = update_key_file(
                    project_path=project_path,
                    output_path=key_file
                )
                logger.info(f"Key.txt 更新完成，共 {count} 个符号")
                # 成功后回调_update_key_done
                self.root.after(0, lambda: self._update_key_done(count, key_file))
            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"更新Key.txt失败: {e}")
                logger.error(f"详细错误:\n{error_trace}")
                # 失败后回调_update_key_error
                self.root.after(0, lambda: self._update_key_error(f"{e}\n\n详情请查看日志: {LOG_FILE}"))
                
        # 启动后台线程，避免阻塞GUI
        threading.Thread(target=do_update, daemon=True).start()
        
    def _update_key_done(self, count, key_file):
        """更新Key.txt完成"""
        logger.info(f"Key.txt 更新成功: {count} 个符号")
        self._log(f"✅ Key.txt 更新成功！共 {count} 个符号")
        self.status_var.set(f"Key.txt 更新成功 ({count} 个符号)")
        # 更新关键字文件栏（会自动触发_update_run_button_state检查按钮状态）
        self.key_var.set(key_file)
        # 更新按钮文字为"更新Key"（因为文件已生成）
        self.update_key_btn.config(text="🔄更新Key")
        messagebox.showinfo("成功", f"Key.txt 更新成功！\n共 {count} 个符号")
        
    def _update_key_error(self, error):
        """更新Key.txt出错"""
        logger.error(f"Key.txt 更新失败: {error}")
        self._log(f"❌ 更新失败: {error}")
        self._log(f"详情请查看日志: {LOG_FILE}")
        self.status_var.set("更新失败")
        # 按钮状态由_update_run_button_state统一管理
        messagebox.showerror("错误", f"更新Key.txt失败:\n{error}")
        
    def _run(self):
        """执行文档生成"""
        input_files = self.input_var.get()
        output_file = self.output_var.get()
        key_file = self.key_var.get()
        depth = self.depth_var.get()
        verbose = self.verbose_var.get()
        embedded = self.embedded_var.get()
        
        logger.info("=" * 60)
        logger.info("开始文档生成任务")
        logger.info(f"输入文件: {input_files}")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"关键字文件: {key_file}")
        logger.info(f"流程图深度: {depth}")
        logger.info(f"详细输出: {verbose}")
        logger.info(f"嵌入PUML: {embedded}")
        logger.info("=" * 60)
        
        # 验证输入
        if not input_files:
            logger.error("未选择输入文件")
            messagebox.showerror("错误", "请选择输入文件")
            return
            
        # 解析输入文件列表
        # 支持分号和逗号分隔的多个文件路径
        file_list = [f.strip() for f in input_files.replace(';', ',').split(',') if f.strip()]
        logger.info(f"解析到 {len(file_list)} 个输入文件")
        
        # 检查文件是否存在
        for f in file_list:
            if not os.path.isfile(f):
                logger.error(f"文件不存在: {f}")
                messagebox.showerror("错误", f"文件不存在: {f}")
                return
            logger.info(f"文件检查通过: {f}")
                
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            logger.info(f"创建输出目录: {output_dir}")
            os.makedirs(output_dir)
        
        # 检查Key.txt是否存在
        if not os.path.exists(key_file):
            logger.warning(f"Key.txt 不存在: {key_file}")
            self._log(f"⚠️ 警告: Key.txt 不存在，将使用默认值")
            
        self._log("=" * 50)
        self._log("开始生成文档...")
        self._log(f"输入文件: {len(file_list)} 个")
        self._log(f"输出文件: {output_file}")
        self._log(f"关键字文件: {key_file}")
        self._log(f"流程图深度: {depth}")
        self._log("=" * 50)
        
        self.status_var.set("正在生成文档...")
        self.run_btn.config(state=tk.DISABLED)
        
        def do_run():
            """后台线程执行的文档生成操作"""
            try:
                logger.info("初始化 CMarddownDoc...")
                # 构建参数字典
                amap = {'verbose': verbose, 'debug': False, 'depth': depth}
                # 创建文档生成器
                doc = CMarddownDoc(amap,
                                   keyword_file=key_file,
                                   output_fname=output_file,
                                   embedded=embedded)
                logger.info(f"开始解析 {len(file_list)} 个文件...")
                # 解析所有输入文件
                doc.parse_files(file_list)
                logger.info("解析完成，开始保存...")
                # 保存输出文件
                doc.save(output_file)
                logger.info(f"文档已保存: {output_file}")
                # 成功后回调_run_done
                self.root.after(0, lambda: self._run_done(output_file))
            except Exception as e:
                error_msg = str(e)
                error_trace = traceback.format_exc()
                logger.error(f"文档生成失败: {error_msg}")
                logger.error(f"详细错误:\n{error_trace}")
                # 失败后回调_run_error
                self.root.after(0, lambda: self._run_error(f"{error_msg}\n\n详情请查看日志: {LOG_FILE}"))
                
        # 启动后台线程，避免阻塞GUI界面
        threading.Thread(target=do_run, daemon=True).start()
        
    def _run_done(self, output_file):
        """执行完成"""
        logger.info("文档生成任务完成")
        self._log("=" * 50)
        self._log("✅ 文档生成成功！")
        self._log(f"📄 输出文件: {output_file}")
        self._log("=" * 50)
        self.status_var.set("文档生成成功")
        self.run_btn.config(state=tk.NORMAL)
        
        # 打开资源管理器并选中输出文件
        if os.path.exists(output_file):
            try:
                # 使用 explorer /select 打开资源管理器并选中文件
                subprocess.run(['explorer', '/select,', os.path.normpath(output_file)], check=False)
            except Exception as e:
                logger.warning(f"打开资源管理器失败: {e}")
        
        # 弹框提示成功
        messagebox.showinfo("成功", f"文档生成成功！\n\n📄 {output_file}")
        
    def _run_error(self, error):
        """执行出错"""
        logger.error(f"文档生成失败: {error}")
        self._log(f"❌ 错误: {error}")
        self._log(f"详情请查看日志: {LOG_FILE}")
        self.status_var.set("生成失败")
        self.run_btn.config(state=tk.NORMAL)
        messagebox.showerror("错误", f"文档生成失败:\n{error}")
    
    def _open_url(self, url):
        """
        使用默认浏览器打开URL
        
        Args:
            url: 要打开的网址
        """
        import webbrowser
        webbrowser.open(url)
        logger.info(f"打开链接: {url}")
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📄 ncdocgen - C文档生成器 v{PROJECT_VERSION}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：
  • 根据 doxygen 风格注释自动生成文档
  • 自动绘制 PlantUML 流程图
  • 支持 Markdown 格式输出

当前维护者：
  {PROJECT_AUTHOR}
  📧 {PROJECT_AUTHOR_EMAIL}

原作者：
  {ORIGINAL_AUTHOR}
  🏠 {ORIGINAL_URL}

项目地址：
  {PROJECT_URL}

许可证：MIT License

© 2024-2026 Kuan He | 2012-2024 Kaikuo Zhuo
        """.strip()
        
        # 创建自定义关于对话框
        about_win = tk.Toplevel(self.root)
        about_win.title("关于 ncdocgen")
        about_win.geometry("450x420")
        about_win.resizable(False, False)
        about_win.transient(self.root)  # 设置为父窗口的临时窗口
        about_win.grab_set()  # 模态对话框
        
        # 居中显示
        about_win.update_idletasks()
        x = (about_win.winfo_screenwidth() - 450) // 2
        y = (about_win.winfo_screenheight() - 420) // 2
        about_win.geometry(f"+{x}+{y}")
        
        # 内容区域
        content_frame = ttk.Frame(about_win, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标和标题
        title_label = ttk.Label(content_frame, text="📄 ncdocgen", 
                                font=('微软雅黑', 18, 'bold'))
        title_label.pack(pady=(0, 5))
        
        version_label = ttk.Label(content_frame, text=f"版本 {PROJECT_VERSION}",
                                  font=('微软雅黑', 10), foreground='#666')
        version_label.pack(pady=(0, 15))
        
        # 分隔线
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 功能说明
        desc_text = """根据 doxygen 风格注释自动生成详细设计文档
支持 PlantUML 流程图和 Markdown 格式输出"""
        desc_label = ttk.Label(content_frame, text=desc_text, 
                               font=('微软雅黑', 9), justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # 分隔线
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 作者信息
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        # 当前维护者
        ttk.Label(info_frame, text="当前维护者:", font=('微软雅黑', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(info_frame, text=PROJECT_AUTHOR, font=('微软雅黑', 9)).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(info_frame, text=PROJECT_AUTHOR_EMAIL, font=('微软雅黑', 9), foreground='#0066cc').grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 原作者
        ttk.Label(info_frame, text="原作者:", font=('微软雅黑', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        ttk.Label(info_frame, text=ORIGINAL_AUTHOR, font=('微软雅黑', 9)).grid(row=2, column=1, sticky=tk.W, padx=5, pady=(10, 0))
        # 原作者项目链接（可点击）
        original_link = tk.Label(info_frame, text="访问原项目主页", foreground='#0066cc',
                                 cursor='hand2', font=('微软雅黑', 9, 'underline'))
        original_link.grid(row=3, column=1, sticky=tk.W, padx=5)
        original_link.bind('<Button-1>', lambda e: self._open_url(ORIGINAL_URL))
        original_link.bind('<Enter>', lambda e: original_link.config(foreground='#003d7a'))
        original_link.bind('<Leave>', lambda e: original_link.config(foreground='#0066cc'))
        
        # GitHub链接（可点击）
        link_frame = ttk.Frame(content_frame)
        link_frame.pack(pady=10)
        
        github_label = tk.Label(link_frame, text="🌟 访问 GitHub 项目主页", 
                                foreground='#0066cc', cursor='hand2',
                                font=('微软雅黑', 9, 'underline'))
        github_label.pack()
        github_label.bind('<Button-1>', lambda e: self._open_url(PROJECT_URL))
        github_label.bind('<Enter>', lambda e: github_label.config(foreground='#003d7a'))
        github_label.bind('<Leave>', lambda e: github_label.config(foreground='#0066cc'))
        
        # 许可证
        license_label = ttk.Label(content_frame, text="MIT License © 2024-2026 Kuan He | 2012-2024 Kaikuo Zhuo",
                                  font=('微软雅黑', 8), foreground='#999')
        license_label.pack(pady=(10, 0))
        
        # 分隔线
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 确定按钮
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        ok_btn = tk.Button(btn_frame, text="  确定  ", command=about_win.destroy, 
                           width=10, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        ok_btn.pack()


def main():
    """GUI程序入口函数"""
    root = tk.Tk()
    app = NcdocgenGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
