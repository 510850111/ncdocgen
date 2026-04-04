#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# C语法处理核心模块 (cgrammar.py)
# -----------------------------------------------------------------------------
# 提供C语言语法分析、语法树构建、注释提取、控制结构解析等功能。
#
# 主要功能:
#     - 字符串处理工具函数（get_split_str, get_format_str）
#     - 语法树节点合并与优化（combine_node_exp）
#     - 注释搜索与提取（parser_search_comment, parser_search_name）
#     - 控制结构解析（if/else, switch/case, for, while, do-while）
#     - 全局变量分析（analyze_gvin_data, update_gvarin, clean_gvarout）
#     - 函数头部信息生成（get_fun_header）
#
# 节点结构:
#     [TK_TYPE, TK_START, TK_END, TK_EXPR, ...]
#
# 节点类型:
#     NODE           - 复合节点
#     DONENODE       - 普通代码节点
#     DONEIF         - if条件节点
#     DONEIFELSE     - if-else条件节点
#     DONEWHILE      - while循环节点
#     DONEFOR        - for循环节点
#     DONEDO         - do-while循环节点
#     DONESWITCH     - switch节点
#     DONECASE       - case分支节点
#     DONEDEFAULT    - default分支节点
#     DONEBREAK      - break语句节点
#     DONECONTINUE   - continue语句节点
#     DONEGOTO       - goto语句节点
#     DONERETURN     - return语句节点
#     SINGLE         - 单语句节点
#
# 依赖模块:
#     - debug: 调试标志
#     - cglobal: 全局常量
#     - chandler: fbasic基类
#     - doxyyacc: Doxygen注释解析
#     - vlex: 变体词法分析器
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

from .debug import *
from .cglobal import *
import click
import logging


# ========================================================================
# 字符串处理工具函数
# ========================================================================

def get_split_str(s):
    """
    将字符串按照空格分开
    
    用于解析@param等标签，分离参数名和描述。
    例如: "@param x 参数x" -> ("@param", "x 参数x")
    
    Args:
        s: 输入字符串
        
    Returns:
        tuple: (第一个单词, 剩余部分)
               如果只有一个单词，返回('', 原字符串)
    """
    subs = s.rstrip().split()
    l = len(subs)
    if l > 1:
        return subs[0], s[len(subs[0]) + 1:].rstrip()
    else:
        return '', s


def get_format_str(s, prefix=4):
    """
    对字符串进行组合，以便进行打印
    
    将多行字符串格式化，除第一行外其余行添加缩进。
    
    Args:
        s: 输入字符串（可能包含换行）
        prefix: 缩进空格数，默认为4
        
    Returns:
        str: 格式化后的字符串
    """
    lines = s.split('\n')
    fstr = lines[0]
    fstr += '\n'
    try:
        for line in lines[1:]:
            fstr += ' ' * prefix
            fstr += line
            fstr += '\n'
    except:
        pass
    return fstr.rstrip()


# ========================================================================
# 标识符解析函数
# ========================================================================

def parser_search_name(exp, cm_map):
    """
    解释标识符 - 从表达式或注释映射中获取显示名称
    
    优先使用注释映射中的内容，否则使用代码表达式。
    
    Args:
        exp: 表达式节点 [TK_TYPE, TK_START, TK_END, TK_EXPR, ...]
        cm_map: 注释映射字典 {行号: 注释内容}
        
    Returns:
        str: 标识符的显示名称
        
    处理逻辑:
        1. 如果exp[TK_START]行在cm_map中有注释，使用注释内容
        2. 否则使用exp[TK_EXPR]（代码表达式）
        3. 去掉末尾的分号
    """
    name = 'NULL'
    if (exp[TK_START] in cm_map):
        name = cm_map[(exp[TK_START])]
    else:
        if (exp[TK_EXPR] != ''):
            name = exp[TK_EXPR]
        if name[-2] == ';':
            name = name[0:-2]
    return name


# ========================================================================
# 节点合并函数
# ========================================================================

def combine_node_exp(exp_list):
    """
    合并相同节点的表达式 - 将连续的DONENODE合并，优化语法树结构
    
    遍历表达式列表，将连续的DONENODE类型合并为一个节点。
    
    Args:
        exp_list: 表达式列表 [TYPE, START, END, [expr1, expr2, ...]]
        
    Returns:
        list: 合并后的节点列表
        
    处理逻辑:
        1. 遍历exp_list[TK_EXPR]中的所有子表达式
        2. 如果连续多个子表达式都是DONENODE类型，合并它们的TK_EXPR内容
        3. 遇到非DONENODE类型，将之前积累的context压入结果，然后压入当前表达式
    """
    new_list = ['NODE', exp_list[TK_START], exp_list[TK_END], []]
    context = ['DONENODE', exp_list[TK_START], 0, []]
    last_i = -1

    # 遍历一个节点的所有子节点（表达式）
    for i in range(len(exp_list[TK_EXPR])):
        exp = exp_list[TK_EXPR][i]
        # 如果待处理的表达式类型为DONENODE，则可以合并列表
        if (exp[TK_TYPE] == 'DONENODE'):
            if (i - last_i == 1):
                # 此时合并，并更新last_i
                context[TK_EXPR].extend(exp[TK_EXPR])
                context[TK_END] = exp[TK_END]
                last_i = i
            else:
                # 说明上次已经不是DONENODE了，新建context
                context = ['DONENODE', exp[TK_START], 0, []]
                context[TK_EXPR].extend(exp[TK_EXPR])
                context[TK_END] = exp[TK_END]
                last_i = i
        else:
            # 如果不是这个类型，说明遇到了新的类型
            # 将有效的已有类型压入
            if (len(context[TK_EXPR]) != 0):
                new_list[TK_EXPR].append(context)
            if (ENABLE_HANDLE_DEBUG == 1):
                print('==GO0 ', new_list[TK_EXPR])
            new_list[TK_EXPR].append(exp)

            # 遇到不同的类型时，先将类型复位
            # 这样可以避免后期误将已经压入的DONENODE再次压入
            context = ['DONENODE', exp[TK_START], 0, []]
        if (ENABLE_HANDLE_DEBUG == 1):
            print('==GO ', exp, '\n==Go2', context, '\n==Go3', new_list)

    # 如果最后一个表达式类型为DONENODE，应增加到list里面
    if (exp[TK_TYPE] == 'DONENODE'):
        new_list[TK_EXPR].append(context)

    if (ENABLE_HANDLE_DEBUG == 1):
        print('==GOE ', new_list, '\n', context)

    # 如果只有一个，直接采用新的节点
    if (len(new_list[TK_EXPR]) == 0):
        new_list = context
    elif len(new_list[TK_EXPR]) == 1:
        new_list = new_list[TK_EXPR][0]
    return new_list


def get_if_str(fmt):
    """
    确保if条件字符串以?结尾
    
    PlantUML语法要求条件判断以'?'结尾。
    
    Args:
        fmt: 条件表达式字符串
        
    Returns:
        str: 带'?'的条件表达式
    """
    s = fmt.rstrip()
    if (s[-1] != '?'):
        return s + '?'
    else:
        return s


# ========================================================================
# 范围索引常量
# ========================================================================

I_START = 0  # 范围索引起始位置
I_END = 1    # 范围索引结束位置


# ========================================================================
# 导入依赖模块
# ========================================================================

from .chandler import fbasic

import sys
#sys.path.insert(0,"..")

import clang.doxyyacc as doxyyacc
import clang.vlex as vlex


# ========================================================================
# C语法处理主类
# ========================================================================

class cgrammar(fbasic):
    """
    C语法处理器主类
    
    继承fbasic提供的基础功能，集成doxygen注释解析，
    提供C语言语法分析、注释搜索、表达式处理等功能。
    
    Attributes:
        doxyp: doxygen解析器
        elist: 注释元素列表
        lexer: Doxygen词法分析器
        slex: 简化版词法分析器（用于全局变量分析）
    """

    def __init__(self, keyfile=""):
        """
        初始化C语法处理器
        
        Args:
            keyfile: 关键字文件路径，如果指定则从文件加载关键字
        """
        fbasic.__init__(self)
        self.doxyp, self.elist, self.lexer = doxyyacc.doxyyacc()
        self.slex = vlex.vlex({})
        if (keyfile != ""):
            self.slex.load_keyword_from_file(keyfile)

    def parser_search_comment(self, exp, cm_map, start, end):
        """
        搜索表达式范围内的注释
        
        遍历start到end行范围，提取注释内容构建节点列表。
        
        Args:
            exp: 表达式节点 [TK_TYPE, TK_START, TK_END, TK_EXPR, ...]
            cm_map: 注释映射表 {line_no: comment_text}
            start: 开始行号
            end: 结束行号
            
        Returns:
            list: 注释节点列表 [TYPE, START, END, expr] 或
                  [TYPE, START, END, [NODE, ...]]
        """
        cm_list = []
        if (exp[TK_TYPE] == '{}'):
            if (ENABLE_HANDLE_DEBUG == 1):
                print(('parser search:', start, end + 1))
            # 遍历本段文本
            # 此处要注意层次结构保持统一，插值的部分应作为一个NODE
            cm_list = ['DONENODE', start, end, []]

            # 如果包含相关的注释，则将其插入到cm_list中
            for i in range(start + 1, end + 1):
                if i in cm_map:
                    cm_list[TK_EXPR].append(['DONENODE', i, i, cm_map[i]])

            if (len(cm_list[TK_EXPR]) == 0):
                # 如果cm_list长度为0，需要将代码嵌入
                code = self.code_pop(start + 1, end)
                if (ENABLE_HANDLE_DEBUG == 1):
                    print(('parser code:', code))
                # 如果代码不为空，则将整段代码进行处理
                if (code != ""):
                    # 如果设置了文本绘图选项，按照;进行分隔
                    if self.flag_get('text'):
                        code_slide = code.split(';')
                        for n in code_slide:
                            nn = n.strip()
                            if nn:
                                cm_list[TK_EXPR].append(
                                    ['DONENODE', start + 1, start + 1, nn])

                        if (len(code_slide) >= 2):
                            cm_list[TK_END] = end - 1
                    else:
                        # 如果未设置，则按照传统的方法截取节点
                        cm_list[TK_EXPR].append(
                            ['DONENODE', start + 1, start + 1, code])

        elif (exp[TK_TYPE][0:4] == 'DONE'):
            # 如果已经是DONE，则直接返回，不做修改
            cm_list = exp[TK_EXPR]
        else:
            # 返回单节点
            cm_list = [
                exp[TK_TYPE], start, end,
                parser_search_name(exp, cm_map)
            ]
        return cm_list

    def parse_single(self):
        """
        解析单语句（占位方法）
        
        由子类或后续扩展实现。
        """
        return

    def precombine_exp(self, exp, ipos, lstart, lend):
        """
        预合并表达式
        
        在解析组合表达式前，将堆栈中完全包含在当前范围内的表达式预先合并。
        
        Args:
            exp: 表达式列表（输出）
            ipos: 表达式位置列表（输出）
            lstart: 当前范围起始行
            lend: 当前范围结束行
            
        处理逻辑:
            1. 从堆栈顶部依次取出token
            2. 如果token范围在当前范围内，压入exp和ipos
            3. 如果token范围超出当前范围，停止合并
        """
        try:
            compact = 1
            while (compact):
                # 先判断是否满足连续的条件，
                #    按照先入后出的原则
                #    如果历史{}不被当前范围(lstart, lend)所包含
                #    则退出本循环，进行解析
                #        如果长度为1，说明没有包含
                #        如果长度>1，说明需要被包含
                exp.append(self.top())
                ipos.append(exp[-1][TK_START:TK_END + 1])

                if (ENABLE_HANDLE_DEBUG == 1):
                    print(('cbe', ipos, exp))

                # 如果压入的解出来的数据的范围不在当前{}之内，则结束这个循环
                if (ipos[-1][I_START] <= lstart or ipos[-1][I_END] >= lend):
                    ipos.pop()
                    exp.pop()
                    raise IndexError
                # 只有真正满足需要，才将precombine_exp pop
                self.rpop()
        except IndexError:
            # 说明已经不存在多余的数量，或者文件已经解析完毕
            if (ENABLE_HANDLE_DEBUG == 1):
                print(('com1', ipos, exp))
            return

    def parse_comp(self, cm_map):
        """
        解析组合表达式（代码块）
        
        处理{}包围的代码块，将内部的多个表达式合并为一个节点。
        
        Args:
            cm_map: 注释映射表
            
        Returns:
            list: 合并后的节点列表
            
        处理流程:
            1. 初始化exp和ipos列表
            2. 调用precombine_exp预合并
            3. 处理表达式间的注释
            4. 合并连续的DONENODE
        """
        exp = []  # 表达式
        ipos = []  # 表达式的范围，压入的是[起始，终止]位置
        # 如果为{}，需要判断
        lstart, lend = self.top()[TK_START:TK_END + 1]
        tlist = ['NODE', lstart, lend, []]  # 列表

        # 首先将当前范围和当前数据保存
        exp.append(self.rpop())
        ipos.append([lstart, lend])

        # 对表达式进行预合并
        self.precombine_exp(exp, ipos, lstart, lend)
        start = lstart
        end = lend

        if (len(exp) == 1):
            #如果长度为1，说明是一个标准长度
            # 此时只将 注释项 导入
            # 返回一个简单的注释
            tlist = self.parser_search_comment(exp[-1], cm_map,
                                               exp[-1][TK_START],
                                               exp[-1][TK_END])
            #print tlist
            self.rpush(tlist)
            # 此时需要退出
            return tlist

        # 此时exp是按照逆序的方式组织的，需要从尾部开始搜索
        while len(exp) > 1:
            # 如果当前元素的长度在{}以下，实际上这个事情在机制上能够保证
            #if (exp[-1][TK_START] > start):

            # 此时需要依次压入 不同段 的内容
            if (start <= exp[-1][TK_START] - 1):
                # 如果两个表达式间还有注释，将其解析，并插入
                # 如果两部分行号连续，则不插入
                cm_res = self.parser_search_comment(['{}'], cm_map, start,
                                                    exp[-1][TK_START] - 1)
                # 如果注释结果为空，也不插入
                if (cm_res[TK_EXPR] != []):
                    tlist[TK_EXPR].append(cm_res)
                else:
                    # 如果注释结果不为空，此时判断起、止行号是否满足需要
                    # 需要完善TBD
                    pass
                if (ENABLE_HANDLE_DEBUG == 1):
                    print(('!', cm_res))
            tlist[TK_EXPR].append(exp[-1])
            if (ENABLE_HANDLE_DEBUG == 1):
                print(('loop', tlist[TK_EXPR]))
            start = exp[-1][TK_END] + 1
            exp.pop()
            # 此时将范围其实更新为新的问题

        # 当长度  为1的时候，将末尾的空间加上
        #    此时需明确长度不为1
        #if ENABLE_HANDLE_DEBUG==1: print 'comp last', start, lend
        # 只在start < lend时才进行后续的插入，否则认为有故障
        if (1 or start < lend):
            cm_res = self.parser_search_comment(exp[-1], cm_map, start, lend)
            if (cm_res[TK_EXPR] != []):
                tlist[TK_EXPR].append(cm_res)
            else:
                if (ENABLE_HANDLE_DEBUG == 1):
                    print('comp last', start, lend)

        # 将结果合并
        new_list = combine_node_exp(tlist)
        self.rpush(new_list)
        if ENABLE_HANDLE_DEBUG == 1:
            print('comp', new_list)

        return new_list

    def get_switch(self, old):
        """
        处理switch语句的case分支
        
        将原始的case节点列表重新组织，将case与对应的语句块绑定。
        
        Args:
            old: 原始switch节点 [TYPE, START, END, [CASE, ...]]
            
        Returns:
            list: 重新组织的switch节点
            
        处理逻辑:
            1. 遍历所有case/default节点
            2. 将break之前的所有节点绑定到当前case
            3. 处理没有break的case（fall-through）
        """
        result = []
        last_case = None
        case_node = None
        end_l = 0
        cnt = 0

        for leaf in old[TK_EXPR]:
            #print '-'*5, leaf
            if (leaf[TK_TYPE] == 'DONECASE' or leaf[TK_TYPE] == 'DONEDEFAULT'):
                if (last_case):
                    # 如果不为空，需要将之前的压入
                    result.append(last_case)
                # 重新初始化
                last_case = leaf
                case_node = last_case[TK_EXPR][0]
                case_expr = last_case[TK_EXPR][1]
                cnt = 0

            elif (leaf[TK_TYPE] == 'DONEBREAK'):
                # 如果遇到break，说明上一次case结束
                last_case[TK_EXPR][1] = case_expr
                result.append(last_case)
                result.append(leaf)
                last_case = None
            else:
                # 如果是普通节点，将其加入到case/default的分支的默认语句中
                # 此时需要重构语句

                if cnt == 0:
                    # 第一次压入时，重新构造NODE节点，覆盖原先的语句
                    case_expr = ['NODE', leaf[TK_START], leaf[TK_END], [leaf]]
                else:
                    # 后续操作中，压入并更新end
                    case_expr[TK_EXPR].append(leaf)
                cnt += 1
                end_l = leaf[TK_END]
                case_node[TK_END] = case_expr[TK_END] = last_case[
                    TK_END] = end_l

        if (leaf[TK_TYPE] != 'DONEBREAK'):
            result.append(last_case)

        #print '='*50
        #for leaf in result:
        #    print '-'*5, leaf

        return ['NODE', old[TK_START], old[TK_END], result]


    # ========================================================================
    # 核心解析方法
    # ========================================================================

    def parse(self):
        """
        核心解析方法 - 从token堆栈解析语法树
        
        根据栈顶token类型，调用对应的解析逻辑，
        将原始token转换为DONEXXX类型的语法树节点。
        
        支持的token类型:
            {}         - 代码块，调用parse_comp
            SINGLE     - 单语句，包装为DONENODE
            IFELSE     - if-else条件分支
            IF/WHILE/DO- 单条件控制结构
            LABELCASE  - 标签case
            CASE/DEFAULT- case分支
            SWITCH     - switch语句
            FOR        - for循环
            BREAK/CONTINUE/GOTO/RETURN - 控制流语句
            FUNC       - 函数定义
        """
        exp = []
        tlist = []
        token = self.top()[TK_TYPE]
        
        if (token == '{}'):
            # 解析代码块{}
            self.parse_comp(self.comment_map)
            
        elif (token == 'SINGLE'):
            # 单语句节点
            exp.append(self.rpop())
            start = exp[0][TK_START]
            end = exp[0][TK_END]
            text = parser_search_name(exp[0], self.comment_map)

            self.push(
                ['DONENODE', start, end, [['DONENODE', start, end, text]]])
                
        elif (token == 'IFELSE'):
            # IF-ELSE结构：三子节点 [条件节点, if体, else体]
            exp.append(self.rpop())  # if条件
            exp.append(self.rpop())  # else体
            exp.append(self.rpop())  # if体

            # 更新位置信息
            start = exp[0][TK_START]
            mid = exp[0][TK_MID]  # else位置
            end = exp[1][TK_END]
            exp[0][TK_END] = exp[1][TK_END]
            
            # 更新条件表达式（添加?）
            exp[0][TK_EXPR] = parser_search_name(exp[0], self.comment_map)
            exp[0][TK_EXPR] = get_if_str(exp[0][TK_EXPR])

            # 压入相关的工作
            tlist.append(exp[0])
            tlist.append(exp[2])
            tlist.append(exp[1])

            # 压入 还要压入 中间值
            self.push(['DONEIFELSE', start, end, tlist, mid])
            if ENABLE_HANDLE_DEBUG == 1:
                print('==PARSER: IFELSE', start, end, exp[0], '\n', exp[1],
                      '\n', exp[2])
                      
        elif (token == 'IF' or token == 'WHILE' or token == 'DO'):
            # 单分支条件结构
            exp.append(self.rpop())  # 条件
            exp.append(self.rpop())  # 语句体

            exp[0][TK_END] = exp[1][TK_END]

            # 更新条件表达式
            exp[0][TK_EXPR] = parser_search_name(exp[0], self.comment_map)
            if (token != 'DEFAULT'):
                exp[0][TK_EXPR] = get_if_str(exp[0][TK_EXPR])

            start = exp[0][TK_START]
            end = exp[0][TK_END]

            tlist.append(exp[0])
            tlist.append(exp[1])

            self.push(['DONE' + token, start, end, tlist])
            
        elif (token == 'LABELCASE'):
            # 标签case（多个case共享一个标签）
            exp.append(self.rpop())
            ret = []
            for item in exp[0][TK_EXPR]:
                ret.append(
                    get_if_str(parser_search_name(item, self.comment_map)))
            comment = ' \nor '.join(ret)
            exp[0][TK_EXPR] = comment
            tlist.append(exp[0])
            start, end = exp[0][TK_START], exp[0][TK_END]

            self.push(['SINGLE', start, end, 'NOP'])
            tlist.append(self.rpop())

            self.push(['DONECASE', start, end, tlist])

        elif (token == 'CASE' or token == 'DEFAULT'):
            # case/default分支
            exp.append(self.rpop())

            exp[0][TK_END] = exp[0][TK_START]

            exp[0][TK_EXPR] = parser_search_name(exp[0], self.comment_map)
            if (token != 'DEFAULT'):
                exp[0][TK_EXPR] = get_if_str(exp[0][TK_EXPR])

            start = exp[0][TK_START]
            end = exp[0][TK_END]

            tlist.append(exp[0])

            self.push(['SINGLE', start, end, 'NOP'])
            tlist.append(self.rpop())

            self.push(['DONE' + token, start, end, tlist])

        elif (token == 'SWITCH'):
            # switch语句
            judge = self.rpop()
            states = self.rpop()

            newstates = self.get_switch(states)

            exp.append(judge)
            exp.append(newstates)

            exp[0][TK_END] = exp[1][TK_END]

            exp[0][TK_EXPR] = parser_search_name(exp[0], self.comment_map)

            start = exp[0][TK_START]
            end = exp[0][TK_END]

            tlist.append(exp[0])
            tlist.append(exp[1])

            self.push(['DONE' + token, start, end, tlist])

        elif (token == 'FOR'):
            # for循环：特殊处理三部分（初始化;条件;迭代）
            exp.append(self.rpop())
            exp.append(self.rpop())

            exp[0][TK_END] = exp[1][TK_END]

            # 解析注释中的for三部分
            comment = parser_search_name(exp[0], self.comment_map)
            lines = comment.split(';')
            if (len(lines) > 1):
                lines.append('')
                lines.append('')
                # TK_EXPR 为FOR判断条件，TK_EXPR0为初始化，TK_EXPR2为迭代
                if (lines[0].strip() != ''):
                    exp[0][TK_EXPR0] = lines[0]
                if (lines[1].strip() != ''):
                    exp[0][TK_EXPR] = lines[1]
                if (lines[2].strip() != ''):
                    exp[0][TK_EXPR2] = lines[2]
            else:
                exp[0][TK_EXPR] = comment

            exp[0][TK_EXPR] = get_if_str(exp[0][TK_EXPR])

            start = exp[0][TK_START]
            end = exp[0][TK_END]

            tlist.append(exp[0])
            tlist.append(exp[1])

            self.push(['DONE' + token, start, end, tlist])
            
        elif (token == 'BREAK' or token == 'CONTINUE' or token == 'GOTO'
              or token == 'RETURN'):
            # 控制流语句
            exp.append(self.rpop())
            tlist.append(exp[0])

            exp[0][TK_EXPR] = token[0:3] + ' ' + parser_search_name(
                exp[0], self.comment_map)

            start = exp[0][TK_START]
            end = exp[0][TK_END]

            self.push(['DONE' + token, start, end, tlist])
            
        elif (token == 'FUNC'):
            # 函数定义
            raw_expr = self.rpop()
            declaration = raw_expr[TK_EXPR]
            if (ENABLE_HANDLE_DEBUG == 1):
                self.trace()

            while (self.len() > 0):
                exp.append(self.rpop())
                tlist.append(
                    self.parser_search_comment(exp[-1], self.comment_map,
                                               exp[-1][TK_START],
                                               exp[-1][TK_END]))

            # 提取函数名（取(之前的标识符）
            namel = declaration.split()
            for i in range(1, len(namel)):
                if (namel[i] == '('):
                    i = i - 1
                    break
            name = namel[i]
            if ENABLE_HANDLE_DEBUG == 1:
                print(('FUNC', name, exp))

            # 更新起始行
            start = raw_expr[TK_START]
            if (start != 0 and start < exp[0][TK_START]):
                exp[0][TK_START] = start

            # 打印函数
            self.printer(name, exp[0])
            return

    # ========================================================================
    # 函数数据处理
    # ========================================================================

    def update_fun_data(self, dst_map, index, data_map, filter=-1):
        """
        更新函数内的数据
        
        将data_map中的数据按格式添加到dst_map[index]。
        
        Args:
            dst_map: 目标字典
            index: 目标键
            data_map: 数据源字典
            filter: 过滤器，-1表示不过滤，否则只匹配对应值
        """
        # -1表示不判断，>=0的数表示仅有匹配的值才会输出
        key_i = 0
        line_len = 0
        # 获取函数作用域内的函数列表，依次添加到index中
        for key in data_map.keys():
            if (filter == -1) or (data_map[key] == filter):
                elem = FUN_STR_FMT % key
                line_len += len(elem)
                dst_map[index] += elem
                if line_len > FUN_STR_WIDTH:
                    dst_map[index] += '\n'
                    line_len = 0
                # 为便于显示，增加自动换行功能
                key_i += 1

    def get_param_map(self, data_map, filter=-1):
        """
        获取参数映射
        
        Args:
            data_map: 数据字典
            filter: 过滤器
            
        Returns:
            dict: 符合条件的键值映射
        """
        r = {}
        # 获取函数作用域内的函数列表，依次添加到index中
        for key in data_map.keys():
            if (filter == -1) or (data_map[key] == filter):
                r[key] = ""
        return r

    def analyze_gvin_data(self, text):
        """
        分析全局变量输入数据
        
        使用vlex词法分析器从文本中提取标识符作为全局变量。
        
        Args:
            text: 输入文本（通常是函数体代码）
            
        Returns:
            dict: {变量名: VTYPE_GLOBAL}
        """
        l = self.slex.lexer
        tokens = l.input(text)
        r = {}
        while 1:
            tok = l.token()
            if not tok:
                break
            if (tok.type == 'ID'):
                # 过滤以_t结尾的类型名
                if not tok.value.endswith('_t'):
                    tok_value = tok.value.replace('[]', '')
                    r[tok_value] = VTYPE_GLOBAL
        return r

    def update_gvarin(self, out_map, fun_map):
        """
        更新输入全局变量映射
        
        在输入变量中剔除函数调用和局部变量。
        
        Args:
            out_map: 输出映射
            fun_map: 函数调用映射
        """
        for key in fun_map:
            try:
                self.gvarin_map[key] = VTYPE_FUN
            finally:
                pass

        for key, v in list(out_map.items()):
            if v != VTYPE_GLOBAL:
                try:
                    self.gvarin_map[key] = v
                finally:
                    pass

    def clean_gvarout(self, output_map, in_map):
        """
        清理输出全局变量中的结构体成员
        
        如果输出变量包含'.'（结构体成员），且基名在输入映射中，则删除。
        
        Args:
            output_map: 输出变量映射（会被修改）
            in_map: 输入变量映射
        """
        key_list = []
        for key, v in list(output_map.items()):
            if '.' in key:
                mb = key.split('.')[0].replace('[]', '')
                if mb in in_map:
                    logging.debug(f'Deleting key {key}')
                    key_list.append(key)
        for key in key_list:
            del output_map[key]

    def get_fun_header(self, name, elist):
        """
        获取函数头部信息
        
        综合注释和代码分析结果，生成函数说明字典。
        
        Args:
            name: 函数名
            elist: doxygen注释元素列表 [[tag, content], ...]
            
        Returns:
            dict: 函数字典，包含proto, brief, param, return, fcall等
        """
        fun_str_map = {
            'proto': '',
            'brief': '',
            'param': '',
            'return': '',
            'fcall': '',
            'gvarin': '',
            'gvarout': '',
            'details': '',
        }

        # 更新函数调用
        self.update_fun_data(fun_str_map, 'fcall', self.fcall_map)

        # 分析输入全局变量
        self.gvarin_map = self.analyze_gvin_data(self.expr)

        # 更新变量映射
        self.update_gvarin(self.gvarout_map, self.fcall_map)
        self.update_fun_data(fun_str_map, 'gvarin', self.gvarin_map,
                             VTYPE_GLOBAL)
        self.clean_gvarout(self.gvarout_map, self.gvarin_map)
        self.update_fun_data(fun_str_map, 'gvarout', self.gvarout_map,
                             VTYPE_GLOBAL)

        pmap = self.get_param_map(self.gvarout_map, VTYPE_PARAM)

        # 解析doxygen注释
        for elem in elist:
            str1, str2 = get_split_str(elem[1])
            if (elem[0] == 'brief'):
                if (name == str1):
                    fun_str_map['brief'] += str2
                else:
                    fun_str_map['brief'] += elem[1]
            elif (elem[0] == 'param'):
                if str1 != '':
                    pmap[str1.lstrip()] = get_format_str(str2)
            elif (elem[0] == 'return'):
                fun_str_map[elem[0]] += get_format_str(elem[1])
            else:
                try:
                    fun_str_map[elem[0]] += elem[1]
                except:
                    fun_str_map[elem[0]] = elem[1]
                    pass

        # 处理未识别的参数
        for k, v in list(pmap.items()):
            fun_str_map['param'] += k
            fun_str_map['param'] += ' : '
            fun_str_map['param'] += get_format_str(v)
            fun_str_map['param'] += '\n'

        fun_str_map['proto'] = self.declaration_get()

        # 默认值填充
        if (fun_str_map['brief'] == ''):
            fun_str_map['brief'] = comment_null_table['brief'] % name

        for key in fun_str_map.keys():
            if (fun_str_map[key] == ''):
                fun_str_map[key] = comment_null_table[key]

        # 重置函数相关变量
        self.gvarout_map = {}
        self.fcall_map = {}
        self.expr = ""

        return fun_str_map

    # ========================================================================
    # 打印输出方法
    # ========================================================================

    def con_printer(self, name, header, exp, depth):
        """
        控制台打印器
        
        调用ccondraw打印函数头部和伪代码。
        
        Args:
            name: 函数名
            header: 函数字典
            exp: 语法树节点
            depth: 展开深度
        """
        from . import ccondraw
        ccondraw.print_fun_header(name, header)
        click.secho(FUN_SEP, fg='yellow')
        click.secho(f'函数伪代码: {name}', fg='green')
        print(FUN_LFMT % exp[TK_START], '{')
        ret = ccondraw.print_func_exp(exp, 1, 0)
        print(FUN_LFMT % exp[TK_END], '}')
        print()

    def basic_printer(self, name, header, exp, depth):
        """
        基础打印器
        
        根据verbose标志决定是否打印到控制台。
        
        Args:
            name: 函数名
            header: 函数字典
            exp: 语法树节点
            depth: 展开深度
        """
        if self.flag_get('verbose'):
            self.con_printer(name, header, exp, depth)

    def extend_printer(self, name, header, exp, depth):
        """
        扩展打印器（抽象方法）
        
        由子类实现具体的文档生成功能。
        
        Args:
            name: 函数名
            header: 函数字典
            exp: 语法树节点
            depth: 展开深度
        """
        if self.flag_get('nodraw') == 0:
            print('----------adding page:', name, '@depth:', depth)
        pass

    def printer(self, name, exp):
        """
        主打印入口
        
        协调整个处理流程：
        1. 检查过滤器
        2. 解析doxygen注释
        3. 生成函数头部信息
        4. 调用基础打印器和扩展打印器
        
        Args:
            name: 函数名
            exp: 语法树节点
        """
        # 过滤器检查
        match = self.flag_get('filter')
        if match != '':
            if name.find(match) >= 0:
                print('_____Filter ', match, 'OK for', name)
            else:
                return

        # 确保表达式有效（首、尾行号正常）
        if (exp[TK_START] < exp[TK_END]):
            depth = DEFAULT_DEPTH

            # 解析注释
            comment = self.get_comment(exp[TK_START])
            comment += '\n'

            # 深度控制
            if self.flag_get('force-depth') != 0:
                # 如果设置了强制深度，照此执行
                depth = self.flag_get('force-depth')
            else:
                depth2 = self.get_comment_depth(exp[TK_START])
                depth = self.flag_get('depth')
                # 如果注释中获取的深度<
                if (depth2 != DEFAULT_DEPTH):
                    depth = depth2

            # 解析doxygen注释，此处lexer需要指定，否则在根目录中调用有问题
            res = self.doxyp.parse(comment, lexer=self.lexer)

            header = self.get_fun_header(name, self.elist)

            self.basic_printer(name, header, exp, depth)
            self.extend_printer(name, header, exp, depth)

            del self.elist[:]


# 定义全局变量
# gfun=cgrammar()
