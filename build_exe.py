#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本：将 ncdocgen 打包为 exe 文件

功能说明:
    使用 PyInstaller 将 Python 脚本打包为 Windows 可执行文件(EXE)
    支持自动安装 PyInstaller、清理临时文件、包含 ctags 工具等
    支持打包 GUI 版本和 CLI 版本

用法:
    python build_exe.py              # 打包 GUI+CLI 版本（默认）
    python build_exe.py --gui        # 打包 GUI 版本
    python build_exe.py --cli        # 打包 CLI 版本
    python build_exe.py --all        # 同时打包 GUI 和 CLI 版本

输出:
    dist/ncdocgen.exe      - GUI 可执行程序
    dist/ncdocgen-cli.exe  - CLI 可执行程序

作者: ncdocgen团队
"""

import os
import sys
import subprocess
import shutil
import argparse


def clean_all():
    """
    清理所有临时文件和旧构建
    
    在打包开始前清理以下文件/目录:
    - build/: PyInstaller 构建目录
    - dist/: 旧的输出目录（确保干净构建）
    - ncdocgen_portable/: 旧便携版目录（如果存在）
    - *.spec: PyInstaller 生成的 spec 文件
    - __pycache__/: Python 缓存目录
    - .pytest_cache/: pytest 缓存
    """
    items_to_remove = [
        'build',              # PyInstaller 构建目录
        'dist',               # 旧的输出目录
        'ncdocgen_portable',  # 旧便携版目录
    ]
    
    print("=" * 50)
    print("清理临时文件和缓存...")
    print("=" * 50)
    
    # 删除主要目录
    for item in items_to_remove:
        if os.path.exists(item):
            print(f"  删除 {item}/")
            shutil.rmtree(item)
    
    # 清理 spec 文件
    spec_count = 0
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            print(f"  删除 {f}")
            os.remove(f)
            spec_count += 1
    
    # 清理 Python 缓存
    cache_dirs = []
    for root, dirs, files in os.walk('.'):
        # 跳过虚拟环境目录
        if 'venv' in root or '.venv' in root or 'env' in root or '__pycache__' in root:
            continue
        for d in dirs:
            if d == '__pycache__' or d == '.pytest_cache':
                cache_path = os.path.join(root, d)
                cache_dirs.append(cache_path)
    
    for cache_dir in cache_dirs:
        print(f"  删除 {cache_dir}")
        shutil.rmtree(cache_dir)
    
    print(f"\n清理完成（删除 {len(items_to_remove) + spec_count + len(cache_dirs)} 个项目）\n")


def check_pyinstaller():
    """
    检查并安装 PyInstaller
    """
    try:
        import PyInstaller
        print("PyInstaller 已安装")
        return True
    except ImportError:
        print("正在安装 PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("PyInstaller 安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"安装 PyInstaller 失败: {e}")
            return False


def build_gui():
    """
    打包 GUI 版本
    
    打包配置说明:
        --name=ncdocgen:     输出的 exe 文件名
        --onefile:           打包为单个文件（便于分发）
        --windowed:          GUI模式（不显示控制台窗口）
        --icon=NONE:         不使用图标
        --add-data=ctags;ctags: 将 ctags 目录包含到打包中
        --clean:             清理 PyInstaller 缓存
        --noconfirm:         覆盖现有文件时不提示
        --log-level=INFO:    设置日志级别为 INFO
        gui.py:              程序入口文件
    
    Returns:
        bool: 打包成功返回 True，失败返回 False
    """
    print("\n" + "=" * 50)
    print("开始打包 GUI 版本...")
    print("=" * 50 + "\n")
    
    args = [
        'pyinstaller',
        '--name=ncdocgen',            # exe 名称
        '--onefile',                  # 打包为单个文件
        '--windowed',                 # GUI 模式（无控制台窗口）
        '--icon=NONE',                # 无图标
        '--add-data=ctags;ctags',     # 包含 ctags
        '--clean',                    # 清理 PyInstaller 缓存
        '--noconfirm',                # 不确认覆盖
        '--log-level=INFO',           # 日志级别
        'gui.py',                     # 入口文件
    ]
    
    result = subprocess.run(args, capture_output=False, text=True)
    return result.returncode == 0


def build_cli():
    """
    打包 CLI 版本
    
    打包配置说明:
        --name=ncdocgen-cli: 输出的 exe 文件名
        --onefile:           打包为单个文件（便于分发）
        --console:           CLI模式（显示控制台窗口）
        --icon=NONE:         不使用图标
        --add-data=ctags;ctags: 将 ctags 目录包含到打包中
        --clean:             清理 PyInstaller 缓存
        --noconfirm:         覆盖现有文件时不提示
        --log-level=INFO:    设置日志级别为 INFO
        cdocgen.py:          程序入口文件
    
    Returns:
        bool: 打包成功返回 True，失败返回 False
    """
    print("\n" + "=" * 50)
    print("开始打包 CLI 版本...")
    print("=" * 50 + "\n")
    
    args = [
        'pyinstaller',
        '--name=ncdocgen-cli',        # exe 名称
        '--onefile',                  # 打包为单个文件
        '--console',                  # CLI 模式（显示控制台窗口）
        '--icon=NONE',                # 无图标
        '--add-data=ctags;ctags',     # 包含 ctags
        '--clean',                    # 清理 PyInstaller 缓存
        '--noconfirm',                # 不确认覆盖
        '--log-level=INFO',           # 日志级别
        'cdocgen.py',                 # 入口文件
    ]
    
    result = subprocess.run(args, capture_output=False, text=True)
    return result.returncode == 0


def cleanup_after_build():
    """
    打包完成后清理临时文件
    
    删除打包过程中生成的临时文件和目录:
    - build/: PyInstaller 构建目录
    - *.spec: PyInstaller 配置文件
    
    注意: 保留 dist/ 目录，因为其中包含最终的 exe 文件
    """
    print("\n" + "=" * 50)
    print("清理打包临时文件...")
    print("=" * 50)
    
    items_to_remove = [
        'build',           # 构建目录
    ]
    
    for item in items_to_remove:
        if os.path.exists(item):
            print(f"  删除 {item}/")
            shutil.rmtree(item)
    
    # 清理 spec 文件
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            print(f"  删除 {f}")
            os.remove(f)
    
    print("临时文件清理完成\n")


def main():
    """
    主函数
    
    打包流程:
    1. 解析命令行参数
    2. 显示标题
    3. 清理缓存和旧构建
    4. 执行打包（GUI/CLI/全部）
    5. 清理临时文件
    6. 显示结果
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='ncdocgen EXE 打包工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python build_exe.py         # 同时打包 GUI + CLI 版本（默认）
  python build_exe.py --gui   # 只打包 GUI 版本
  python build_exe.py --cli   # 只打包 CLI 版本
  python build_exe.py --all   # 同时打包 GUI + CLI 版本
        '''
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--gui', action='store_true', help='只打包 GUI 版本')
    group.add_argument('--cli', action='store_true', help='只打包 CLI 版本')
    group.add_argument('--all', action='store_true', help='同时打包 GUI 和 CLI 版本（默认）')
    
    args = parser.parse_args()
    
    # 确定打包模式（默认打包双版本）
    if args.gui:
        # 只打包 GUI
        build_gui_flag = True
        build_cli_flag = False
    elif args.cli:
        # 只打包 CLI
        build_gui_flag = False
        build_cli_flag = True
    else:
        # 默认或 --all：打包双版本
        build_gui_flag = True
        build_cli_flag = True
    
    # 显示标题
    print("=" * 50)
    print("ncdocgen EXE 打包工具")
    print("=" * 50)
    
    if args.all:
        print("模式: 打包 GUI + CLI 版本")
    elif args.cli:
        print("模式: 只打包 CLI 版本")
    else:
        print("模式: 只打包 GUI 版本")
    print()
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        sys.exit(1)
    
    # 清理旧构建和缓存
    clean_all()
    
    # 执行打包
    success_count = 0
    total_count = 0
    
    if build_gui_flag:
        total_count += 1
        if build_gui():
            success_count += 1
            print("\n[✓] GUI 版本打包成功")
        else:
            print("\n[✗] GUI 版本打包失败")
    
    if build_cli_flag:
        total_count += 1
        if build_cli():
            success_count += 1
            print("\n[✓] CLI 版本打包成功")
        else:
            print("\n[✗] CLI 版本打包失败")
    
    # 打包完成后清理临时文件
    cleanup_after_build()
    
    # 显示结果
    print("=" * 50)
    if success_count == total_count:
        print("打包全部成功！")
        print("=" * 50)
        print("\n输出文件:")
        if build_gui_flag and os.path.exists('dist/ncdocgen.exe'):
            print(f"  - dist\\ncdocgen.exe     (GUI 版本)")
        if build_cli_flag and os.path.exists('dist/ncdocgen-cli.exe'):
            print(f"  - dist\\ncdocgen-cli.exe  (CLI 版本)")
        print("\n使用说明:")
        print("  - GUI 版本: 双击运行，图形界面操作")
        print("  - CLI 版本: 命令行使用，支持所有命令行参数")
        print("  - 首次使用请先生成 Key.txt")
    else:
        print(f"打包完成: {success_count}/{total_count} 成功")
        print("=" * 50)
        if success_count < total_count:
            sys.exit(1)


if __name__ == '__main__':
    main()
