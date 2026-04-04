#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 语法处理基础类 (chandler.py)
# -----------------------------------------------------------------------------
# 提供C语法分析的基类功能，包括：
#     - Token堆栈管理（push/pop/top）
#     - 代码行存储和提取
#     - 全局变量/参数/函数调用追踪
#     - 标志位管理
#     - 注释提取和深度解析
#
# 设计说明:
#     此类作为cgrammar的基类，封装与语法分析相关的状态管理和工具方法。
#     不直接进行语法解析，但提供解析所需的基础设施。
#
# 主要属性:
#     token_list   - Token堆栈，存储语法分析中间结果
#     code_lines   - 代码行字典 {行号: 代码内容}
#     comment_map  - 注释映射 {行号: 注释内容}
#     gvarout_map  - 输出全局变量追踪 {变量名: 类型}
#     gvarin_map   - 输入全局变量追踪（通过expr字符串）
#     fcall_map    - 函数调用追踪 {函数名: 行号}
#     param_map    - 参数映射 {参数名: 类型}
#     flags        - 配置标志字典
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

from .debug import *
from .cglobal import *


class fbasic():
    """
    函数处理基础类
    
    提供C语法分析的基础功能，管理解析状态和数据。
    作为cgrammar的基类使用。
    
    Attributes:
        flags (dict): 配置标志 {'depth': 10, 'filter': '', 'silent': 0}
        semi_line (int): 当前语句结束行号
        cur_line (int): 当前处理行号
        def_lines (list): 函数定义行列表 [[行号, 代码], ...]
        code_lines (dict): 代码行存储 {行号: 代码}
        fcall_map (dict): 函数调用映射 {函数名: 行号}
        token_list (list): Token堆栈 [token, ...]
        gvarin_map (dict): 输入全局变量映射
        expr (str): 当前表达式字符串（用于全局变量分析）
        gvarout_map (dict): 输出全局变量映射 {变量名: VTYPE}
        param_map (dict): 参数映射 {参数名: VTYPE_PARAM}
        comment_map (dict): 注释映射 {行号: 注释内容}
    """

    def __init__(self):
        """
        初始化基础处理器
        
        初始化所有状态变量和数据结构。
        """
        self.flags = {'depth': DEFAULT_DEPTH, 'filter': '', 'silent': 0}
        self.semi_line = 0
        self.cur_line = 0
        self.def_lines = []  # 用于存储预定义的line
        self.code_lines = {}  # 找不到有效注释时，通过code lines存储语句
        self.fcall_map = {}  # 用于存储所调用的函数
        self.token_list = []  # token的堆栈
        self.gvarin_map = {}  # 输入的全局变量的map
        self.expr = ""
        self.gvarout_map = {}  # 输出的全局变量的map
        self.param_map = {}  # 参数的map
        self.comment_map = {}  # 注释

    def reset(self):
        """
        重置解析状态
        
        清空函数相关的追踪数据，保留注释映射。
        在解析新函数前调用。
        """
        self.fcall_map.clear()
        self.gvarin_map.clear()
        self.expr = ""
        self.gvarout_map.clear()
        self.param_map.clear()

    def reset_param(self, pstr):
        """
        从函数原型重置参数映射
        
        解析函数原型字符串，提取参数名并更新param_map。
        同时清理gvarout_map中过期的参数标记。
        
        Args:
            pstr: 函数原型字符串，如 "int func(int a, int b)"
        """
        # 提取参数列表部分（括号之间）
        raw_param = pstr.split(')')[0].split('(')[-1].strip()
        if raw_param:
            raw_plist = raw_param.split(',')
            try:
                # 提取每个参数的变量名（最后一个单词）
                plist = [p.split()[-1] for p in raw_plist]
            except Exception as e:
                print((e, pstr, raw_plist))
                plist = []
        else:
            plist = []
        self.param_map.clear()
        # 如果已有的列表中包含某个参数，而该参数不在原型中，说明是之前的声明留下的，改为全局变量
        for k, v in list(self.gvarout_map.items()):
            if v == VTYPE_PARAM:
                if not k in plist:
                    self.gvarout_map[k] = VTYPE_GLOBAL
        pass

    # 初始化
    def init(self):
        """清空token堆栈"""
        del self.token_list[:]

    # 获取栈顶
    def top(self, offset=0):
        """
        获取token堆栈顶部元素
        
        Args:
            offset: 偏移量，0表示栈顶，1表示栈顶下一个
            
        Returns:
            token: 堆栈中的token
        """
        return self.token_list[-1 - offset]

    # raw push
    def rpush(self, token):
        """
        原始压栈操作
        
        直接压入token，不触发解析。
        
        Args:
            token: 要压入的token
        """
        self.token_list.append(token)

    # raw pop
    def rpop(self):
        """
        原始出栈操作
        
        直接弹出并返回栈顶token，不触发解析。
        
        Returns:
            token: 栈顶token
        """
        return self.token_list.pop()

    # 系统解析函数
    def parse(self):
        """
        解析入口（抽象方法）
        
        由子类实现具体的语法解析逻辑。
        """
        pass

    # 压入相关操作，并根据类型进行解析
    def push(self, token):
        """
        压入token并触发解析
        
        将token压入堆栈后，调用parse()进行语法解析。
        
        Args:
            token: 要压入的token
        """
        self.token_list.append(token)
        if ENABLE_GENERIC_DEBUG == 1:
            print(('push', self.len(), token))
        self.parse()

    # 针对token list的pop操作
    def pop(self):
        """
        出栈操作（抽象方法）
        
        由子类实现具体的出栈逻辑。
        """
        pass

    def len(self):
        """
        获取token堆栈长度
        
        Returns:
            int: 堆栈中token数量
        """
        return len(self.token_list)

    def trace(self):
        """
        打印token堆栈（调试用）
        """
        if ENABLE_GENERIC_DEBUG == 1:
            print(('tklist', self.token_list))

    def flag_set(self, index, value):
        """
        设置标志位
        
        Args:
            index: 标志名
            value: 标志值
        """
        self.flags[index] = value

    def flag_get(self, index):
        """
        获取标志位
        
        Args:
            index: 标志名
            
        Returns:
            标志值，不存在返回0
        """
        return self.flags.get(index, 0)

    def semil_update(self, line):
        """
        更新语句结束行号
        
        Args:
            line: 行号
        """
        self.semi_line = line

    def semil_get(self):
        """
        获取语句结束行号
        
        Returns:
            int: 语句结束行号
        """
        return self.semi_line

    # 更新当前行
    def curl_get(self):
        """
        获取当前行号
        
        Returns:
            int: 当前行号
        """
        return self.cur_line

    def curl_update(self, p):
        """
        从PLY解析对象更新当前行号
        
        遍历解析对象的lineno信息，更新cur_line。
        
        Args:
            p: PLY解析对象
        """
        for i in range(1, len(p)):
            if (p.lineno(i) != 0):
                self.cur_line = p.lineno(i)

    def declaration_update(self, line, code):
        """
        更新函数声明
        
        存储函数定义行，并解析参数。
        
        Args:
            line: 行号
            code: 函数声明代码
        """
        self.reset_param(code)
        self.def_lines.append([line, code])

    def declaration_get(self, off=0):
        """
        获取函数声明
        
        Args:
            off: 偏移量，0表示最近一次
            
        Returns:
            str: 函数声明代码
        """
        return self.def_lines[-1 - off][1]

    #
    def code_push(self, line, code):
        """
        存储代码行
        
        Args:
            line: 行号
            code: 代码内容
        """
        self.code_lines[line] = code

    def code_pop(self, start, end):
        """
        提取代码行范围
        
        提取start到end范围内的代码，用分号连接。
        
        Args:
            start: 起始行号
            end: 结束行号
            
        Returns:
            str: 合并后的代码字符串（去掉末尾分号）
        """
        ret = ""
        # 此时需要注意range是一个开区间
        for i in range(start, end + 1):
            if i in self.code_lines:
                ret += self.code_lines[i]
                ret += ';'
        return ret[0:-1]

    def code_trace(self):
        """
        打印代码行映射（调试用）
        """
        for elem in self.code_lines.keys():
            if ENABLE_GENERIC_DEBUG == 1:
                print('#L', elem, self.code_lines[elem])

    # 更新当前的序列
    def update(self, p, trim=0, sep=' '):
        """
        更新表达式序列
        
        合并解析对象的多个元素到p[0]。
        
        Args:
            p: PLY解析对象
            trim: 尾部跳过的元素数量
            sep: 分隔符
        """
        if USELIST == 1:
            p[0] = []
            for i in range(1, len(p) - trim):
                p[0].append(p[i])
        else:
            updatestr(p, trim, sep)

        start, end = p.linespan(-1)
        p.set_lineno(0, p.lineno(1))

        self.curl_update(p)

    # 判定指定的分支中是否需要额外压入语句 （用于更新lineno的数值）
    def extra_get(self, p, si):
        """
        判断是否需要额外处理
        
        如果分支不以'}'结尾且分号数量<=1，需要额外处理。
        
        Args:
            p: PLY解析对象
            si: 元素索引
            
        Returns:
            int: 1需要处理，0不需要
        """
        if (ENABLE_YTOOL_DEBUG == 1):
            print('===ex get', p[si], self.semil_get())
        if (p[si][-2] != '}' and p[si].count(';') <= 1):
            return 1
        return 0

    def sextra_push(self, p, si, start=0, end=0):
        """
        特殊额外压入（带起止行号）
        
        如果条件满足，创建SINGLE节点并压入。
        
        Args:
            p: PLY解析对象
            si: 元素索引
            start: 起始行号（可选）
            end: 结束行号（可选）
            
        Returns:
            int: 结束行号或0
        """
        if (ENABLE_YTOOL_DEBUG == 1):
            print('===sex', p[si], self.semil_get())
        semi = self.semil_get()
        if (p[si][-2] != '}' and p[si].count(';') <= 1):
            elem = ['SINGLE', p.lineno(si), semi, p[si]]
            if (start != 0):
                elem[1] = start
            if (end != 0):
                elem[2] = end
            if (elem[1] == 0):
                elem[1] = semi
            self.push(elem)
            return elem[2]
        return 0

    # 如果需要，将额外的元素事先压入
    # 通过判断元素的第一个字符是不是'{'如果是，说明已经作为{}压入，不管
    # 通过判断元素的最后一个有效字符是不是'}'如果是，说明已经作为{}压入，不进行额外处理
    #    如果不是，再判断是否是其他的复合语句，
    #        如果是（;数量>1），也不压入
    #        如果不是复合语句，将statement压入
    #
    def extra_push(self, p, si, start=0):
        """
        额外压入处理
        
        对于简单的单语句，创建SINGLE节点压入堆栈。
        
        Args:
            p: PLY解析对象
            si: 元素索引
            start: 起始行号（可选）
            
        Returns:
            int: 结束行号或0
        """
        if (ENABLE_YTOOL_DEBUG == 1):
            print('===ex', p[si], self.semil_get())
        if (p[si][-2] != '}' and p[si].count(';') <= 1):
            start, end = p.linespan(si)
            self.push(['SINGLE', p.lineno(si), end, p[si]])
            return end
        return 0

    def gvarout_push(self, name, value=VTYPE_GLOBAL):
        """
        添加输出全局变量
        
        更新gvarout_map，仅当新值更大时更新。
        
        Args:
            name: 变量名
            value: 变量类型值（VTYPE_GLOBAL等）
        """
        try:
            if (value > self.gvarout_map[name]):
                self.gvarout_map[name] = value
        except Exception as e:
            self.gvarout_map[name] = value

    def var_dump(self):
        """
        打印全局变量映射（调试用）
        """
        for k in self.gvarout_map.keys():
            print(k, self.gvarout_map[k])

    def gvarin_push(self, name, value=0):
        """
        添加输入全局变量
        
        将变量名添加到expr字符串，用于后续分析。
        过滤掉路径分隔符和全角冒号。
        
        Args:
            name: 变量名
            value: 行号（未使用）
        """
        # 过滤掉反斜杠、正斜杠（路径分隔符）和全角冒号，避免vlex报错
        name = name.replace('\\', '').replace('/', '').replace('：', '')
        if '.' in name:
            self.expr += name.replace('[]', '').split('.')[0] + ' '
        else:
            self.expr += name
        if ENABLE_GENERIC_DEBUG == 1:
            print(('=====gvin', name, value, self.expr))

    def param_push(self, name, value=VTYPE_PARAM):
        """
        添加参数
        
        Args:
            name: 参数名
            value: 参数类型值（默认VTYPE_PARAM）
        """
        self.param_map[name] = value

    def fun_push(self, line, name):
        """
        添加函数调用
        
        使用字典存储，自动合并相同调用。
        
        Args:
            line: 行号
            name: 函数名
        """
        self.fcall_map[name.rstrip()] = line

    # 获取注释
    def get_comment(self, start):
        """
        获取指定行的注释
        
        优先查找当前行，其次查找上一行。
        
        Args:
            start: 行号
            
        Returns:
            str: 注释内容，不存在返回空字符串
        """
        comment = ''
        cm = self.comment_map
        if (start in cm):
            comment = cm[start]
        elif (start - 1 in cm):
            comment = cm[start - 1]
        return comment

    # 获取函数的注释深度
    def get_comment_depth(self, start):
        """
        从注释中提取流程图深度
        
        查找@depth标签，如 "@depth 5" 返回5。
        
        Args:
            start: 函数起始行号
            
        Returns:
            int: 深度值，未指定返回DEFAULT_DEPTH
        """
        import re
        comment = self.get_comment(start)

        if comment != '':
            width_str = re.search(r'@depth\s+\d+', comment)
            try:
                # 确定模式匹配之后，获取后面的数值
                depth = int(width_str.group(0).split()[1])
                return depth
            except:
                return DEFAULT_DEPTH
        return DEFAULT_DEPTH
