#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ncdocgen 命令行入口模块
======================
提供基于Click库的命令行界面，支持在终端中直接使用ncdocgen。

主要功能:
    - 解析命令行参数
    - 支持更新Key.txt
    - 生成Markdown文档
    - 配置流程图深度、详细输出等选项

使用示例:
    python cdocgen.py code.c -o output.md
    python cdocgen.py *.c -k Key.txt -v
    python cdocgen.py --update-key --project-path ./src

作者: ncdocgen团队
版本: v1.0.0
"""

import logging
import click
import os

# 导入核心功能模块
# CMarddownDoc: Markdown文档生成器，负责解析C文件并生成文档
# update_key_file: Key.txt更新器，通过ctags扫描项目生成关键字文件
from visio.cmarkdown import CMarddownDoc
from common.key_generator import update_key_file

# =============================================================================
# 版本信息
# =============================================================================

# 历史版本记录（供参考）
# __version__ = "0.3.10.2020.4.25"   # 修复全局变量识别中首字母大写的bug
# __version__ = "0.3.11.2020.9.16"   # 增加STATIC容忍,修复参数成员变量误识别
# __version__ = "0.3.12.2022.3.25"   # 增加plantuml
# __version__ = "0.3.13.2023.3.26"   # plantuml增加break
# __version__ = "0.4.0a"             # 支持python3
# __version__ = "0.4.0b"             # 使用click库，增加gui程序
# __version__ = "0.4.1.2023.11.13"   # 优化多重label case，解决bug1-5
# __version__ = "0.4.1.2023.11.19"   # 优化命令行提示
__version__ = "1.0.0"    # 首个GitHub发布版本

main_version = __version__


def usage():
    """
    生成使用说明字符串
    
    Returns:
        str: 格式化的使用说明文本
    """
    usagestr = r"""
从C语言中的doxygen注释(/*- */)生成详细设计文件。支持自动绘制plantuml流程图，并生成函数说明表，支持全局变量说明。

By <kaikuo.zhuo@hotmail.com>, 2012-2015,2017,2022-2023

By <kuan.he@bj-tct.com>, 2026 v%s

[FILELIST] 文件名说明:
    支持 *.c, ??.c 通配符，支持通配符组合，如: "1.c module\*.c"等
""" % main_version
    return usagestr


# =============================================================================
# 主命令定义
# =============================================================================

@click.command(help=usage())
@click.option(
    '-o', '--output', 
    default='./out/auto_output.md', 
    help='输出的md文件路径'
)
@click.option(
    '-k', '--keyword', 
    default='', 
    help='关键字文件(Key.txt)路径'
)
@click.option(
    '--debug', 
    is_flag=True, 
    help='调试标志，启用后会输出更多调试信息'
)
@click.option(
    '-v', '--verbose', 
    is_flag=True, 
    help='详细输出，显示解析过程的详细信息'
)
@click.option(
    '-e', '--embedded', 
    is_flag=True, 
    help='puml内容作为url嵌入到md文件中'
)
@click.option(
    '-d', '--depth', 
    default=10, 
    type=int, 
    help='流程图绘制的最大深度(默认10)'
)
@click.option(
    '-u', '--update-key', 
    is_flag=True, 
    help='使用ctags自动更新Key.txt文件'
)
@click.option(
    '--project-path', 
    default='.', 
    help='项目路径(配合--update-key使用)'
)
@click.argument(
    'filelist',
    nargs=-1,  # 接受可变数量的参数
)
def draw(output, keyword, debug, verbose, embedded, depth, update_key, project_path, filelist):
    """
    文档生成主函数
    
    根据命令行参数执行Key.txt更新或文档生成操作。
    
    Args:
        output: 输出文件路径
        keyword: Key.txt关键字文件路径
        debug: 是否启用调试模式
        verbose: 是否启用详细输出
        embedded: 是否嵌入PUML URL
        depth: 流程图绘制深度
        update_key: 是否只更新Key.txt
        project_path: 项目路径（用于更新Key.txt）
        filelist: 输入C文件列表
    """
    # 构建参数字典，传递给文档生成器
    amap = {'verbose': verbose, 'debug': debug, 'depth': depth}
    
    # 如果启用详细输出，配置日志级别为DEBUG
    if verbose:
        logging.basicConfig(
            format='[%(levelname)s] %(message)s',
            level=logging.DEBUG
        )
    
    # 过滤输入文件列表，跳过目录，只保留文件
    valid_files = []
    for f in filelist:
        if os.path.isfile(f):
            valid_files.append(f)
        elif os.path.isdir(f):
            # 如果参数是目录，且使用了 -u 但没有指定 --project-path
            # 则将其作为项目路径
            if update_key and project_path == '.':
                project_path = f
                click.secho(f"[提示] 使用目录作为项目路径: {f}", fg='yellow')
            else:
                click.secho(f"[警告] 跳过目录(不是文件): {f}", fg='yellow')
        else:
            click.secho(f"[警告] 路径不存在: {f}", fg='yellow')
    
    # 如果指定了 --update-key，先更新 Key.txt
    if update_key:
        try:
            key_file = keyword if keyword else 'Key.txt'
            count = update_key_file(
                project_path=project_path,
                output_path=key_file
            )
            if count == 0:
                click.secho("[警告] 未生成任何符号，请检查项目路径", fg='yellow')
                return
            click.secho(f"[成功] Key.txt 已更新: {key_file}", fg='green')
            click.secho("")
        except FileNotFoundError as e:
            click.secho(f"[错误] {e}", fg='red')
            return
        except Exception as e:
            click.secho(f"[错误] 更新 Key.txt 失败: {e}", fg='red')
            return
    
    # 只有在指定了有效输入文件时才执行文档生成
    if valid_files:
        click.secho(f"+++ Program flags: {amap}", fg='green')
        click.secho(f'+++ Output file: {output}', fg='green')
        
        # 创建文档生成器实例
        doc = CMarddownDoc(
            amap,
            keyword_file=keyword,
            output_fname=output,
            embedded=embedded
        )
        # 解析所有输入文件
        doc.parse_files(valid_files)
        # 保存输出文件
        doc.save(output)
    elif not update_key:
        # 既没有输入文件，也没有指定--update-key
        click.secho("未指定输入文件, 使用--help选项查看帮助.", fg="red")


# =============================================================================
# 程序入口
# =============================================================================

if __name__ == "__main__":
    draw()
