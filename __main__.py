#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ncdocgen 入口模块
支持命令行和GUI两种模式

用法:
    python -m ncdocgen              # 启动GUI
    python -m ncdocgen --cli ...    # 使用命令行模式
    python -m ncdocgen -h           # 查看帮助

运行模式说明:
    1. 无参数: 启动GUI界面
    2. 有参数但未指定--cli: 启动GUI并预填充参数
    3. 指定--cli: 使用纯命令行模式

作者: ncdocgen团队
"""

import sys
import argparse


def main():
    """
    程序主入口函数
    
    解析命令行参数，决定启动GUI还是命令行模式。
    """
    # 创建参数解析器
    # RawDescriptionHelpFormatter 保留epilog中的换行格式
    parser = argparse.ArgumentParser(
        description='ncdocgen - C文档生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  启动GUI界面:
    python -m ncdocgen
    
  命令行模式:
    python -m ncdocgen --cli code.c -o out.md -k Key.txt
    
  更新Key.txt:
    python -m ncdocgen --update-key --project-path ./code
        """
    )
    
    # 定义命令行参数
    parser.add_argument('--cli', action='store_true',
                       help='使用命令行模式（默认启动GUI）')
    parser.add_argument('filelist', nargs='*',
                       help='输入的C文件列表')
    parser.add_argument('-o', '--output', default='./out/output.md',
                       help='输出文件路径')
    parser.add_argument('-k', '--keyword', default='Key.txt',
                       help='关键字文件路径')
    parser.add_argument('-u', '--update-key', action='store_true',
                       help='更新Key.txt')
    parser.add_argument('--project-path', default='.',
                       help='项目路径（用于更新Key.txt）')
    parser.add_argument('-d', '--depth', type=int, default=10,
                       help='流程图深度（默认10）')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有参数，启动GUI
    # 或者只有-h/--help参数，也启动GUI（显示帮助后会退出）
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        if len(sys.argv) == 1:
            # 无参数，启动GUI
            from gui import main as gui_main
            gui_main()
            return
    
    # 有参数但没指定--cli，启动GUI并传递参数
    # 这种模式允许用户通过命令行参数快速启动GUI并预填充值
    if not args.cli and len(sys.argv) > 1:
        import tkinter as tk
        from gui import NcdocgenGUI
        
        root = tk.Tk()
        app = NcdocgenGUI(root)
        
        # 将命令行参数设置到GUI界面对应的变量
        # 这样用户可以在GUI中看到预填充的值，也可以修改
        if args.filelist:
            app.input_var.set(';'.join(args.filelist))
        if args.output:
            app.output_var.set(args.output)
        if args.keyword:
            app.key_var.set(args.keyword)
        if args.project_path:
            app.project_var.set(args.project_path)
        app.depth_var.set(args.depth)
        app.verbose_var.set(args.verbose)
        
        root.mainloop()
        return
    
    # 命令行模式
    # 导入cdocgen模块的draw函数，传入解析后的参数
    from cdocgen import draw
    draw(
        output=args.output,
        keyword=args.keyword,
        debug=False,
        verbose=args.verbose,
        embedded=False,
        depth=args.depth,
        update_key=args.update_key,
        project_path=args.project_path,
        filelist=args.filelist
    )


if __name__ == '__main__':
    main()
