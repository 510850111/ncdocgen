"""
clang 包 - C语言解析模块
========================
提供C语言的词法分析和语法分析功能。

子模块:
    clex        - C语言词法分析器，识别关键字、标识符、注释等
    cyacc       - C语言语法分析器，构建抽象语法树(AST)
    doxylex     - Doxygen注释词法分析器
    doxyyacc    - Doxygen注释语法分析器
    cglobal     - 全局常量和工具函数

使用示例:
    from clang.clex import clex
    from clang.cyacc import cyacc
    
    # 创建词法分析器
    comment_map = {}
    lexer = clex(comment_map)
    
    # 创建语法分析器
    parser = cyacc(lexer, fun_handler)
    
    # 解析代码
    result = parser.parse(data)

作者: ncdocgen团队
"""

import sys

# 添加父目录到路径，支持从子目录直接运行模块
if sys.path[-1] != '..':
    sys.path.append('..')
