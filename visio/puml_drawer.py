#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# PlantUML 流程图绘制器 (puml_drawer.py)
# -----------------------------------------------------------------------------
# 将语法树节点转换为 PlantUML 活动图代码。
#
# 功能:
#     - 递归遍历语法树，生成 PlantUML 语法
#     - 支持各种控制结构：if/else, while, for, do-while, switch/case
#     - 支持 break/continue/goto/return 控制流语句
#     - 注释优先于代码显示（流程图语义）
#
# PlantUML 活动图语法:
#     start/stop         - 开始/结束节点
#     :action;           - 活动节点
#     if (cond) then (Y) - if分支开始
#     else(N)            - else分支
#     endif              - if结束
#     while (cond) is (Y)- while循环
#     endwhile           - while结束
#     repeat             - do-while开始
#     repeat while(cond) - do-while条件
#
# 节点类型处理:
#     DONENODE      - 普通活动节点
#     DONEIFELSE    - if-else条件分支
#     DONEIF        - if条件分支
#     DONEWHILE     - while循环
#     DONEFOR       - for循环（展开为init;while;inc）
#     DONEDO        - do-while循环
#     DONESWITCH    - switch语句
#     DONECASE      - case分支
#     DONEDEFAULT   - default分支
#     DONEBREAK     - break语句（带循环检测）
#     DONECONTINUE  - continue语句
#     DONEGOTO      - goto语句
#     DONERETURN    - return语句
#
# 使用示例:
#     from visio.puml_drawer import puml_drawer
#     drawer = puml_drawer("output", comment_map)
#     puml_code = drawer.draw_fun("func_name", syntax_tree, 0, 0, depth=10)
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import sys
import logging

sys.path.insert(0, '..')
from common.cglobal import *

# =============================================================================
# 可视化节点索引常量
# =============================================================================

TV_ID = 0      # 节点ID
TV_X = 1       # X坐标
TV_Y = 2       # Y坐标
TV_TYPE = 3    # 节点类型
TV_TEXT = 4    # 显示文本
TV_LINE = 5    # 源代码行号


def get_conn_text(node1):
    """
    获取连接文本表示
    
    将节点转换为连接文本，支持节点对象、整数ID或None。
    
    Args:
        node1: 节点对象、整数ID或None
        
    Returns:
        str: 连接文本，如"[05]"、"5"或"nil"
    """
    try:
        t1 = "[%2d]" % node1[TV_ID]
    except:
        if isinstance(node1, int):
            t1 = "%2d" % node1
        elif node1 is None:
            t1 = "nil"
    return t1


# =============================================================================
# 字符串缓冲区类
# =============================================================================

class StringBuff:
    """
    字符串缓冲区
    
    捕获标准输出到字符串列表，用于收集 PlantUML 代码。
    通过重定向sys.stdout实现。
    
    Attributes:
        _list (list): 存储输出的字符串列表
        raw_handler: 原始标准输出
        
    使用示例:
        buf = StringBuff()
        print("Hello")  # 被捕获到_list
        result = buf.pop()  # 恢复stdout并返回收集的内容
    """

    def __init__(self):
        """初始化缓冲区，重定向stdout"""
        self._list = []
        self.raw_handler = sys.stdout
        sys.stdout = self

    def write(self, line):
        """
        写入方法（捕获print输出）
        
        Args:
            line: 要写入的字符串
        """
        self._list.append(line)

    def pop(self):
        """
        恢复stdout并返回收集的内容
        
        Returns:
            str: 收集的所有输出拼接成的字符串
        """
        sys.stdout = self.raw_handler
        return ''.join(self._list)


# =============================================================================
# PlantUML 绘制器类
# =============================================================================

class puml_drawer:
    """
    PlantUML 流程图绘制器
    
    将语法树转换为 PlantUML 活动图代码。
    
    Attributes:
        end_list (list): 结束节点列表（未使用）
        count (int): 节点计数器
        comment_map (dict): 注释映射 {行号: 注释内容}
        _comment_cache (dict): 注释缓存副本
        
    设计说明:
        - 使用StringBuff捕获输出
        - 递归处理语法树节点
        - 注释优先级高于代码
        - 支持in_loop标记处理break语句
    """

    def __init__(self, filename, comment_map=None, autoquit=0):
        """
        初始化绘制器
        
        Args:
            filename: 输出文件名（未使用）
            comment_map: 注释映射字典
            autoquit: 自动退出标志（未使用）
        """
        self.end_list = []
        self.count = 0
        # 保存原始comment_map的引用，用于实时查找
        self.comment_map = comment_map if comment_map is not None else {}
        # 保存一份注释的副本，防止被cgrammar删除
        self._comment_cache = {}

    def _ensure_cache(self):
        """
        确保注释缓存已填充
        
        在首次访问时从comment_map复制所有注释。
        这是因为cgrammar可能会删除已使用的注释。
        """
        if not self._comment_cache and self.comment_map:
            self._comment_cache = self.comment_map.copy()

    def get_node_text(self, node):
        """
        获取节点显示的文本，优先使用注释内容
        
        优先级:
            1. 缓存的注释 (防止cgrammar删除)
            2. 当前的comment_map
            3. 节点的代码表达式
            
        Args:
            node: 语法树节点 [TYPE, START, END, EXPR, ...]
            
        Returns:
            str: 节点显示文本
        """
        line_no = node[TK_START]
        # 确保缓存已填充
        self._ensure_cache()
        # 首先尝试从缓存的注释中获取
        if line_no in self._comment_cache:
            comment = self._comment_cache[line_no].strip()
            if comment:
                return comment
        # 其次尝试从当前的 comment_map 获取
        if line_no in self.comment_map:
            comment = self.comment_map[line_no].strip()
            if comment:
                return comment
        # 没有注释则使用代码表达式
        return node[TK_EXPR].strip()
        # 首先尝试从缓存的注释中获取
        if line_no in self._comment_cache:
            comment = self._comment_cache[line_no].strip()
            if comment:
                return comment
        # 其次尝试从当前的 comment_map 获取（可能被cgrammar删除部分注释）
        if line_no in self.comment_map:
            comment = self.comment_map[line_no].strip()
            if comment:
                return comment
        # 没有注释则使用代码表达式
        return node[TK_EXPR].strip()

    def print_prefix(self, n, x):
        """
        打印缩进前缀
        
        Args:
            n: 行号（未使用，保留参数）
            x: 缩进级别
        """
        print(FUN_DELIM * x, end=' ')

    def print_blank(self):
        """打印空行"""
        print('')

    def draw_fun(self, name, exp, x, y, max_depth=100, dirpath=''):
        """
        绘制完整函数流程图
        
        生成包含开始/结束标记的完整 PlantUML 代码。
        
        Args:
            name: 函数名
            exp: 语法树根节点
            x: 初始缩进级别
            y: 初始深度
            max_depth: 最大展开深度
            dirpath: 输出目录（未使用）
            
        Returns:
            str: 完整 PlantUML 代码
        """
        # 在绘制前填充注释缓存
        self._ensure_cache()
        buf = StringBuff()
        print('```plantuml')
        print('@startuml')
        print('title 函数%s流程图' % name)
        print(' start')
        self.print_func_exp(exp, x, y)
        print(' stop')
        print('@enduml')
        print('```')
        ret = buf.pop()
        return ret

    def print_func_exp(self,
                       exp,
                       x=0,
                       y=0,
                       ext=None,
                       first_case=False,
                       in_loop=False):
        """
        递归打印函数表达式（核心方法）
        
        根据节点类型采用不同的 PlantUML 语法生成策略。
        
        Args:
            exp: 语法树节点
            x: 水平缩进级别
            y: 垂直递归深度
            ext: 扩展信息（用于case标签）
            first_case: 是否是switch的第一个case
            in_loop: 当前是否在循环内部（影响break处理）
            
        Returns:
            str: 节点类型字符串
            
        节点处理:
            DONE*: 各种控制结构
            DONENODE/DONECODE: 普通活动节点
            NODE: 递归处理子节点
        """
        ttype = exp[TK_TYPE]
        label_case_list = []

        # 处理@alias标签（特殊注释语法）
        if (ttype[0:4] == 'DONE'):
            try:  # 打印alias
                node = exp[TK_EXPR][0]
                node_data = node
                comment = get_exp_head(node_data)

                idx = comment.index('@alias')
                text = comment[idx + 7:].rstrip()
                if (text[-1] == '?'):
                    text2 = text[0:-1]
                # self.draw_node(NODE_P, x, y+count, text2, node[TK_START])
                self.print_prefix(node[TK_START], x)
                print(':@%s@;' % text2)
                return 'DONENODE'
            except:
                pass

        # logging.debug(f'func_head {ttype} {in_loop}')
        if (ttype == 'DONENODE' or ttype == 'DONECODE'):
            # 普通代码节点：打印活动
            for node in (exp[TK_EXPR]):
                self.print_prefix(node[TK_START], x)
                print(':%s;' % self.get_node_text(node))
                
        elif (ttype == 'DONEBREAK' or ttype == 'DONECONTINUE'
              or ttype == 'DONEGOTO'):
            # 控制流跳转语句
            op = ttype[4:len(ttype)].lower()
            # 对于 break/continue/goto，只打印注释（如果有），不打印代码本身
            for node in (exp[TK_EXPR]):
                line_no = node[TK_START]
                self._ensure_cache()
                comment = None
                # 尝试获取注释
                if line_no in self._comment_cache:
                    comment = self._comment_cache[line_no].strip()
                elif line_no in self.comment_map:
                    comment = self.comment_map[line_no].strip()
                # 只有有注释时才打印动作
                if comment:
                    self.print_prefix(line_no, x)
                    print(':%s;' % comment)
            if ttype == 'DONEBREAK':
                self.print_prefix(node[TK_START], x)
                logging.debug(f'break in_loop {in_loop}')
                if in_loop:
                    print('break')
            self.print_blank()
            
        elif (ttype == 'DOENRETURN'):
            # return语句（注意：原代码拼写为DOENRETURN）
            op = ttype[4:len(ttype)].lower()
            for node in (exp[TK_EXPR]):
                self.print_prefix(node[TK_START], x)
                print(':%s;' % self.get_node_text(node))
            print('stop')
            
        elif (ttype == 'DONEIFELSE'):
            # IF-ELSE结构
            node = exp[TK_EXPR][0]

            self.print_prefix(node[TK_START], x)
            print('if (%s) then (Y)' % (self.get_node_text(node)))

            # 递归打印if分支
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1, in_loop=in_loop)

            # 获取ELSE
            self.print_prefix(node[TK_MID], x)
            print('else(N)')

            # 递归打印else分支
            self.print_func_exp(exp[TK_EXPR][2], x + 1, y + 1, in_loop=in_loop)

            self.print_prefix(node[TK_END], x)
            print('endif')

            self.print_blank()
            
        elif (ttype == 'DONEIF'):
            # IF结构（单分支）
            op = ttype[4:len(ttype)].lower()
            node = exp[TK_EXPR][0]

            self.print_prefix(node[TK_START], x)
            print(op + '(%s) then (Y)' % (self.get_node_text(node)))

            # 递归打印if体
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1, in_loop=in_loop)

            self.print_prefix(node[TK_END], x)
            print('end%s' % (op))
            self.print_blank()
            
        elif (ttype == 'DONEWHILE'):
            # WHILE循环
            op = ttype[4:len(ttype)].lower()
            node = exp[TK_EXPR][0]

            self.print_prefix(node[TK_START], x)
            print(op + '(%s) is (Y)' % (self.get_node_text(node)))

            # 标记在循环内部，用于break处理
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1, in_loop=True)

            self.print_prefix(node[TK_END], x)
            print('end%s' % (op))
            self.print_blank()
            
        elif (ttype == 'DONECASE'):
            # CASE分支
            node = exp[TK_EXPR][0]

            self.print_prefix(node[TK_START], x)
            tk_expr = self.get_node_text(node)

            if first_case:
                print(f'if ({tk_expr}) then (Y)')
            else:
                print(f'elseif ({tk_expr}) then (Y)')

            # 递归打印case体
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1, in_loop=in_loop)
            
        elif (ttype == 'DONELABELCASE'):
            # LABEL CASE（多case合并）
            node = exp[TK_EXPR][0]
            label_case_list.append(node)
            
        elif (ttype == 'DONEDEFAULT'):
            # DEFAULT分支
            node = exp[TK_EXPR][0]

            self.print_prefix(node[TK_START], x)
            print('else (%s)' % (self.get_node_text(node)))

            # 递归打印default体
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1)

        elif (ttype == 'DONEDO'):
            # DO-WHILE循环
            op = ttype[4:len(ttype)].lower()
            node = exp[TK_EXPR][0]
            self.print_prefix(node[TK_START], x)
            print('repeat')

            # 标记在循环内部
            logging.debug('do in_loop')
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1, in_loop=True)

            self.print_prefix(node[TK_END], x)
            print('repeat while (%s)' % (self.get_node_text(node)))
            self.print_blank()
            
        elif (ttype == 'DONEFOR'):
            # FOR循环（展开为：初始化;while;增量）
            op = ttype[4:len(ttype)].lower()
            node = exp[TK_EXPR][0]

            # 打印初始化
            self.print_prefix(node[TK_START], x)
            print(':%s;' % (node[TK_EXPR0].strip()))

            # 打印while条件
            self.print_prefix(node[TK_START], x)
            print('while (%s) is (Y)' % (self.get_node_text(node)))

            # 循环体
            logging.debug('for in_loop')
            self.print_func_exp(exp[TK_EXPR][1], x + 1, y + 1, in_loop=True)

            # 打印增量
            self.print_prefix(node[TK_END], x)
            print(':%s;' % (node[TK_EXPR2].strip()))
            self.print_prefix(node[TK_END], x)
            print('endwhile (N)')
            self.print_blank()
            
        elif (ttype == 'DONESWITCH'):
            # SWITCH语句
            op = ttype[4:len(ttype)].lower()
            node = exp[TK_EXPR][0]

            self.print_prefix(node[TK_START], x)
            print(':switch %s;' % (self.get_node_text(node)))
            
            # 遍历所有case分支
            j = 0
            for idx, node2 in enumerate(exp[TK_EXPR][1][TK_EXPR]):
                if (node2[TK_TYPE] == 'DONECASE'
                        or node2[TK_TYPE] == 'DONEDEFAULT'):
                    j += 1
                self.print_func_exp(node2,
                                    x + j,
                                    y + 1,
                                    node[-1],
                                    first_case=True if (idx == 0) else False,
                                    in_loop=in_loop)
            self.print_prefix(node[TK_END], x)
            print('endif ')

            self.print_blank()
            
        elif (ttype == 'NODE'):
            # 复合节点：递归处理所有子节点
            for node in exp[TK_EXPR]:
                self.print_func_exp(node, x, y, in_loop=in_loop)

        return ttype
