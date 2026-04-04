#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 变体C词法分析器 (vlex.py)
# -----------------------------------------------------------------------------
# 基于PLY的C语言词法分析器变体，主要用于全局变量分析。
#
# 特点:
#     - 忽略简单注释（只提取 /** */ 格式的流程图注释）
#     - 支持从Key.txt文件加载自定义关键字
#     - 区分类型标识符（以_t结尾）和普通标识符
#     - 识别全大写标识符为常量
#
# Token类别:
#     - 关键字: auto, break, case, char, const, continue, default, do, double
#               else, enum, extern, float, for, goto, if, int, long, register
#               return, short, signed, sizeof, static, struct, switch, typedef
#               union, unsigned, void, volatile, while
#     - 注释: CPCOMMENT, CCOMMENT, NEWCOMMENT, FLOWCHART_COMMENT, DEV_COMMENT_POST
#     - 标识符: ID, TYPEID, ICONST, HCONST, FCONST, SCONST, CCONST, ZHCN
#     - 运算符: +, -, *, /, %, |, &, ~, ^, <<, >>, ||, &&, !, <, <=, >, >=, ==, !=
#     - 赋值: =, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=
#     - 自增/减: ++, --
#     - 结构: ->
#     - 条件: ?
#     - 分隔符: ( ) [ ] { } , . ; :
#     - 其他: ... (ELLIPSIS)
#
# 使用示例:
#     from clang.vlex import vlex
#     cm = {}  # 注释映射字典
#     lexer = vlex(cm)
#     lexer.load_keyword_from_file('Key.txt')
#     lexer.lexer.input(code)
#     for tok in lexer.lexer: print(tok)
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import sys
import ply.lex as lex


class vlex:
    """
    变体C词法分析器类
    
    用于解析C代码，特别关注标识符和注释。
    与标准clex不同，此lexer主要用于全局变量分析和注释提取。
    
    Attributes:
        reserved (tuple): C语言保留字列表
        tokens (tuple): 所有token类型
        cm_map (dict): 注释映射字典 {行号: 注释内容}
        keyword_map (dict): 自定义关键字映射 {关键字: 类型}
        lexer (Lexer): PLY词法分析器实例
    """
    
    # =======================================================================
    # C语言保留字
    # =======================================================================
    
    reserved = (
        'AUTO', 'BREAK', 'CASE', 'CHAR', 'CONST', 'CONTINUE', 'DEFAULT', 'DO', 'DOUBLE',
        'ELSE', 'ENUM', 'EXTERN', 'FLOAT', 'FOR', 'GOTO', 'IF', 'INT', 'LONG', 'REGISTER',
        'RETURN', 'SHORT', 'SIGNED', 'SIZEOF', 'STATIC', 'STRUCT', 'SWITCH', 'TYPEDEF',
        'UNION', 'UNSIGNED', 'VOID', 'VOLATILE', 'WHILE', 'CR',
    )

    # =======================================================================
    # Token类型定义
    # =======================================================================
    
    tokens = reserved + (
        # 注释类型
        'CPCOMMENT', 'CCOMMENT', 'NEWCOMMENT', 

        # 字面量
        'ID',           # 标识符
        'TYPEID',       # 类型标识符
        'ICONST',       # 整数常量
        'HCONST',       # 十六进制常量
        'FCONST',       # 浮点常量
        'SCONST',       # 字符串常量
        'CCONST',       # 字符常量
        'ZHCN',         # 中文标识符（反引号包裹）

        # 运算符
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        
        # 赋值运算符
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
        'LSHIFTEQUAL', 'RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',

        # 自增/减
        'PLUSPLUS', 'MINUSMINUS',

        # 结构解引用
        'ARROW',

        # 条件运算符
        'CONDOP',
        
        # 分隔符
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'LBRACE', 'RBRACE',
        'COMMA', 'PERIOD', 'SEMI', 'COLON',

        # 省略号
        'ELLIPSIS',
    )

    # =======================================================================
    # 忽略字符
    # =======================================================================
    
    t_ignore = ' \r\t\x0c'

    # =======================================================================
    # 字符串和字符常量（必须放在t_ID之前，确保优先匹配）
    # =======================================================================
    
    def t_SCONST(self, t):
        r'"([^"\\\n]|\\.|[^"\\\n\x00-\x7F])*?"'
        """
        字符串常量规则
        
        匹配双引号包围的字符串，支持包含中文字符的字符串。
        """
        t.type = 'SCONST'
        t.value = t.value[1:-1]  # 去掉首尾引号
        return t
    
    def t_CCONST(self, t):
        r"'([^'\\\n]|\\.|[^'\\\n\x00-\x7F])*?'"
        """
        字符常量规则
        
        匹配单引号包围的字符，支持中文字符。
        """
        t.type = 'CCONST'
        return t

    # ===================================================================
    # 简单Token规则（正则表达式）
    # =======================================================================
    # PLY使用t_前缀 + 大写token名定义简单规则
    
    # 运算符
    t_PLUS             = r'\+'
    t_MINUS            = r'-'
    t_TIMES            = r'\*'
    t_DIVIDE           = r'/'
    t_MOD              = r'%'
    t_OR               = r'\|'
    t_AND              = r'&'
    t_NOT              = r'~'
    t_XOR              = r'\^'
    t_LSHIFT           = r'<<'
    t_RSHIFT           = r'>>'
    t_LOR              = r'\|\|'
    t_LAND             = r'&&'
    t_LNOT             = r'!'
    t_LT               = r'<'
    t_GT               = r'>'
    t_LE               = r'<='
    t_GE               = r'>='
    t_EQ               = r'=='
    t_NE               = r'!='

    # 赋值运算符
    t_EQUALS           = r'='
    t_TIMESEQUAL       = r'\*='
    t_DIVEQUAL         = r'/='
    t_MODEQUAL         = r'%='
    t_PLUSEQUAL        = r'\+='
    t_MINUSEQUAL       = r'-='
    t_LSHIFTEQUAL      = r'<<='
    t_RSHIFTEQUAL      = r'>>='
    t_ANDEQUAL         = r'&='
    t_OREQUAL          = r'\|='
    t_XOREQUAL         = r'^='

    # 自增/减
    t_PLUSPLUS         = r'\+\+'
    t_MINUSMINUS       = r'--'

    # 结构解引用
    t_ARROW            = r'->'

    # 条件运算符
    t_CONDOP           = r'\?'

    # 分隔符
    t_LPAREN           = r'\('
    t_RPAREN           = r'\)'
    t_LBRACKET         = r'\['
    t_RBRACKET         = r'\]'
    t_LBRACE           = r'\{'
    t_RBRACE           = r'\}'
    t_COMMA            = r','
    t_PERIOD           = r'\.'
    t_SEMI             = r';'
    t_COLON            = r':'
    t_ELLIPSIS         = r'\.\.\.'

    # 整数常量
    t_ICONST = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

    # =======================================================================
    # 保留字映射表
    # =======================================================================
    
    reserved_map = {}
    for r in reserved:
        reserved_map[r.lower()] = r

    # =======================================================================
    # 构造函数和初始化
    # =======================================================================
    
    def __init__(self, comment, autobuild=1):
        """
        初始化词法分析器
        
        Args:
            comment: 注释映射字典，用于存储提取的注释
            autobuild: 是否自动构建lexer，默认为1
        """
        self.cm_map = comment
        self.keyword_map = {}
        if autobuild == 1:
            self.build(lextab="vlextab")

    def load_keyword_from_file(self, filename):
        """
        从文件加载自定义关键字列表
        
        文件格式:
            keyword = TYPE     # 设置后续关键字的默认类型
            keyword1           # 使用上次设置的类型
            keyword2 = INT     # 为单个关键字指定类型
            # 以#开头的行为注释
        
        Args:
            filename: 关键字文件路径（通常是Key.txt）
        """
        try:
            f = open(filename)
            last_key = 'AUTO'
            for line in f:
                if line[0] != '#':  # #打头则忽略
                    ws = line.split('=')
                    # 如果长度大于2，更新类型
                    if (len(ws) >= 2):
                        last_key = ws[1].strip().upper()
                    key = ws[0].strip()
                    if (key):
                        self.keyword_map[key] = last_key
        except:
            pass

    # =======================================================================
    # 复杂Token规则（函数形式）
    # =======================================================================
    
    def t_HCONST(self, t):
        r'((0x)|(0X))[0-9a-fA-F]+([uU]|[lL]|[uU][lL]|[lL][uU])?'
        """
        十六进制常量规则
        
        匹配0x或0X开头的十六进制数，统一转换为ICONST类型。
        """
        t.type = 'ICONST'
        return t

    # 浮点常量
    t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

    # =======================================================================
    # 换行和中文支持
    # =======================================================================
    
    def t_NEWLINE(self, t):
        r'\n+'
        """
        换行符规则
        
        匹配一个或多个换行，更新行号。
        """
        t.lexer.lineno += t.value.count("\n")

    def t_ZHCN(self, t):
        r'`.*?`'
        """
        中文标识符规则
        
        匹配反引号包围的文本，作为ID类型处理。
        用于支持中文变量名（特殊需求）。
        """
        t.type = "ID"
        t.value = t.value[1:-1]  # 去掉反引号
        return t

    def t_ID(self, t):
        r'[A-Za-z_][\w_.\[\]]*'
        """
        标识符规则
        
        处理各种标识符，包括：
        1. C保留字（映射到对应类型）
        2. 以_t/_T结尾的类型名（识别为INT）
        3. 自定义关键字（从Key.txt加载）
        4. 全大写标识符（识别为SCONST常量）
        5. 普通标识符
        """
        # 首先检查C保留字映射
        t.type = self.reserved_map.get(t.value, "ID")
        tup = t.value.upper()
        
        if (len(t.value) > 2
                and tup[-1] == 'T'     # 以_t/_T结尾
                and tup[-2] == '_'):
            # 类型标识符
            t.type = 'INT'
            return t
        elif (tup == 'CR'):
            # 忽略CR
            pass
        elif (tup == 'FAR'):
            # 忽略FAR（嵌入式常见）
            t.type = 'AUTO'
        elif (t.value in self.keyword_map):
            # 自定义关键字
            t.type = self.keyword_map[t.value]
            return t
        else:
            # 全大写识别为常量
            if t.value.isupper():
                t.type = 'SCONST'
            return t

    # =======================================================================
    # 注释处理规则
    # =======================================================================
    # 优先级：规则名长度决定匹配优先级，长规则优先
    
    def t_NEWCOMMENT(self, t):
        r'//.*?\n'
        """
        C++风格行注释规则
        
        匹配//开头的注释，只更新行号不存储。
        """
        t.lexer.lineno += 1

    def t_DEV_COMMENT_POST(self, t):
        r'/\*<(.|\n)*?\*/'
        """
        后缀开发人员注释规则
        
        匹配/*< ... */格式的注释，属于普通开发人员注释，
        不显示在流程图上，不存储到cm_map。
        """
        t.lexer.lineno += t.value.count('\n')
        # 不存储到 cm_map

    def t_FLOWCHART_COMMENT(self, t):
        r'/\*\*(?!\*)(.|\n)*?\*/'
        """
        流程图专属注释规则（核心功能）
        
        匹配/** ... */格式的注释（注意：第三个字符不是*），
        这是流程图专属注释，会被提取并绑定到下一行代码。
        
        提取逻辑:
            1. 去掉开头的/**和结尾的*/
            2. 去除首尾空白
            3. 存储到cm_map，键为当前行号+1（下一行）
        """
        t.lexer.lineno += t.value.count('\n')
        # 提取注释内容
        res = t.value.strip()
        if res.startswith('/**'):
            res = res[3:]
        elif res.startswith('/*'):
            res = res[2:]
        if res.endswith('*/'):
            res = res[:-2]
        res = res.strip()
        if res:
            # 绑定到下一行（注释通常在代码前）
            self.cm_map[t.lexer.lineno + 1] = res

    def t_comment(self, t):
        r'/\*(.|\n)*?\*/'
        """
        普通C注释规则
        
        匹配/* ... */格式的普通注释，只更新行号不存储。
        由于规则名长度较短，优先级低于FLOWCHART_COMMENT。
        """
        t.lexer.lineno += t.value.count('\n')

    # =======================================================================
    # 预处理器指令
    # =======================================================================
    
    def t_preprocessor(self, t):
        r'\#(.)*?\n'
        """
        预处理器指令规则
        
        匹配#开头的预处理器指令（如#include, #define），
        更新行号但不生成token。
        """
        t.lexer.lineno += 1
        
    # =======================================================================
    # 错误处理
    # =======================================================================
    
    def t_error(self, t):
        """
        错误处理
        
        打印非法字符信息并跳过。
        静默处理中文字符，避免干扰输出。
        """
        char = t.value[0]
        # 如果字符是中文（Unicode范围），静默跳过
        if ord(char) > 127:
            t.lexer.skip(1)
            return
        print(("vlex c illegal character %s @L%d" % (repr(char), t.lexer.lineno)))
        t.lexer.skip(1)

    # =======================================================================
    # 构建和测试方法
    # =======================================================================
    
    def build(self, **kwargs):
        """
        构建PLY词法分析器
        
        Args:
            **kwargs: 传递给lex.lex()的参数
        """
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        """
        测试方法
        
        Args:
            data: 输入字符串
        """
        self.lexer.input(data)
        while True:
             tok = lexer.token()
             if not tok:
                 break
             print(tok)
    

# =============================================================================
# 单元测试
# =============================================================================

if __name__ == "__main__":
    # 简单的单元测试
    cm = {}
    mylex = vlex(cm)
    lex.runmain(mylex.lexer)
    print(cm)
