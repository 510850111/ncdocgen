#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
C语言全局常量和工具函数
=====================
定义语法树节点索引、全局常量、辅助函数等。

节点结构 (Token Vector):
    [ID, X, Y, TYPE, TEXT, LINE, START, END, EXPR, EXPR0, EXPR1, EXPR2]
    
    TV_ID     - 节点唯一ID
    TV_X      - X坐标（用于可视化）
    TV_Y      - Y坐标
    TV_TYPE   - 节点类型（如 'DONENODE', 'DONEIF' 等）
    TV_TEXT   - 显示文本
    TV_LINE   - 源代码行号
    TK_START  - 注释起始行
    TK_END    - 注释结束行
    TK_EXPR   - 子表达式列表
    TK_EXPR0-2 - 特殊表达式槽位

作者: ncdocgen团队
"""


import sys

# ========================================================================
# MAP类型索引常量
# ========================================================================
# 用于all_map列表，存储不同类型的数据

MAP_CODE = 0    # 代码文本映射
MAP_CM   = 1    # 注释映射（comment_map）
MAP_IDEN = 2    # 标识符映射

# ========================================================================
# 变量类型常量
# ========================================================================
# 用于区分不同作用域的变量

VTYPE_GLOBAL = 0    # 全局变量
VTYPE_PARAM  = 1    # 函数参数
VTYPE_LOCAL  = 2    # 局部变量
VTYPE_FUN    = 3    # 函数

# ========================================================================
# 流程图(CHART)相关常量
# ========================================================================
# 用于生成流程图时的数据索引

CHART_LINE  = 0     # 行号
CHART_TYPE  = 1     # 节点类型
CHART_TOKEN = 2     # 令牌/标记
CHART_NUM   = 3     # 数量

# ========================================================================
# 数据类型常量
# ========================================================================
# 用于区分类型定义和数据

TOKENDATA_TYPE = 0  # 类型定义
TOKENDATA_LINK = 1  # 数据链接

# ========================================================================
# 可视化节点(VNODE)常量
# ========================================================================
# 用于Visio流程图节点属性

VNODE_WIDTH  = 0    # 节点宽度
VNODE_HEIGHT = 1    # 节点高度
VNODE_ENTRY  = 2    # 入口点
VNODE_EXIT   = 3    # 出口点
VNODE_TYPE   = 4    # 节点类型
VNODE_DATA   = 5    # 节点数据

# 节点对(Pair)索引
VNODE_PAIR_TYPE = 0 # 对类型
VNODE_PAIR_NODE = 1 # 对节点

# ========================================================================
# 语法树Token索引常量
# ========================================================================
# 定义语法树节点各字段的索引位置

TK_TYPE  = 0    # 节点类型（如DONEIF, DONEFOR等）
TK_COUNT = 1    # 子节点数量
TK_START = 1    # 起始行号（与TK_COUNT共用）
TK_END   = 2    # 结束行号
TK_EXPR  = 3    # 子表达式列表
TK_EXPR0 = 4    # 表达式槽位0（如for循环的初始化）
TK_EXPR2 = 5    # 表达式槽位2（如for循环的增量）
TK_MID   = 4    # 中间位置（如if-else的else位置）

TK_EXPRS = 4    # 单行语句表达式

# ========================================================================
# 默认配置常量
# ========================================================================

DEFAULT_DEPTH = 10  # 默认流程图展开深度
USELIST = 0         # 使用string还是list进行整合（0:string, 1:list）

# ========================================================================
# 格式化字符串常量
# ========================================================================
# 用于输出格式化

CM_FMTSTR = ' %-10s|  '      # 注释映射格式
CM_SEP    = '-' * 70         # 分隔线

FUN_SEP   = '#' * 70         # 函数分隔线
FUN_BLANK = '-' * 4          # 空白缩进
FUN_LFMT  = '%04d'           # 行号格式（4位数字）
FUN_DELIM = '  '             # 分隔符

FUN_STR_WIDTH = 28           # 标识符显示宽度
FUN_STR_FMT   = '%-27s '     # 标识符格式（左对齐27字符）

# 导入配置文件（标签翻译表、默认值表）
from .config import *

# 函数注释项的顺序列表
# 用于按顺序提取和显示函数头部的注释项
comment_seq_list = ['proto', 'brief', 'param', 'return', 'fcall', 'gvarin', 'gvarout', 'details']


def get_rcur_info():
    """
    获取调用者的栈帧信息（递归版本）
    
    用于调试，打印当前函数名和行号。
    """
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    print(('########### ', f.f_code.co_name, f.f_lineno, '#####'))

# 调试开关（0:关闭, 1:开启）
DEBUG = 0


def get_cur_info():
    """
    获取当前调用者的栈帧信息
    
    Returns:
        tuple: (函数名, 行号)
        如果DEBUG=1，返回固定值"fun"
    """
    if DEBUG == 1:
        return "fun"
    else:
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
        return (f.f_code.co_name, f.f_lineno)


def updatestr(p, trim=0, sep=' '):
    """
    更新字符串列表
    
    将列表中的多个字符串片段合并到p[0]，用sep分隔。
    
    Args:
        p: 字符串列表，结果存储在p[0]
        trim: 从末尾跳过的元素数量
        sep: 分隔符，默认为空格
    """
    p[0] = ''
    for i in range(1, len(p) - trim):
        if (p[i]):
            p[0] += p[i]
            if (p[0][-1] != ' '):
                p[0] += sep


def print_com_err(err, lineinfo=""):
    """
    打印注释错误信息
    
    Args:
        err: 错误信息
        lineinfo: 行号信息
    """
    print("com err %s" % lineinfo, end=' ')
    print(err)


import os


def get_full_name(name):
    """
    获取完整文件名
    
    如果文件名不包含盘符，则在当前工作目录下查找。
    处理GBK编码的路径（兼容Windows中文路径）。
    
    Args:
        name: 文件名或路径
        
    Returns:
        str: 完整文件路径
    """
    if (name.find(':') == -1):
        filename = os.getcwd().decode('gbk') + "\\" + name.decode('gbk')
    else:
        filename = name
    return filename


def get_short_doc_name(name):
    """
    获取简短的文档名称
    
    从完整路径中提取目录名和文件名，生成简短的文档标识符。
    格式: _CDOC_目录名_文件名
    
    Args:
        name: 完整文件路径
        
    Returns:
        str: 简短的文档名称
    """
    fslice = name.split('\\')
    if (len(fslice) >= 2):
        return '_CDOC_' + fslice[-2] + '_' + fslice[-1]
    else:
        return '_CDOC_' + fslice[0]


##############
# 测试数据
# 用于开发和测试的示例C代码
data = '''
#include <include.h>
int b;
int a=1;
int b=(a);
/** abcd */
/** abcd */
int func(int b)
{
	/** step1*/
	a=2;
	/** judge a */
	if (a==2){	
		/** do left */
	}else
	{
		/** do right */
	}
}
'''
