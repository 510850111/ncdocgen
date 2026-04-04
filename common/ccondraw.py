#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 控制台伪代码打印器 (ccondraw.py)
# -----------------------------------------------------------------------------
# 将语法树节点递归打印为缩进格式的伪代码，用于控制台输出。
#
# 支持的节点类型:
#     DONENODE       - 普通代码节点
#     DONEBREAK      - break语句
#     DONECONTINUE   - continue语句
#     DONEGOTO       - goto语句
#     DONERETURN     - return语句
#     DONEIFELSE     - if-else条件分支
#     DONEIF         - if条件分支
#     DONEWHILE      - while循环
#     DONECASE       - case分支
#     DONEDEFAULT    - default分支
#     DONEDO         - do-while循环
#     DONEFOR        - for循环
#     DONESWITCH     - switch语句
#     NODE           - 复合节点（递归处理）
#
# 输出格式:
#     使用行号前缀 + 缩进 + 代码的格式
#     控制结构使用 { } 包围，并显示跳转信息
#
# 使用示例:
#     from common.ccondraw import print_func_exp, print_fun_header
#     print_fun_header('func_name', header_dict)
#     print_func_exp(syntax_tree_node, x=0, y=0)
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import click
from .cglobal import *


def print_prefix(n, x):
    """
    打印行号前缀和缩进
    
    格式: "0001  " + "    "*x
    
    Args:
        n: 行号
        x: 缩进级别（每级4个空格）
    """
    print(FUN_LFMT % n, FUN_DELIM * x, end=' ')


def print_blank():
    """打印空行（用于分隔代码块）"""
    print(FUN_BLANK)


def print_func_exp(exp, x=0, y=0):
    """
    递归打印函数表达式（核心函数）
    
    根据节点类型采用不同的打印格式，递归处理子节点。
    
    Args:
        exp: 表达式节点 [TYPE, START, END, EXPR, ...]
        x: 水平缩进级别（初始为0）
        y: 垂直递归深度（用于调试）
        
    Returns:
        str: 节点类型字符串
        
    节点处理逻辑:
        DONENODE/DONECODE: 直接打印代码内容
        BREAK/CONTINUE/GOTO/RETURN: 打印控制语句
        IFELSE: 打印if和else分支，递归处理子节点
        IF/WHILE/CASE/DEFAULT: 打印控制结构和子节点
        DO: 打印do-while结构
        FOR: 打印for循环（处理初始化、条件、迭代）
        SWITCH: 打印switch结构和所有case
        NODE: 递归处理所有子节点
    """
    ttype = exp[TK_TYPE]
    
    if (
            ttype == 'DONENODE'
            or ttype == 'DONECODE'
            ):
        # 如果是最终节点，直接打印
        for node in (exp[TK_EXPR]):
            print_prefix(node[TK_START], x)
            print(node[TK_EXPR])
            
    elif (
            ttype == 'DONEBREAK'
            or ttype == 'DONECONTINUE'
            or ttype == 'DONEGOTO'
            or ttype == 'DONERETURN'
            ):
        # 控制流语句：提取操作名（break/continue/goto/return）
        op = ttype[4:len(ttype)].lower()
        for node in (exp[TK_EXPR]):
            print_prefix(node[TK_START], x)
            print(node[TK_EXPR])
        print_blank()
        
    elif (ttype == 'DONEIFELSE'):
        # IF-ELSE结构：三子节点 [条件, if体, else体]
        node = exp[TK_EXPR][0]

        # 打印if条件和开始
        print_prefix(node[TK_START], x)
        print('if(%s){  -->%d' % (node[TK_EXPR], node[TK_END]))

        # 递归打印if分支
        print_func_exp(exp[TK_EXPR][1], x + 1, y + 1)

        # 打印else条件和开始
        print_prefix(node[TK_MID], x)
        print('}else(%s){  -->%d' % (node[TK_EXPR], node[TK_END]))

        # 递归打印else分支
        print_func_exp(exp[TK_EXPR][2], x + 1, y + 1)

        # 打印if结构结束
        print_prefix(node[TK_END], x)
        print('} <if(%d)' % (node[TK_START]))
        print_blank()
        
    elif (ttype == 'DONEIF'
            or ttype == 'DONEWHILE'
            or ttype == 'DONECASE'
            or ttype == 'DONEDEFAULT'
            ):
        # 单分支控制结构：两子节点 [条件, 语句体]
        op = ttype[4:len(ttype)].lower()
        node = exp[TK_EXPR][0]

        # 打印条件
        print_prefix(node[TK_START], x)
        print(op + '(%s){  -->%d' % (node[TK_EXPR], node[TK_END]))

        # 递归打印语句体
        print_func_exp(exp[TK_EXPR][1], x + 1, y + 1)

        # 打印结构结束
        print_prefix(node[TK_END], x)
        print('} <%s(%d)' % (op, node[TK_START]))
        print_blank()
        
    elif (ttype == 'DONEDO'):
        # DO-WHILE结构：do { } while(条件)
        op = ttype[4:len(ttype)].lower()
        node = exp[TK_EXPR][0]
        
        # 打印do开始
        print_prefix(node[TK_START], x)
        print(op + '{  -->%d' % (node[TK_END]))

        # 递归打印循环体
        print_func_exp(exp[TK_EXPR][1], x + 1, y + 1)

        # 打印while条件
        print_prefix(node[TK_END], x)
        print('}while <(%s)(-->%d)' % (node[TK_EXPR], node[TK_START]))
        print_blank()
        
    elif (ttype == 'DONEFOR'):
        # FOR循环结构：包含初始化、条件、迭代
        op = ttype[4:len(ttype)].lower()
        node = exp[TK_EXPR][0]

        # 打印初始化表达式
        print_prefix(node[TK_START], x)
        print('..(%s)' % (node[TK_EXPR0]))

        # 打印for条件和开始
        print_prefix(node[TK_START], x)
        print(op + '(%s){  -->%d' % (node[TK_EXPR], node[TK_END]))

        # 递归打印循环体
        print_func_exp(exp[TK_EXPR][1], x + 1, y + 1)

        # 打印迭代表达式
        print_prefix(node[TK_END], x)
        print('..(%s)' % (node[TK_EXPR2]))
        
        # 打印for结构结束
        print_prefix(node[TK_END], x)
        print('} <%s(%d)' % (op, node[TK_START]))
        print_blank()
        
    elif (ttype == 'DONESWITCH'):
        # SWITCH结构：多case分支
        op = ttype[4:len(ttype)].lower()
        node = exp[TK_EXPR][0]

        # 打印switch条件和开始
        print_prefix(node[TK_START], x)
        print(op + '(%s){  -->%d' % (node[TK_EXPR], node[TK_END]))

        # 遍历并打印所有case分支
        j = 0
        for node2 in (exp[TK_EXPR][1][TK_EXPR]):
            # 遍历switch里面的分支判断
            if (node2[TK_TYPE] == 'DONECASE'
                    or node2[TK_TYPE] == 'DONEDEFAULT'
                    ):
                j += 1
            print_func_exp(node2, x + j, y + 1)
            
        # 打印switch结构结束
        print_prefix(node[TK_END], x)
        print('} <%s(%d)' % (op, node[TK_START]))
        print_blank()
        
    elif (ttype == 'NODE'):
        # 复合节点：递归处理所有子节点
        for node in exp[TK_EXPR]:
            print_func_exp(node, x, y)
        
    return ttype


import sys
sys.path.append('..')


def print_fun_header(name, header):
    """
    打印函数头部信息
    
    按照comment_seq_list顺序打印函数说明表的各项内容。
    
    Args:
        name: 函数名
        header: 函数字典，包含brief, param, return等键
        
    输出格式:
        函数头部: name
        ----------------------------------------------------------------------
        原    型|  ...
        ----------------------------------------------------------------------
        概    述|  ...
        ...
    """
    click.secho(FUN_SEP, fg='yellow')
    click.secho(f'函数头部: {name}', fg='green')
    for key in comment_seq_list:
        print(CM_SEP)
        print(CM_FMTSTR % comment_translate_table[key], end=' ')

        lines = header[key].split('\n')
        print(lines[0])
        try:
            for line in lines[1:]:
                print(CM_FMTSTR % (' '), end=' ')
                print(line)
        except:
            pass
    print(CM_SEP)


# =============================================================================
# 单元测试
# =============================================================================

if __name__ == '__main__':
    tt = ['DONESWITCH', 11, 34, [
        ['SWITCH', 11, 34, 'sw?'], 
        ['NODE', 12, 34, 
         [['DONECASE', 14, 22, [['CASE', 14, 14, 'e2?'], 
                                ['NODE', 14, 22, [['DONENODE', 14, 14,
[['DONENODE', 14, 14, 'case e2']]], ['DONEIF', 16, 18, [['IF', 16, 18, 'dodo e2?'], ['DONENODE', 16, 18
, [['DONENODE', 17, 17, 'go ( ) ']]]]], ['DONENODE', 19, 22, [['DONENODE', 20, 20, '\xbf\xc9\xc4\xdc ']]]]]
                               ]], 
          ['DONEBREAK', 23, 23, [['BREAK', 23, 23, 'BRE break23']]], 
          ['DONECASE', 25, 25, [['CASE', 25, 25, 'e2?'], ['DONENODE', 25, 25, [['DONENODE', 25, 25, 'NOP']]]]], 
          ['DONECASE', 26, 30, [['CASE', 26, 26, 'e3?'], ['NODE', 26, 30, [['DONENODE', 26, 26, [['DONENODE', 26, 26, 'NOP']]], ['DONEIF', 27, 30, [['IF', 27, 30,
'dodo ( )?'], ['DONENODE', 28, 30, [['DONENODE', 29, 29, 'dodo1 ( ) ']]]]]]]]],
['DONEBREAK', 31, 31, [['BREAK', 31, 31, 'BRE break31']]], ['DONECASE', 32, 32,
[['CASE', 32, 32, 'tt?'], ['DONENODE', 32, 32, [['DONENODE', 32, 32, 'NOP']]]]]
, ['DONEBREAK', 33, 33, [['BREAK', 33, 33, 'BRE break33']]]]
        ]
    ]]

    tt2 = ['DONENODE', 1, 10, [
        ['DONENODE', 2, 3, 'gogo1'], 
        ['DONENODE', 5, 7, 'gogo2'], 
    ]]    
    
    tt3 = ['DONENODE', 1, 10, [
        ['DONENODE', 2, 3, 'gogo1'], 
        ['DONENODE', 2, 3, 'gogo2'], 
    ]]    
    #print print_func_exp(tt)
    print(print_func_exp(tt2))
    print(print_func_exp(tt3))


