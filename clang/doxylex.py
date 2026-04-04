#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Doxygen注释词法分析器 (doxylex.py)
# -----------------------------------------------------------------------------
# 用于解析Doxygen风格的注释，提取@标签和描述文本。
#
# 支持的标签:
#     @author, @file, @date, @brief, @param, @return, @depth, @detail, @details
#     @gvarin, @gvarout, @alias, @ignore
#
# Token类型:
#     KEY       - @开头的标签 (如 @brief)
#     WORD      - 普通单词/描述文本
#     NEWLINE   - 换行符
#     STAR      - 星号 (*)
#     BLANKLINE - 空白行 (*\n)
#
# 使用示例:
#     from clang.doxylex import doxylex
#     mylex = doxylex()
#     mylex.lexer.input("@brief 这是描述\\n")
#     for tok in mylex.lexer: print(tok)
#
# 依赖: PLY (Python Lex-Yacc)
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

from ply import lex


class doxylex:
    """
    Doxygen注释词法分析器类
    
    使用PLY库构建，识别Doxygen风格的注释标签和文本。
    
    Attributes:
        reserved (tuple): 保留字列表，Doxygen标准标签
        tokens (tuple): 所有token类型列表
        reserved_map (dict): 保留字到token类型的映射
        lexer (Lexer): PLY词法分析器实例
    """
    
    # =======================================================================
    # 保留字定义
    # =======================================================================
    # Doxygen标准标签，用于文档生成
    
    reserved = (
        'AUTHOR', 'FILE', 'DATE',           # 文件信息标签
        'BRIEF', 'PARAM', 'RETURN',         # 函数说明标签
        'DEPTH', 'DETAIL', 'DETAILS',       # 流程图控制标签
        'GVARIN', 'GVAROUT',                # 全局变量标签
        'ALIAS', 'IGNORE',                  # 其他标签
    )

    # =======================================================================
    # Token类型定义
    # =======================================================================
    
    tokens = reserved + (
        'KEY',          # @开头的标签关键字
        'WORD',         # 普通单词/描述文本
        'NEWLINE',      # 换行符
        'STAR',         # 星号（未使用）
        'BLANKLINE'     # 空白注释行 (*\n)
    )
    
    # =======================================================================
    # 忽略字符
    # =======================================================================
    # 空格、制表符、换页符将被忽略
    
    t_ignore = ' \t\x0c'

    # =======================================================================
    # 保留字映射表
    # =======================================================================
    # 将小写标签名映射到大写的token类型
    
    reserved_map = {}
    for r in reserved:
        reserved_map[r.lower()] = r

    # =======================================================================
    # 构造函数
    # =======================================================================
    
    def __init__(self, autobuild=1):
        """
        初始化词法分析器
        
        Args:
            autobuild: 是否自动构建lexer，默认为1（自动构建）
        """
        if autobuild == 1:
            self.build(lextab="doxytab")

    def build(self, **kwargs):
        """
        构建PLY词法分析器
        
        Args:
            **kwargs: 传递给lex.lex()的参数
        """
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        """
        测试方法：输入数据并打印所有token
        
        Args:
            data: 输入字符串
        """
        self.lexer.input(data)
        while True:
             tok = lexer.token()
             if not tok:
                 break
             print(tok)

    # =======================================================================
    # Token规则定义
    # =======================================================================
    # PLY使用t_前缀识别token规则
    
    def t_NEWLINE(self, t):
        r'(\n|\r)+'
        """
        换行符规则
        
        匹配一个或多个换行符，更新行号计数器。
        """
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_KEY(self, t):
        r'@[A-Za-z_][\w_]*'
        """
        Doxygen标签规则
        
        匹配@开头的标识符，查找保留字映射表确定类型。
        如果是保留字，使用对应的大写类型；否则保持KEY类型。
        """
        # 保留@符号，完整匹配保留字映射
        t.type = self.reserved_map.get(t.value, "KEY")
        return t

    # 空白注释行规则：星号后跟可选空格和换行
    t_BLANKLINE = r'\*\s*\n'

    # 单词规则：从非星号、非空格字符开始到行尾
    # 用于匹配描述文本
    t_WORD = r'[^*\s].*'

    # =======================================================================
    # 错误处理
    # =======================================================================
    
    def t_error(self, t):
        """
        错误处理：遇到非法字符
        
        打印错误信息并跳过该字符。
        星号字符通常属于注释格式，不报错。
        """
        if (t.value[0] != '*'):
            print(("doxy illegal chr %s" % repr(t.value[0])))
        t.lexer.skip(1)


# =============================================================================
# 单元测试
# =============================================================================

if __name__ == "__main__":
    # 简单的单元测试
    cm = {}
    mylex = doxylex()
    lex.runmain(mylex.lexer)
    print(cm)
