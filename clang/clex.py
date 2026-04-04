#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# C语言词法分析器 (clex.py)
# -----------------------------------------------------------------------------
# 基于PLY的完整C语言词法分析器，支持ANSI C标准。
#
# 主要功能:
#     - 识别C语言全部关键字和运算符
#     - 处理各种字面量（整数、浮点、字符串、字符）
#     - 提取流程图专属注释（/** */ 格式）
#     - 支持从Key.txt加载自定义关键字
#     - 区分类型标识符（_t结尾、全大写）
#
# 注释处理策略（重要）:
#     - /** ... */   -> FLOWCHART_COMMENT，提取内容绑定到下一行
#     - /* ... */    -> DEV_COMMENT，忽略（开发人员注释）
#     - // ...       -> NEWCOMMENT，忽略
#
# 类层次:
#     clex - 主C词法分析器
#     vlex - 变体词法分析器（继承clex，用于特殊场景）
#
# 使用示例:
#     from clang.clex import clex
#     cm = {}  # 注释映射字典
#     lexer = clex(cm)
#     lexer.load_keyword_from_file('Key.txt')
#     lexer.lexer.input(c_code)
#     for tok in lexer.lexer:
#         print(tok)
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import sys
import ply.lex as lex


class clex:
    """
    C语言词法分析器主类
    
    使用PLY库构建，完整支持ANSI C的词法分析。
    特别处理流程图注释提取和自定义关键字。
    
    Attributes:
        reserved (tuple): C语言保留字
        tokens (tuple): 所有token类型
        cm_map (dict): 注释映射 {行号: 注释内容}
        keyword_map (dict): 自定义关键字映射
        lexer (Lexer): PLY词法分析器实例
    """
    
    # =======================================================================
    # C语言保留字 (ANSI C)
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
    # 按类别组织：注释、字面量、运算符、赋值、自增/减、结构、条件、分隔符
    
    tokens = reserved + (
        # 注释类型（当前版本注释token不返回，仅用于提取）
        # 'FLOWCHART_COMMENT',  # /** */ 流程图专属注释
        # 'DEV_COMMENT',        # /* */ 普通开发人员注释

        # 字面量
        'ID',       # 标识符
        'TYPEID',   # 类型标识符（全大写）
        'ICONST',   # 整数常量
        'HCONST',   # 十六进制常量
        'FCONST',   # 浮点常量
        'SCONST',   # 字符串常量
        'CCONST',   # 字符常量
        'ZHCN',     # 中文标识符

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
    # 空格、回车、制表符、换页符将被忽略
    
    t_ignore = ' \r\t\x0c'

    # =======================================================================
    # 简单Token规则（正则表达式）
    # =======================================================================
    # PLY使用t_前缀 + 大写token名定义规则
    
    # 运算符
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_OR = r'\|'
    t_AND = r'&'
    t_NOT = r'~'
    t_XOR = r'\^'
    t_LSHIFT = r'<<'
    t_RSHIFT = r'>>'
    t_LOR = r'\|\|'
    t_LAND = r'&&'
    t_LNOT = r'!'
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='

    # 赋值运算符
    t_EQUALS = r'='
    t_TIMESEQUAL = r'\*='
    t_DIVEQUAL = r'/='
    t_MODEQUAL = r'%='
    t_PLUSEQUAL = r'\+='
    t_MINUSEQUAL = r'-='
    t_LSHIFTEQUAL = r'<<='
    t_RSHIFTEQUAL = r'>>='
    t_ANDEQUAL = r'&='
    t_OREQUAL = r'\|='
    t_XOREQUAL = r'^='

    # 自增/减
    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'--'

    # 结构解引用
    t_ARROW = r'->'

    # 条件运算符
    t_CONDOP = r'\?'

    # 分隔符
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_PERIOD = r'\.'
    t_SEMI = r';'
    t_COLON = r':'
    t_ELLIPSIS = r'\.\.\.'

    # 整数常量（十进制，可选后缀u/U/l/L）
    t_ICONST = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

    # =======================================================================
    # 复杂Token规则（函数形式）
    # =======================================================================
    
    def t_HCONST(self, t):
        r'((0x)|(0X))[0-9a-fA-F]+([uU]|[lL]|[uU][lL]|[lL][uU])?'
        """
        十六进制常量规则
        
        匹配0x或0X开头的十六进制数，统一转换为ICONST类型处理。
        """
        t.type = 'ICONST'
        return t

    # 浮点常量
    t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

    def t_SCONST(self, t):
        r'"([^"\\\n]|\\.|[^"\\\n\x00-\x7F])*?"'
        """
        字符串常量规则
        
        匹配双引号包围的字符串，支持包含中文字符的字符串。
        """
        t.type = 'SCONST'
        t.value = t.value[1:-1]
        return t

    def t_CCONST(self, t):
        r"'([^'\\\n]|\\.|[^'\\\n\x00-\x7F])*?'"
        """
        字符常量规则
        
        匹配单引号包围的字符，支持中文字符。
        """
        t.type = 'CCONST'
        return t

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
            comment: 注释映射字典，用于存储提取的流程图注释
            autobuild: 是否自动构建lexer，默认为1
        """
        self.cm_map = comment
        self.keyword_map = {}
        if autobuild == 1:
            self.build(lextab="clextab")

    def load_keyword_from_file(self, filename):
        """
        从文件加载自定义关键字列表
        
        支持UTF-8编码（带BOM），文件格式：
            keyword = TYPE     # 设置后续关键字的默认类型
            keyword1           # 使用上次设置的类型
            # 以#开头的行为注释
        
        Args:
            filename: 关键字文件路径（Key.txt）
        """
        try:
            # 使用 UTF-8 编码打开文件（支持 BOM）
            with open(filename, 'r', encoding='utf-8-sig') as f:
                self.load_key_text(f.readlines())
        except Exception as e:
            print(f"[警告] 加载关键字文件失败: {e}")
            pass

    def load_key_text(self, lines):
        """
        从文本行加载关键字
        
        解析每行内容，更新keyword_map。
        
        Args:
            lines: 文本行列表
        """
        last_key = 'AUTO'
        for line in lines:
            # 去除 BOM 和空白字符
            line = line.strip()
            if not line or line.startswith('#'):  # 跳过空行和注释行
                continue
            ws = line.split('=')
            # 如果长度大于等于2，更新类型
            if (len(ws) >= 2):
                last_key = ws[1].strip().upper()
            key = ws[0].strip()
            if (key):
                self.keyword_map[key] = last_key

    # =======================================================================
    # 换行和特殊标识符
    # =======================================================================
    
    def t_NEWLINE(self, t):
        r'\n+'
        """
        换行符规则
        
        匹配一个或多个换行，更新行号计数。
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
        t.value = t.value[1:-1]
        return t

    def t_ID(self, t):
        r'[A-Za-z_][\w_]*'
        """
        标识符规则（核心逻辑）
        
        处理标识符识别，优先级：
        1. C保留字 -> 映射为对应类型
        2. _t/_T结尾 -> 识别为INT类型
        3. CR/FAR/STATIC/CONST -> 忽略（设为AUTO）
        4. 自定义关键字 -> 查找keyword_map
        5. 全大写且长度>1 -> TYPEID（如 UINT8）
        
        特殊处理：关键字后跟'('视为函数调用，保持为ID
        """
        t.type = self.reserved_map.get(t.value, "ID")
        if (len(t.value) > 2 and t.value[-1].lower() ==
                't'  # end with _t and _T will be recognized as TYPE
                and t.value[-2] == '_'):
            t.type = 'INT'
            return t
        elif (t.value.upper() == 'CR'):
            # 忽略CR
            pass
        elif (t.value.upper() in ('FAR', 'STATIC', 'CONST')):
            # if get a FAR, 忽略FAR
            t.type = 'AUTO'
        elif (t.value in self.keyword_map):
            # Check lookahead: if followed by '(', treat as function call (ID)
            # instead of keyword (AUTO)
            remaining = t.lexer.lexdata[t.lexer.lexpos:].lstrip()
            if remaining.startswith('('):
                # This looks like a function call, keep as ID
                pass
            else:
                t.type = self.keyword_map[t.value]
            return t
        elif (t.value.isupper() and len(t.value) > 1):
            # 全大写的标识符视为类型定义（如 UINT8, INT32 等）
            t.type = 'TYPEID'
            return t
        else:
            pass
            return t

    # =======================================================================
    # 注释处理规则
    # =======================================================================
    # PLY按函数名长度决定优先级，长函数名优先匹配
    
    def t_NEWCOMMENT(self, t):
        r'//.*?\n'
        """
        C++风格行注释
        
        匹配//开头的注释，更新行号但不存储。
        """
        t.lexer.lineno += 1

    def t_FLOWCHART_COMMENT(self, t):
        r'/\*\*(?!\*)(.|\n)*?\*/'
        """
        流程图专属注释规则（核心功能）
        
        匹配/** ... */格式的注释（第三个字符不是*）。
        这是唯一会被提取并显示在流程图上的注释类型。
        
        提取逻辑:
            1. 去掉开头的/**和结尾的*/
            2. 去除首尾空白
            3. 绑定到下一行代码（lineno + 1）
        """
        # bind it to next line 绑定到下一行
        # 新需求：只匹配 /** 开头且第三个字符不是*的注释（恰好两个星号）
        t.lexer.lineno += t.value.count('\n')
        # get comment content
        res = t.value.strip()
        if res.startswith('/**'):
            res = res[3:]
        elif res.startswith('/*'):
            res = res[2:]
        if res.endswith('*/'):
            res = res[:-2]
        res = res.strip()
        # 绑定到下一行
        if res:
            self.cm_map[t.lexer.lineno + 1] = res

    def t_DEV_COMMENT(self, t):
        r'/\*(?!\*)(.|\n)*?\*/'
        """
        普通开发人员注释
        
        匹配/* ... */格式的注释（不包括/**）。
        这些是普通开发注释，不显示在流程图上。
        """
        # 新需求：只有 /** */ 是流程图专属，其他注释不存储到cm_map
        # 匹配 /* 开头的注释（包括 /*** 等，但不包括 /** ）
        t.lexer.lineno += t.value.count('\n')
        # 不存储到 cm_map，因为这是开发人员注释

    def t_comment(self, t):
        r'/\*(.|\n)*?\*/'
        """
        通用注释规则（备用）
        
        由于函数名长度最短，优先级最低。
        作为其他注释规则的兜底匹配。
        """
        t.lexer.lineno += t.value.count('\n')

    # =======================================================================
    # 预处理器指令
    # =======================================================================
    
    def t_preprocessor(self, t):
        r'\#(.)*?\n'
        """
        预处理器指令
        
        匹配#开头的行（如#include, #define），
        更新行号但不生成token。
        """
        t.lexer.lineno += 1

    # =======================================================================
    # 错误处理
    # =======================================================================
    
    def t_error(self, t):
        """
        错误处理
        
        打印非法字符信息并跳过该字符。
        """
        print(("c illegal character %s @L%d" %
               (repr(t.value[0]), t.lexer.lineno)))
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
# 变体词法分析器（继承版本）
# =============================================================================

class vlex(clex):
    """
    变体C词法分析器
    
    继承clex，用于特殊场景（如全局变量分析）。
    简化了ID识别规则，支持点号(.)和下划线(_)开头的标识符。
    """

    def __init__(self, autobuild=1):
        """
        初始化变体词法分析器
        
        Args:
            autobuild: 是否自动构建
        """
        clex.__init__(self, {}, 0)
        self.keyword_map = {}
        if autobuild == 1:
            self.build(lextab="vlextab")

    def build(self, **kwargs):
        """构建PLY词法分析器"""
        self.lexer = lex.lex(module=self, **kwargs)

    def t_ID2(self, t):
        r'[A-Za-z_][\w_.]*'
        """
        变体标识符规则
        
        支持点号(.)在标识符中，用于结构体成员访问。
        简化的识别逻辑：保留字 -> _t类型 -> 关键字映射。
        """
        t.type = self.reserved_map.get(t.value, "ID")
        if (len(t.value) > 2 and t.value[-1].lower() ==
                't'  # end with _t and _T will be recognized as TYPE
                and t.value[-2] == '_'):
            t.type = 'INT'
            return t
        elif (t.value.upper() == 'CR'):
            # 忽略CR
            pass
        elif (t.value.upper() == 'FAR'):
            # if get a FAR, 忽略FAR
            t.type = 'AUTO'
        elif (t.value in self.keyword_map):
            t.type = self.keyword_map[t.value]
            return t
        else:
            pass
            return t

    # t_ID = t_ID2


# =============================================================================
# 单元测试
# =============================================================================

if __name__ == "__main__":
    # a simple unit test
    cm = {}
    mylex = clex(cm)
    #mylex = vlex()
    #mylex.build(lextab="clextab")
    lex.runmain(mylex.lexer)
    print(cm)
