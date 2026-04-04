#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Key.txt 生成器模块
通过调用 ctags 自动提取 C 语言符号并生成 Key.txt
"""

import os
import subprocess
import tempfile
import click
from pathlib import Path


class KeyGenerator:
    """通过 ctags 生成 Key.txt 的类"""
    
    # ctags 符号类型映射
    # 格式: ctags_kind: (描述, token_type)
    # 注意：只包含原始脚本中定义的 'dseuxt' 类型
    SYMBOL_KINDS = {
        'd': ('宏定义', 'AUTO'),      # 宏定义 (define)
        's': ('结构体', 'AUTO'),      # 结构体 (struct)
        'e': ('枚举', 'AUTO'),        # 枚举 (enum)
        'u': ('联合体', 'AUTO'),      # 联合体 (union)
        'x': ('外部变量', 'AUTO'),    # 外部变量/函数声明 (extern)
        't': ('类型定义', 'AUTO'),    # typedef
    }
    
    def __init__(self, ctags_path=None, project_path=None, output_path=None):
        """
        初始化 KeyGenerator
        
        @param ctags_path: ctags 可执行文件路径，默认为项目目录下的 ctags
        @param project_path: 要扫描的项目目录，默认为当前目录
        @param output_path: Key.txt 输出路径，默认为当前目录下的 Key.txt
        """
        self.ctags_path = ctags_path or self._find_ctags()
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.output_path = Path(output_path) if output_path else Path('Key.txt')
        
    def _find_ctags(self):
        """查找 ctags 可执行文件"""
        # 首先检查项目目录下的 ctags
        script_dir = Path(__file__).parent.parent
        bundled_ctags = script_dir / 'ctags' / 'ctags.exe'
        if bundled_ctags.exists():
            return str(bundled_ctags)
        
        # 检查系统 PATH
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(['ctags', '--version'], capture_output=True, check=True, creationflags=creationflags)
            return 'ctags'
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        raise FileNotFoundError(
            "未找到 ctags 可执行文件。\n"
            "请确保 ctags 文件夹在项目目录中，\n"
            "或将 ctags 添加到系统 PATH。"
        )
    
    def _get_c_files(self):
        """获取项目中的所有 C 语言文件"""
        c_files = []
        exclude_dirs = {'build', 'obj', 'bin', '3rdparty', 'out', 'test', '.git', '.vscode', '__pycache__', 'venv', '.venv'}
        
        for root, dirs, files in os.walk(self.project_path):
            # 过滤掉排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(('.c', '.h', '.cpp', '.hpp', '.inc')):
                    full_path = os.path.join(root, file)
                    c_files.append(full_path)
        
        return c_files
    
    def _run_ctags(self, temp_file):
        """运行 ctags 生成符号索引"""
        # 要扫描的符号类型（与原始脚本 Extract-C-Symbols.ps1 中的 $TargetSymbolKinds = 'dseuxt' 保持一致）
        kinds = 'dseuxt'  # d=宏定义, s=结构体, e=枚举, u=联合体, x=外部变量, t=typedef
        
        # 获取所有 C 文件
        c_files = self._get_c_files()
        
        if not c_files:
            click.secho("[警告] 未找到任何 C 语言文件", fg='yellow')
            return
        
        click.secho(f"[1/3] 找到 {len(c_files)} 个 C 语言文件", fg='yellow')
        
        # 由于 Windows 命令行长度限制，分批处理
        batch_size = 50  # 每批处理 50 个文件
        all_symbols = []
        
        for i in range(0, len(c_files), batch_size):
            batch = c_files[i:i+batch_size]
            batch_temp = temp_file.parent / f"{temp_file.name}.batch{i}"
            
            cmd = [
                self.ctags_path,
                '--language-force=C',    # 强制使用 C 语言模式
                f'--c-kinds={kinds}',    # 指定要提取的符号类型
                '--excmd=number',        # 使用行号作为定位信息
                '-f', str(batch_temp),   # 输出到临时文件
            ]
            
            # 添加文件列表
            cmd.extend(batch)
            
            try:
                # Windows下隐藏控制台窗口
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=creationflags
                )
                # 读取这批的结果
                if batch_temp.exists():
                    with open(batch_temp, 'r', encoding='utf-8', errors='ignore') as f:
                        all_symbols.extend(f.readlines())
                    batch_temp.unlink()
            except Exception as e:
                click.secho(f"[警告] 处理批次 {i//batch_size + 1} 时出错: {e}", fg='yellow')
                continue
        
        # 合并所有结果到最终文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.writelines(all_symbols)
        
        click.secho(f"[1/3] 正在分析符号...", fg='yellow')
    
    def _parse_ctags_output(self, temp_file):
        """解析 ctags 输出文件"""
        symbols = {}
        
        if not temp_file.exists():
            return symbols
        
        with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # 跳过注释行
                if line.startswith('!_'):
                    continue
                
                # ctags 输出格式: symbol_name<TAB>file<TAB>line;<TAB>kind
                parts = line.split('\t')
                if len(parts) >= 4:
                    symbol_name = parts[0]
                    kind = parts[3]
                    
                    if kind in self.SYMBOL_KINDS:
                        if kind not in symbols:
                            symbols[kind] = []
                        symbols[kind].append(symbol_name)
        
        return symbols
    
    def _generate_key_file(self, symbols):
        """生成 Key.txt 文件"""
        click.secho(f"[2/3] 正在生成 Key.txt: {self.output_path}", fg='yellow')
        
        lines = []
        lines.append("# 自动生成的 Key.txt")
        lines.append(f"# 扫描目录: {self.project_path}")
        # 生成时间使用 datetime 代替，避免弹黑框
        from datetime import datetime
        gen_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f"# 生成时间: {gen_time}")
        lines.append("")
        
        total = 0
        for kind, kind_info in self.SYMBOL_KINDS.items():
            if kind in symbols and symbols[kind]:
                desc, token_type = kind_info
                lines.append(f"# {desc}")
                
                # 去重并排序
                unique_symbols = sorted(set(symbols[kind]))
                
                for symbol in unique_symbols:
                    lines.append(f"{symbol}={token_type}")
                    total += 1
                
                lines.append("")
        
        # 写入文件
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return total
    
    def generate(self):
        """生成 Key.txt 的主入口"""
        click.secho("=" * 50, fg='cyan')
        click.secho("    Key.txt 自动生成工具", fg='cyan')
        click.secho("=" * 50, fg='cyan')
        click.secho(f"ctags 路径: {self.ctags_path}", fg='green')
        click.secho(f"项目路径: {self.project_path}", fg='green')
        click.secho(f"输出路径: {self.output_path}", fg='green')
        click.secho("")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tags', delete=False) as tmp:
            temp_file = Path(tmp.name)
        
        try:
            # 步骤 1: 运行 ctags
            self._run_ctags(temp_file)
            
            # 步骤 2: 解析 ctags 输出
            symbols = self._parse_ctags_output(temp_file)
            
            if not symbols:
                click.secho("[警告] 未找到任何 C 语言符号", fg='yellow')
                return 0
            
            # 统计各类符号数量
            for kind, kind_info in self.SYMBOL_KINDS.items():
                if kind in symbols:
                    count = len(set(symbols[kind]))
                    click.secho(f"  找到 {kind_info[0]}: {count} 个", fg='green')
            
            # 步骤 3: 生成 Key.txt
            total = self._generate_key_file(symbols)
            
            click.secho("")
            click.secho("=" * 50, fg='cyan')
            click.secho(f"[3/3] 成功生成 Key.txt，共 {total} 个符号", fg='green')
            click.secho("=" * 50, fg='cyan')
            
            return total
            
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()


def update_key_file(project_path=None, output_path=None):
    """
    便捷函数：更新 Key.txt
    
    @param project_path: 项目目录，默认为当前工作目录
    @param output_path: Key.txt 输出路径，默认为 ./Key.txt
    @return: 生成的符号数量
    """
    generator = KeyGenerator(
        project_path=project_path,
        output_path=output_path
    )
    return generator.generate()


if __name__ == '__main__':
    # 测试
    update_key_file()
