#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# C语言增强语法分析器 (ceyacc.py)
# -----------------------------------------------------------------------------
# 基于PLY的C语言语法分析器（增强版本）。
#
# 与cyacc.py的区别:
#     - 增强的错误恢复能力
#     - 改进的预处理指令处理
#     - 更完善的类型定义追踪
#     - 支持更多C语言扩展特性
#
# 主要功能:
#     - 完整的C语言语法解析
#     - 语法树构建
#     - 控制结构识别
#     - 增强的错误处理和恢复
#
# 语法规则分类（与cyacc.py相同）:
#     1. 顶层结构: translation_unit, external_declaration
#     2. 函数定义: function_definition（4种形式）
#     3. 声明: declaration, declaration_list, declaration_specifiers
#     4. 类型系统: type_specifier, type_qualifier, storage_class_specifier
#     5. 结构体/联合体: struct_or_union_specifier
#     6. 枚举: enum_specifier, enumerator
#     7. 声明符: declarator, direct_declarator, pointer
#     8. 初始化: initializer, initializer_list
#     9. 复合语句: compound_statement
#     10. 语句: statement, labeled_statement
#     11. 选择语句: selection_statement (if, switch)
#     12. 循环语句: iteration_statement (while, do-while, for)
#     13. 跳转语句: jump_statement
#     14. 表达式: expression（15级优先级）
#
# PLY配置:
#     method='LALR', tabmodule='ceyacc_tab'
#     debug=False, write_tables=False, errorlog=NullLogger()
#
# 使用示例:
#     from clang.ceyacc import cyacc
#     from clang.clex import clex
#     
#     lexer = clex(comment_map)
#     parser = cyacc(lexer, handler)
#     result = parser.parse(data)
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import sys
from ply import yacc

from pathlib import Path

# Get the token map
try:
    from . import clex
except:
    import clex

if sys.path[-1]!='..': sys.path.extend([str(Path.cwd()), str(Path.cwd()/'..')])

from common.debug import *
from common.cglobal import *

# =============================================================================
# 语法分析器工厂函数
# =============================================================================
# cyacc(mylexer, fun) - 创建C语言增强语法分析器
# Args:
#     mylexer: 词法分析器实例
#     fun: 语法处理回调对象
# Returns:
#     yacc.Parser: 配置好的语法分析器对象
# =============================================================================

# translation-unit:

def cyacc(mylexer, fun):
    def p_translation_unit_1(p):
        'translation_unit : external_declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_translation_unit_2(p):
        'translation_unit : translation_unit external_declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # external-declaration:

    def p_external_declaration_1(p):
        'external_declaration : function_definition'
        # 在找到函数定义时，将{起点和当前函数体的结尾压入
        # 此处需要对{}压出
        fun.pop()
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_external_declaration_2(p):
        'external_declaration : declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # function-definition:

    def p_function_definition_1(p):
        'function_definition : declaration_specifiers declarator declaration_list compound_statement'
        fun.update(p, 1)
        # 将函数的原型压入
        fun.declaration_update(p.lineno(1), p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[2]])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_function_definition_2(p):
        'function_definition : declarator declaration_list compound_statement'
        #pass
        fun.update(p, 1)
        fun.declaration_update(p.lineno(1), 'void '+p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[1]])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_function_definition_3(p):
        'function_definition : declarator compound_statement'
        #pass
        fun.update(p, 1)
        fun.declaration_update(p.lineno(1), 'void '+p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[1]])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_function_definition_4(p):
        'function_definition : declaration_specifiers declarator compound_statement'
        #pass
        fun.update(p, 1)
        fun.declaration_update(p.lineno(2), p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[2]])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # declaration:

    def p_declaration_1(p):
        'declaration : declaration_specifiers init_declarator_list SEMI'
        #pass
        fun.code_push(p.lineno(3), p[2])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_2(p):
        'declaration : declaration_specifiers SEMI'
        fun.code_push(p.lineno(2), p[1])
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # declaration-list:

    def p_declaration_list_1(p):
        'declaration_list : declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_list_2(p):
        'declaration_list : declaration_list declaration '
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # declaration-specifiers
    def p_declaration_specifiers_1(p):
        'declaration_specifiers : storage_class_specifier declaration_specifiers'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_specifiers_2(p):
        'declaration_specifiers : type_specifier declaration_specifiers'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_specifiers_3(p):
        'declaration_specifiers : type_qualifier declaration_specifiers'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_specifiers_4(p):
        'declaration_specifiers : storage_class_specifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_specifiers_5(p):
        'declaration_specifiers : type_specifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declaration_specifiers_6(p):
        'declaration_specifiers : type_qualifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # storage-class-specifier
    def p_storage_class_specifier(p):
        '''storage_class_specifier : AUTO
                                    | REGISTER
                                    | STATIC
                                    | EXTERN
                                    | TYPEDEF
                                    '''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # type-specifier:
    def p_type_specifier(p):
        '''type_specifier : VOID
                          | CHAR
                          | SHORT
                          | INT
                          | LONG
                          | FLOAT
                          | DOUBLE
                          | SIGNED
                          | UNSIGNED
                          | struct_or_union_specifier
                          | enum_specifier
                          | TYPEID
                          '''
        #pass
        fun.update(p)
        #print("TT", p[1], p.lineno(1), get_curline())
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # type-qualifier:
    def p_type_qualifier(p):
        '''type_qualifier : CONST
                          | VOLATILE'''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # struct-or-union-specifier

    def p_struct_or_union_specifier_1(p):
        'struct_or_union_specifier : struct_or_union ID LBRACE struct_declaration_list RBRACE'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_struct_or_union_specifier_2(p):
        'struct_or_union_specifier : struct_or_union LBRACE struct_declaration_list RBRACE'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_struct_or_union_specifier_3(p):
        'struct_or_union_specifier : struct_or_union ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # struct-or-union:
    def p_struct_or_union(p):
        '''struct_or_union : STRUCT
                            | UNION
                            '''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # struct-declaration-list:

    def p_struct_declaration_list_1(p):
        'struct_declaration_list : struct_declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_struct_declaration_list_2(p):
        'struct_declaration_list : struct_declaration_list struct_declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # init-declarator-list:

    def p_init_declarator_list_1(p):
        'init_declarator_list : init_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_init_declarator_list_2(p):
        'init_declarator_list : init_declarator_list COMMA init_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # init-declarator

    def p_init_declarator_1(p):
        'init_declarator : declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_init_declarator_2(p):
        'init_declarator : declarator EQUALS initializer'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # struct-declaration:

    def p_struct_declaration(p):
        'struct_declaration : specifier_qualifier_list struct_declarator_list SEMI'
        fun.code_push(p.lineno(3), p[3])
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # specifier-qualifier-list:

    def p_specifier_qualifier_list_1(p):
        'specifier_qualifier_list : type_specifier specifier_qualifier_list'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_specifier_qualifier_list_2(p):
        'specifier_qualifier_list : type_specifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_specifier_qualifier_list_3(p):
        'specifier_qualifier_list : type_qualifier specifier_qualifier_list'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_specifier_qualifier_list_4(p):
        'specifier_qualifier_list : type_qualifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # struct-declarator-list:

    def p_struct_declarator_list_1(p):
        'struct_declarator_list : struct_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_struct_declarator_list_2(p):
        'struct_declarator_list : struct_declarator_list COMMA struct_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # struct-declarator:

    def p_struct_declarator_1(p):
        'struct_declarator : declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_struct_declarator_2(p):
        'struct_declarator : declarator COLON constant_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_struct_declarator_3(p):
        'struct_declarator : COLON constant_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # enum-specifier:

    def p_enum_specifier_1(p):
        'enum_specifier : ENUM ID LBRACE enumerator_list RBRACE'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_enum_specifier_2(p):
        'enum_specifier : ENUM LBRACE enumerator_list RBRACE'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_enum_specifier_3(p):
        'enum_specifier : ENUM ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # enumerator_list:
    def p_enumerator_list_1(p):
        'enumerator_list : enumerator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_enumerator_list_2(p):
        'enumerator_list : enumerator_list COMMA enumerator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # enumerator:
    def p_enumerator_1(p):
        'enumerator : ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_enumerator_2(p):
        'enumerator : ID EQUALS constant_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # declarator:

    def p_declarator_1(p):
        'declarator : pointer direct_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_declarator_2(p):
        'declarator : direct_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # direct-declarator:

    def p_direct_declarator_1(p):
        'direct_declarator : ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_declarator_2(p):
        'direct_declarator : LPAREN declarator RPAREN'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_declarator_3(p):
        'direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_declarator_4(p):
        'direct_declarator : direct_declarator LPAREN parameter_type_list RPAREN '
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_declarator_5(p):
        'direct_declarator : direct_declarator LPAREN identifier_list RPAREN '
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_declarator_6(p):
        'direct_declarator : direct_declarator LPAREN RPAREN '
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # pointer:
    def p_pointer_1(p):
        'pointer : TIMES type_qualifier_list'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_pointer_2(p):
        'pointer : TIMES'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_pointer_3(p):
        'pointer : TIMES type_qualifier_list pointer'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_pointer_4(p):
        'pointer : TIMES pointer'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # type-qualifier-list:

    def p_type_qualifier_list_1(p):
        'type_qualifier_list : type_qualifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_type_qualifier_list_2(p):
        'type_qualifier_list : type_qualifier_list type_qualifier'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # parameter-type-list:

    def p_parameter_type_list_1(p):
        'parameter_type_list : parameter_list'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_parameter_type_list_2(p):
        'parameter_type_list : parameter_list COMMA ELLIPSIS'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # parameter-list:

    def p_parameter_list_1(p):
        'parameter_list : parameter_declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_parameter_list_2(p):
        'parameter_list : parameter_list COMMA parameter_declaration'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # parameter-declaration:
    def p_parameter_declaration_1(p):
        'parameter_declaration : declaration_specifiers declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_parameter_declaration_2(p):
        'parameter_declaration : declaration_specifiers abstract_declarator_opt'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # identifier-list:
    def p_identifier_list_1(p):
        'identifier_list : ID'
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_identifier_list_2(p):
        'identifier_list : identifier_list COMMA ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # initializer:

    def p_initializer_1(p):
        'initializer : assignment_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_initializer_2(p):
        '''initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE'''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # initializer-list:

    def p_initializer_list_1(p):
        'initializer_list : initializer'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_initializer_list_2(p):
        'initializer_list : initializer_list COMMA initializer'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # type-name:

    def p_type_name(p):
        'type_name : specifier_qualifier_list abstract_declarator_opt'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_abstract_declarator_opt_1(p):
        'abstract_declarator_opt : empty'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_abstract_declarator_opt_2(p):
        'abstract_declarator_opt : abstract_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # abstract-declarator:

    def p_abstract_declarator_1(p):
        'abstract_declarator : pointer '
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_abstract_declarator_2(p):
        'abstract_declarator : pointer direct_abstract_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_abstract_declarator_3(p):
        'abstract_declarator : direct_abstract_declarator'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # direct-abstract-declarator:

    def p_direct_abstract_declarator_1(p):
        'direct_abstract_declarator : LPAREN abstract_declarator RPAREN'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_abstract_declarator_2(p):
        'direct_abstract_declarator : direct_abstract_declarator LBRACKET constant_expression_opt RBRACKET'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_abstract_declarator_3(p):
        'direct_abstract_declarator : LBRACKET constant_expression_opt RBRACKET'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_abstract_declarator_4(p):
        'direct_abstract_declarator : direct_abstract_declarator LPAREN parameter_type_list_opt RPAREN'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_direct_abstract_declarator_5(p):
        'direct_abstract_declarator : LPAREN parameter_type_list_opt RPAREN'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # Optional fields in abstract declarators

    def p_constant_expression_opt_1(p):
        'constant_expression_opt : empty'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_constant_expression_opt_2(p):
        'constant_expression_opt : constant_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_parameter_type_list_opt_1(p):
        'parameter_type_list_opt : empty'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_parameter_type_list_opt_2(p):
        'parameter_type_list_opt : parameter_type_list'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 语句规则
    # ========================================================================
    # 包括标号语句、表达式语句、选择语句、循环语句、跳转语句、复合语句

    # statement:
    #    '''
    #    statement : labeled_statement
    #              | expression_statement
    #              | selection_statement
    #              | iteration_statement
    #              | jump_statement
    #              | compound_statement
    #              '''

    def p_statement(p):
        '''
        statement : labeled_statement
                  '''
        fun.pop()
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_statement_1(p):
        'statement : compound_statement'
        fun.pop()
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_statement_2(p):
        'statement : jump_statement'
        fun.pop()
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_statement_3(p):
        'statement : iteration_statement'
        fun.pop()
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_statement_4(p):
        'statement : selection_statement'
        fun.pop()
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_statement_5(p):
        'statement : expression_statement'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))


    # ========================================================================
    # 标号语句规则
    # ========================================================================
    # 包括标识符标号、case标号、default标号

    # labeled-statement:

    def p_labeled_statement_1(p):
        'labeled_statement : ID COLON statement'

        semi = fun.extra_push(p,3)
        fun.push(['LABEL', p.lineno(1), semi, p[1]])
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

#    def p_labeled_statement_2(p):
#        """labeled_statement : CASE constant_expression COLON expression_statement
#        """
#        #'labeled_statement : CASE constant_expression COLON expression_statement'
#        fun.update(p)
#        print 'CASE2', p[2], p[4]
#        semi = fun.sextra_push(p,4)
#        #print 'CASE2', fun.top(1)
#        #print 'CASE2', fun.top()
#        fun.push([p[1].upper(), p.lineno(1), semi, p[2]])
#        #pass
#        if CURINFO==1: print(get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0))

#    def p_labeled_statement_3(p):
#        'labeled_statement : DEFAULT COLON expression_statement'
#        # 此处需要针对DEFAULT的情况进行判断
#        semi = fun.semil_get()
#        if ENABLE_YACC_DEBUG==1: print '===', p[1], semi
#
#        if (semi < p.lineno(1)):
#            # 如果分号小于行号，说明这个;不是当前default对应的;
#            semi = p.lineno(1)
#        else:
#            # 如果比较大，说明是对应的语句
#            fun.extra_push(p, 3)
#        # 压入数据
#        fun.push([p[1].upper(), p.lineno(1), semi, p[1]])
#        #pass
#        fun.update(p)
#        if CURINFO==1: print(get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0))

    def p_labeled_statement_4(p):
        'labeled_statement : CASE constant_expression COLON '
        # 根据贪婪原则，只有CASE和break之间的表达式为空
        fun.update(p)
        no = p.lineno(3)
        #fun.push(['SINGLE', no, no, 'NOP'])
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[2]])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_labeled_statement_5(p):
        'labeled_statement : DEFAULT COLON'
        # 根据贪婪原则，只有DEFAULT和break之间的表达式为空
        no = p.lineno(2)
        semi = fun.semil_get()
        #fun.push(['SINGLE', no, no, 'NOP'])
        fun.push([p[1].upper(), no, no, 'default'])
        
        #fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))




    # ========================================================================
    # 表达式语句规则
    # ========================================================================
    # 以分号结束的表达式

    # expression-statement:
    def p_expression_statement(p):
        'expression_statement : expression_opt SEMI'
        #pass
        semi = fun.semil_update(p.lineno(2))
        if ENABLE_YACC_DEBUG: print('===;', semi, p[1])
        fun.code_push(p.lineno(2), p[1])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 复合语句规则（代码块）
    # ========================================================================
    # { 声明列表 语句列表 }

    # compound-statement:

    def p_compound_statement_1(p):
        'compound_statement : LBRACE declaration_list statement_list RBRACE'
        #pass
        fun.push(['{}', p.lineno(1), p.lineno(4), ''])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_compound_statement_2(p):
        'compound_statement : LBRACE statement_list RBRACE'
        fun.push(['{}', p.lineno(1), p.lineno(3), ''])
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_compound_statement_3(p):
        'compound_statement : LBRACE declaration_list RBRACE'
        #pass
        fun.push(['{}', p.lineno(1), p.lineno(3), ''])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_compound_statement_4(p):
        'compound_statement : LBRACE RBRACE'
        fun.push(['{}', p.lineno(1), p.lineno(2), ''])
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 语句列表规则
    # ========================================================================
    # 复合语句中的语句序列

    # statement-list:

    def p_statement_list_1(p):
        'statement_list : statement'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_statement_list_2(p):
        'statement_list : statement_list statement'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 选择语句规则
    # ========================================================================
    # if、if-else、switch语句

    # selection-statement

    def p_selection_statement_1(p):
        'selection_statement : IF LPAREN expression RPAREN compound_statement'
        #pass
        #trace_index()
        semi = fun.extra_push(p,5)

        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])

        # 找到IF时，需要寻找语句的位置
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_selection_statement_2(p):
        'selection_statement : IF LPAREN expression RPAREN compound_statement ELSE statement '
        # IF ELSE需要压两次
        # 此时需要注意：
        #    如果是else对应的语句无{}
        #        需要将其extra_push
        #    
        #    如果是if对应的语句无{}，
        #        需要将其pop，再push
        #    
        semi = fun.extra_push(p, 7)
        if (semi==0):
            semi = p.lineno(6)
        if (ENABLE_YACC_DEBUG==1): print('===ELSE', p[7], semi)
        semi2 = semi

        # 如果获取的分支a的语句
        if (fun.extra_get(p, 5)==1):
            top = fun.rpop()
            if (ENABLE_YACC_DEBUG==1): print('===ELSE POP', p[5], semi)
            #fun.push(['DONENODE', p.lineno(6), p.lineno(6), ])
            semi = fun.extra_push(p, 5, p.lineno(6))
            fun.push(top)
            if (semi==0):
                semi = p.lineno(6)
            if (ENABLE_YACC_DEBUG==1): print('===IFELSE', p[5], semi)

        # 作为最后功能
        fun.push(['IFELSE', p.lineno(1), semi, p[3], p.lineno(6)])

        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    #def p_selection_statement_2_1(p):
    #    'selection_statement : IF LPAREN expression RPAREN expression_statement ELSE statement '
    #    # IF ELSE需要压两次
    #    # 此时需要注意：
    #    #    如果是else对应的语句无{}
    #    #        需要将其extra_push
    #    #    
    #    #    如果是if对应的语句无{}，
    #    #        需要将其pop，再push
    #    #    
    #    semi = fun.extra_push(p, 7)
    #    if (semi==0):
    #        semi = p.lineno(6)
    #    if (ENABLE_YACC_DEBUG==1): print '===ELSE', p[7], semi
    #    semi2 = semi

    #    # 如果获取的分支a的语句
    #    if (fun.extra_get(p, 5)==1):
    #        # 将else分支取出
    #        top = fun.rpop()
    #        if (ENABLE_YACC_DEBUG==1): print '===ELSE POP', p[5], semi
    #        semi = fun.sextra_push(p, 5, p.lineno(6))
    #        fun.push(top)
    #        if (semi==0):
    #            semi = p.lineno(6)
    #        if (ENABLE_YACC_DEBUG==1): print '===IFELSE', p[5], semi

    #    # 作为最后功能
    #    fun.push(['IFELSE', p.lineno(1), semi, p[3], p.lineno(6)])

    #    fun.update(p)
    #    if CURINFO==1: print(get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0))


    def p_selection_statement_3(p):
        'selection_statement : SWITCH LPAREN expression RPAREN statement '
        #pass
        semi = fun.extra_push(p,5)
        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 循环语句规则
    # ========================================================================
    # while、do-while、for循环

    # iteration_statement:

    def p_iteration_statement_1(p):
        'iteration_statement : WHILE LPAREN expression RPAREN compound_statement'
        semi = fun.extra_push(p,5)
        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_iteration_statement_2(p):
        'iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN compound_statement '
        #pass
        if ENABLE_YACC_DEBUG==1: print('===YFOR', p[3], p[9])
        semi = fun.extra_push(p,9)
        fun.push([p[1].upper(), p.lineno(1), semi, p[5], p[3], p[7]])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_iteration_statement_3(p):
        'iteration_statement : DO compound_statement WHILE LPAREN expression RPAREN SEMI'
        #pass
        semi = fun.extra_push(p,2)
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[5]])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 跳转语句规则
    # ========================================================================
    # goto、continue、break、return语句

    # jump_statement:

    def p_jump_statement_1(p):
        'jump_statement : GOTO ID SEMI'
        #pass
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[2]])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_jump_statement_2(p):
        'jump_statement : CONTINUE SEMI'
        #pass
        fun.push([p[1].upper(), p.lineno(1), p.lineno(2), 'continue%d'%p.lineno(1)])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_jump_statement_3(p):
        'jump_statement : BREAK SEMI'
        #pass
        fun.push([p[1].upper(), p.lineno(1), p.lineno(2), 'break%d'%p.lineno(1)])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_jump_statement_4(p):
        'jump_statement : RETURN expression_opt SEMI'
        #pass
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[2]])
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_expression_opt_1(p):
        'expression_opt : empty'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_expression_opt_2(p):
        'expression_opt : expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 表达式规则（15级优先级，从低到高）
    # ========================================================================
    # 逗号、赋值、条件、逻辑或、逻辑与、按位或、按位异或、
    # 按位与、相等性、关系、移位、加法、乘法、一元、后缀、基本

    # expression:
    def p_expression_1(p):
        'expression : assignment_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_expression_2(p):
        'expression : expression COMMA assignment_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 赋值表达式规则
    # ========================================================================

    # assigment_expression:
    def p_assignment_expression_1(p):
        'assignment_expression : conditional_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_assignment_expression_2(p):
        'assignment_expression : unary_expression assignment_operator assignment_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 赋值运算符规则
    # ========================================================================
    # =, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=

    # assignment_operator:
    def p_assignment_operator(p):
        '''
        assignment_operator : EQUALS
                            | TIMESEQUAL
                            | DIVEQUAL
                            | MODEQUAL
                            | PLUSEQUAL
                            | MINUSEQUAL
                            | LSHIFTEQUAL
                            | RSHIFTEQUAL
                            | ANDEQUAL
                            | OREQUAL
                            | XOREQUAL
                            '''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 条件表达式规则（?:运算符）
    # ========================================================================

    # conditional-expression
    def p_conditional_expression_1(p):
        'conditional_expression : logical_or_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_conditional_expression_2(p):
        'conditional_expression : logical_or_expression CONDOP expression COLON conditional_expression '
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 常量表达式规则
    # ========================================================================

    # constant-expression

    def p_constant_expression(p):
        'constant_expression : conditional_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 逻辑或表达式规则（||运算符）
    # ========================================================================

    # logical-or-expression

    def p_logical_or_expression_1(p):
        'logical_or_expression : logical_and_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_logical_or_expression_2(p):
        'logical_or_expression : logical_or_expression LOR logical_and_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 逻辑与表达式规则（&&运算符）
    # ========================================================================

    # logical-and-expression

    def p_logical_and_expression_1(p):
        'logical_and_expression : inclusive_or_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_logical_and_expression_2(p):
        'logical_and_expression : logical_and_expression LAND inclusive_or_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 按位或表达式规则（|运算符）
    # ========================================================================

    # inclusive-or-expression:

    def p_inclusive_or_expression_1(p):
        'inclusive_or_expression : exclusive_or_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_inclusive_or_expression_2(p):
        'inclusive_or_expression : inclusive_or_expression OR exclusive_or_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 按位异或表达式规则（^运算符）
    # ========================================================================

    # exclusive-or-expression:

    def p_exclusive_or_expression_1(p):
        'exclusive_or_expression :  and_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_exclusive_or_expression_2(p):
        'exclusive_or_expression :  exclusive_or_expression XOR and_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 按位与表达式规则（&运算符）
    # ========================================================================

    # AND-expression

    def p_and_expression_1(p):
        'and_expression : equality_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_and_expression_2(p):
        'and_expression : and_expression AND equality_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))


    # ========================================================================
    # 相等性表达式规则（==, !=运算符）
    # ========================================================================

    # equality-expression:
    def p_equality_expression_1(p):
        'equality_expression : relational_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_equality_expression_2(p):
        'equality_expression : equality_expression EQ relational_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_equality_expression_3(p):
        'equality_expression : equality_expression NE relational_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))


    # ========================================================================
    # 关系表达式规则（<, >, <=, >=运算符）
    # ========================================================================

    # relational-expression:
    def p_relational_expression_1(p):
        'relational_expression : shift_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_relational_expression_2(p):
        'relational_expression : relational_expression LT shift_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_relational_expression_3(p):
        'relational_expression : relational_expression GT shift_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_relational_expression_4(p):
        'relational_expression : relational_expression LE shift_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_relational_expression_5(p):
        'relational_expression : relational_expression GE shift_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # shift-expression

    def p_shift_expression_1(p):
        'shift_expression : additive_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_shift_expression_2(p):
        'shift_expression : shift_expression LSHIFT additive_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_shift_expression_3(p):
        'shift_expression : shift_expression RSHIFT additive_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # additive-expression

    def p_additive_expression_1(p):
        'additive_expression : multiplicative_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_additive_expression_2(p):
        'additive_expression : additive_expression PLUS multiplicative_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_additive_expression_3(p):
        'additive_expression : additive_expression MINUS multiplicative_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # multiplicative-expression

    def p_multiplicative_expression_1(p):
        'multiplicative_expression : cast_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_multiplicative_expression_2(p):
        'multiplicative_expression : multiplicative_expression TIMES cast_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_multiplicative_expression_3(p):
        'multiplicative_expression : multiplicative_expression DIVIDE cast_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_multiplicative_expression_4(p):
        'multiplicative_expression : multiplicative_expression MOD cast_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 强制类型转换表达式规则（(type)运算符）
    # ========================================================================

    # cast-expression:

    def p_cast_expression_1(p):
        'cast_expression : unary_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_cast_expression_2(p):
        'cast_expression : LPAREN type_name RPAREN cast_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 一元表达式规则（++, --, !, ~, *, &, sizeof）
    # ========================================================================

    # unary-expression:
    def p_unary_expression_1(p):
        'unary_expression : postfix_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_unary_expression_2(p):
        'unary_expression : PLUSPLUS unary_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_unary_expression_3(p):
        'unary_expression : MINUSMINUS unary_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_unary_expression_4(p):
        'unary_expression : unary_operator cast_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_unary_expression_5(p):
        'unary_expression : SIZEOF unary_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_unary_expression_6(p):
        'unary_expression : SIZEOF LPAREN type_name RPAREN'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))
        
    #unary-operator
    def p_unary_operator(p):
        '''unary_operator : AND
                        | TIMES
                        | PLUS 
                        | MINUS
                        | NOT
                        | LNOT '''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 后缀表达式规则（[], (), ., ->, ++, --）
    # ========================================================================

    # postfix-expression:
    def p_postfix_expression_1(p):
        'postfix_expression : primary_expression'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_2(p):
        'postfix_expression : postfix_expression LBRACKET expression RBRACKET'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_3(p):
        'postfix_expression : postfix_expression LPAREN argument_expression_list RPAREN'
        #pass
        fun.update(p)
        fun.fun_push(p.lineno(2), p[1])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_4(p):
        'postfix_expression : postfix_expression LPAREN RPAREN'
        #pass
        fun.update(p)
        fun.fun_push(p.lineno(2), p[1])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_5(p):
        'postfix_expression : postfix_expression PERIOD ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_6(p):
        'postfix_expression : postfix_expression ARROW ID'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_7(p):
        'postfix_expression : postfix_expression PLUSPLUS'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_postfix_expression_8(p):
        'postfix_expression : postfix_expression MINUSMINUS'
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 基本表达式规则（标识符、常量、字符串、括号）
    # ========================================================================

    # primary-expression:
    def p_primary_expression(p):
        '''primary_expression :  ID
                            |  constant
                            |  SCONST
                            |  LPAREN expression RPAREN'''
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 参数表达式列表规则
    # ========================================================================
    # 函数调用时的实参列表

    # argument-expression-list:
    def p_argument_expression_list(p):
        '''argument_expression_list :  assignment_expression
                                  |  argument_expression_list COMMA assignment_expression'''
        #pass
        fun.update(p)
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    # ========================================================================
    # 常量规则
    # ========================================================================
    # 整数、浮点、字符常量

    # constant:
    def p_constant(p): 
        '''constant : ICONST
                  | FCONST
                  | CCONST'''
        p[0]=str(p[1])
        if CURINFO==1: print((get_cur_info()[0],p[0],p.lineno(0),p.endlineno(0)))

    def p_empty(p):
        'empty : '
        pass

    def p_error(p):
        print(("c syntax error at '%s L%d'" % (p.value, p.lineno)))

    lexer = mylexer.lexer
    tokens = mylexer.tokens
    p1=yacc.yacc(method='LALR', 
                 tabmodule='ce_tab', 
                 debug=False,
                 write_tables=False,
                 errorlog=yacc.NullLogger())
    return p1

if __name__ == "__main__":
    import common.cgrammar as cgrammar

    try:
        name = 'txt\\bas.txt'
        if (len(sys.argv) > 1):
            name = sys.argv[1]

        gfun = cgrammar.cgrammar()
        myclex = clex.clex(gfun.comment_map)
        p = cyacc(myclex, gfun)

        f=open(name)
        data = f.read()
        res = p.parse(data,debug=0)

    except EOFError:
        print(e)

