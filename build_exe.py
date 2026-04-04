#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本：将 ncdocgen 打包为 exe 文件

功能说明:
    使用 PyInstaller 将 Python 脚本打包为 Windows 可执行文件(EXE)
    支持自动安装 PyInstaller、清理临时文件、包含 ctags 工具等

用法:
    python build_exe.py

输出:
    dist/ncdocgen.exe - 单文件可执行程序

作者: ncdocgen团队
"""

import os
import sys
import subprocess
import shutil


def clean_all():
    """
    清理所有临时文件和旧构建
    
    在打包开始前清理以下文件/目录:
    - build/: PyInstaller 构建目录
    - ncdocgen_portable/: 旧便携版目录（如果存在）
    - *.spec: PyInstaller 生成的 spec 文件
    """
    items_to_remove = [
        'build',           # PyInstaller 构建目录
        'ncdocgen_portable',  # 旧便携版目录
    ]
    
    print("清理临时文件...")
    for item in items_to_remove:
        if os.path.exists(item):
            print(f"  删除 {item}/")
            shutil.rmtree(item)
    
    # 清理 spec 文件
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            print(f"  删除 {f}")
            os.remove(f)
    
    print("清理完成\n")


def build_exe():
    """
    使用 PyInstaller 打包
    
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
    
    # 检查 PyInstaller 是否已安装
    # 如果未安装，自动使用 pip 安装
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("PyInstaller 安装完成")
    
    print("\n开始打包...\n")
    
    # PyInstaller 参数
    args = [
        'pyinstaller',
        '--name=ncdocgen',            # exe 名称
        '--onefile',                  # 打包为单个文件
        '--windowed',                 # GUI 模式
        '--icon=NONE',                # 无图标
        '--add-data=ctags;ctags',     # 包含 ctags
        '--clean',                    # 清理临时文件
        '--noconfirm',                # 不确认覆盖
        '--log-level=INFO',           # 日志级别
        'gui.py',                     # 入口文件
    ]
    
    # 执行打包命令
    # capture_output=False 表示将 PyInstaller 的输出直接显示在控制台
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
    print("\n清理打包临时文件...")
    
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
    1. 显示标题
    2. 清理旧构建
    3. 执行打包
    4. 清理临时文件
    5. 显示结果
    """
    print("=" * 50)
    print("ncdocgen EXE 打包工具")
    print("=" * 50)
    print()
    
    # 清理旧构建
    clean_all()
    
    # 打包
    if build_exe():
        # 打包成功后清理临时文件
        cleanup_after_build()
        
        print("=" * 50)
        print("打包成功！")
        print("=" * 50)
        print(f"\n输出文件: dist\\ncdocgen.exe")
        print("\n使用说明:")
        print("1. dist\\ncdocgen.exe 可直接复制到任意位置使用")
        print("2. 首次使用请先生成 Key.txt")
        print("3. 运行后会自动创建 log/ 目录存放日志")
    else:
        print("\n打包失败！请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
