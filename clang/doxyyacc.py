#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Doxygen注释语法分析器 (doxyyacc.py)
# -----------------------------------------------------------------------------
# 使用PLY的YACC解析Doxygen风格的注释，提取结构化文档信息。
#
# 语法规则:
#     translation_unit : statement
#                      | translation_unit statement
#     statement        : KEY expression    (@标签 + 内容)
#                      | expression        (纯文本)
#     expression       : expression WORD NEWLINE  (多行文本)
#                      | WORD NEWLINE             (单行文本)
#                      | BLANKLINE | NEWLINE      (空行)
#
# 输出格式:
#     返回 ([tag, content], ...) 列表，如:
#     [('brief', '函数说明'), ('param', 'x 参数x')]
#
# 关键PLY配置 (PyInstaller兼容性):
#     debug=False, write_tables=False, errorlog=yacc.NullLogger()
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import sys
from ply import yacc

# 处理相对导入（支持模块直接运行和包内导入）
try:
    from . import doxylex
except:
    import doxylex

if sys.path[-1] != '..':
    sys.path.append('..')

from common.debug import *
from common.cglobal import *


# =============================================================================
# 元素列表类
# =============================================================================
# 用于存储解析结果的容器

class elem_list:
    """
    Doxygen元素列表容器
    
    存储解析后的Doxygen标签和内容对。
    
    Attributes:
        cm (list): 存储 [tag, content] 对的列表
    """
    
    def __init__(self):
        """初始化空列表"""
        self.cm = []

    def push(self, elem):
        """
        添加元素到列表
        
        Args:
            elem: [tag, content] 格式的列表
        """
        self.cm.append(elem)

    def reset(self):
        """清空列表"""
        del self.cm[:]


# =============================================================================
# 全局词法分析器实例
# =============================================================================

doxyl = doxylex.doxylex()


# =============================================================================
# Doxygen语法分析器工厂函数
# =============================================================================

def doxyyacc(mylexer=doxyl, elist=elem_list()):
    """
    创建Doxygen语法分析器
    
    使用PLY的YACC构建语法分析器，定义Doxygen注释的语法规则。
    
    Args:
        mylexer: 词法分析器实例，默认为全局doxyl
        elist: 元素列表容器，用于存储解析结果
        
    Returns:
        tuple: (parser, elist.cm, lexer)
            - parser: YACC语法分析器对象
            - elist.cm: 解析结果列表
            - lexer: 词法分析器对象
            
    语法规则说明:
        translation_unit - 顶层规则，表示一个完整的注释块
        statement        - 单条语句（标签+内容 或 纯文本）
        expression       - 表达式（文本内容）
    """

    # -------------------------------------------------------------------------
    # 语法规则定义
    # -------------------------------------------------------------------------
    # PLY使用p_前缀识别语法规则
    # 函数文档字符串是BNF语法规则
    
    def p_translation_unit(p):
        '''translation_unit : statement
                        | translation_unit statement'''
        # 递归规则：注释块由一个或多个statement组成
        pass

    def p_statement_assign(p):
        'statement : KEY expression'
        # 匹配标签语句：@key content
        # 将结果存储到elist
        updatestr(p)
        elist.push([p[1][1:], p[2]])  # 去掉@符号，保存[标签, 内容]
        if DEBUG_DOXYYACC == 1:
            print((get_cur_info()[0], p[0]))
        pass

    def p_statement_line(p):
        'statement : expression'
        # 匹配纯文本语句（没有@标签）
        if p[1] == '':
            # 空行，忽略
            pass
        else:
            # 非空行，保存内容
            updatestr(p)
            if DEBUG_DOXYYACC == 1:
                print((get_cur_info()[0], p[0]))

    def p_expression_com(p):
        'expression : expression WORD NEWLINE'
        # 多行表达式：处理跨行文本
        # 将多行用换行符连接
        p[0] = ''
        p[0] = p[1] + '\n' + p[2]
        if DEBUG_DOXYYACC == 1:
            print((get_cur_info()[0], p[0]))
        pass

    def p_expression_line(p):
        'expression : WORD NEWLINE'
        # 单行表达式：WORD + 换行
        updatestr(p, 1)
        if DEBUG_DOXYYACC == 1:
            print((get_cur_info()[0], p[0]))
        pass

    def p_expression_blankline(p):
        '''expression : BLANKLINE
                       | NEWLINE'''
        # 空行表达式：匹配空白行或纯换行
        p[0] = ''
        if DEBUG_DOXYYACC == 1:
            print((get_cur_info()[0], p[0]))

    def p_empty(p):
        'empty : '
        # 空产生式，用于占位
        pass

    def p_error(p):
        """
        语法错误处理
        
        打印错误位置和当前token值。
        """
        print(("doxy syntax error at '%s L%d'" % (p.value, p.lineno)))

    # -------------------------------------------------------------------------
    # 构建语法分析器
    # -------------------------------------------------------------------------
    
    lexer = mylexer.lexer
    tokens = mylexer.tokens
    
    # 关键配置：禁用调试和表写入，确保PyInstaller兼容性
    p1 = yacc.yacc(
        method='LALR',              # 使用LALR解析算法
        tabmodule='doxy_tab',       # 解析表模块名
        debug=False,                # 禁用调试输出（PyInstaller必需）
        write_tables=False,         # 不写入解析表文件（PyInstaller必需）
        errorlog=yacc.NullLogger()  # 空错误日志（PyInstaller必需）
    )
    
    return p1, elist.cm, lexer


# =============================================================================
# 格式化输出常量
# =============================================================================

FMTSTR = '%-12s|  '


# =============================================================================
# 命令行测试
# =============================================================================

if __name__ == '__main__':
    try:
        # 默认测试文件
        name = '..\\txt\\doxy.txt'
        if (len(sys.argv) > 1):
            name = sys.argv[1]

        # 创建解析器
        p, elist, ret = doxyyacc()

        # 读取并解析文件
        f = open(name)
        data = f.read()
        res = p.parse(data, debug=0)
        
        # 格式化打印输出
        for elem in elist:
            print('-' * 50)
            print(FMTSTR % (elem[0]), end=' ')
            for line in elem[1].split('\n'):
                print(line)
                print(FMTSTR % (' '), end=' ')
            print('')

    except EOFError:
        print(e)
