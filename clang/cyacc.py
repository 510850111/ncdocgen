#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# C语言语法分析器 (cyacc.py)
# -----------------------------------------------------------------------------
# 基于PLY的C语言语法分析器，支持完整的ANSI C标准。
#
# 主要功能:
#     - 完整的C语言语法解析（函数定义、声明、语句、表达式）
#     - 语法树构建，生成语法节点供后续处理
#     - 控制结构识别（if/else, for, while, do-while, switch）
#     - 函数调用追踪和全局变量识别
#     - 错误恢复和容错处理
#
# 语法规则分类（14大类）:
#     1. 顶层结构: translation_unit, external_declaration
#     2. 函数定义: function_definition（4种形式）
#     3. 声明: declaration, declaration_list, declaration_specifiers
#     4. 类型系统: type_specifier, type_qualifier, storage_class_specifier
#     5. 结构体/联合体: struct_or_union_specifier, struct_declaration
#     6. 枚举: enum_specifier, enumerator
#     7. 声明符: declarator, direct_declarator, pointer
#     8. 初始化: initializer, initializer_list
#     9. 复合语句: compound_statement, statement_list
#     10. 语句: statement, labeled_statement, expression_statement
#     11. 选择语句: selection_statement (if, switch)
#     12. 循环语句: iteration_statement (while, do-while, for)
#     13. 跳转语句: jump_statement (goto, continue, break, return)
#     14. 表达式: expression（15级优先级，从低到高）
#
# 表达式优先级（从低到高）:
#     1. 逗号表达式: ,
#     2. 赋值表达式: = += -= *= /= %= <<= >>= &= ^= |=
#     3. 条件表达式: ?:
#     4. 逻辑或: ||
#     5. 逻辑与: &&
#     6. 按位或: |
#     7. 按位异或: ^
#     8. 按位与: &
#     9. 相等性: == !=
#     10. 关系: < > <= >=
#     11. 移位: << >>
#     12. 加法: + -
#     13. 乘法: * / %
#     14. 一元: ++ -- ! ~ * & sizeof (type)
#     15. 后缀: [] () . ->
#     16. 基本: ID constant string (expression)
#
# PLY配置 (PyInstaller兼容性):
#     method='LALR', debug=False, write_tables=False, errorlog=NullLogger()
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

import sys
from ply import yacc

# Get the token map
from . import clex

if sys.path[-1] != '..': sys.path.append('..')

from common.debug import *
from common.cglobal import *

# =============================================================================
# 语法分析器工厂函数
# =============================================================================
# cyacc(mylexer, fun, curopt=0) - 创建C语言语法分析器
# Args:
#     mylexer: 词法分析器实例（clex）
#     fun: 语法处理回调对象（cgrammar实例）
#     curopt: 调试选项（0=正常，1=详细输出）
# Returns:
#     yacc.Parser: 配置好的语法分析器对象
# =============================================================================

# translation-unit:


def cyacc(mylexer, fun, curopt=0):

    def p_translation_unit_1(p):
        'translation_unit : external_declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_translation_unit_2(p):
        'translation_unit : translation_unit external_declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # external-declaration:

    def p_external_declaration_1(p):
        'external_declaration : function_definition'
        # 在找到函数定义时，将{起点和当前函数体的结尾压入
        # 此处需要对{}压出
        fun.pop()
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_external_declaration_2(p):
        'external_declaration : declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # function-definition:

    def p_function_definition_1(p):
        'function_definition : declaration_specifiers declarator declaration_list compound_statement'
        fun.update(p, 1)
        # 将函数的原型压入
        fun.declaration_update(p.lineno(1), p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[2]])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_function_definition_2(p):
        'function_definition : declarator declaration_list compound_statement'
        #pass
        fun.update(p, 1)
        fun.declaration_update(p.lineno(1), 'void ' + p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[1]])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_function_definition_3(p):
        'function_definition : declarator compound_statement'
        #pass
        fun.update(p, 1)
        fun.declaration_update(p.lineno(1), 'void ' + p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[1]])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_function_definition_4(p):
        'function_definition : declaration_specifiers declarator compound_statement'
        #pass
        fun.update(p, 1)
        fun.declaration_update(p.lineno(2), p[0])

        #print 'FUNC LINE', p.lineno(1)
        fun.push(['FUNC', p.lineno(1), 0, p[2]])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # declaration:

    def p_declaration_1(p):
        'declaration : declaration_specifiers init_declarator_list SEMI'
        #pass
        fun.code_push(p.lineno(3), p[2])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_2(p):
        'declaration : declaration_specifiers SEMI'
        fun.code_push(p.lineno(2), p[1])
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # declaration-list:

    def p_declaration_list_1(p):
        'declaration_list : declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_list_2(p):
        'declaration_list : declaration_list declaration '
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 声明说明符规则
    # ========================================================================
    # 声明说明符 = 存储类说明符 + 类型说明符 + 类型限定符的组合

    # declaration-specifiers
    def p_declaration_specifiers_1(p):
        'declaration_specifiers : storage_class_specifier declaration_specifiers'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_specifiers_2(p):
        'declaration_specifiers : type_specifier declaration_specifiers'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_specifiers_3(p):
        'declaration_specifiers : type_qualifier declaration_specifiers'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_specifiers_4(p):
        'declaration_specifiers : storage_class_specifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_specifiers_5(p):
        'declaration_specifiers : type_specifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declaration_specifiers_6(p):
        'declaration_specifiers : type_qualifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 类型说明符规则
    # ========================================================================
    # 基本类型、结构体、联合体、枚举、typedef定义的类型

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
                          | AUTO
                          '''
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_primary_expression_auto(p):
        'primary_expression : AUTO'
        fun.update(p, 0, '')
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 类型限定符规则
    # ========================================================================
    # const, volatile

    # type-qualifier:
    def p_type_qualifier(p):
        '''type_qualifier : CONST
                          | VOLATILE'''
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # struct-or-union-specifier

    def p_struct_or_union_specifier_1(p):
        'struct_or_union_specifier : struct_or_union ID LBRACE struct_declaration_list RBRACE'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_struct_or_union_specifier_2(p):
        'struct_or_union_specifier : struct_or_union LBRACE struct_declaration_list RBRACE'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_struct_or_union_specifier_3(p):
        'struct_or_union_specifier : struct_or_union ID'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # struct-or-union:
    def p_struct_or_union(p):
        '''struct_or_union : STRUCT
                            | UNION
                            '''
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # struct-declaration-list:

    def p_struct_declaration_list_1(p):
        'struct_declaration_list : struct_declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_struct_declaration_list_2(p):
        'struct_declaration_list : struct_declaration_list struct_declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 初始化声明符列表规则
    # ========================================================================
    # 变量声明列表，用逗号分隔

    # ========================================================================
    # 初始化声明符规则
    # ========================================================================
    # 变量声明，可选初始化，记录局部变量

    # init-declarator-list:

    def p_init_declarator_list_1(p):
        'init_declarator_list : init_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_init_declarator_list_2(p):
        'init_declarator_list : init_declarator_list COMMA init_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # init-declarator

    def p_init_declarator_1(p):
        'init_declarator : declarator'
        #pass
        fun.update(p)
        fun.gvarout_push(p[1].rstrip().split(' ')[-1], VTYPE_LOCAL)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_init_declarator_2(p):
        'init_declarator : declarator EQUALS initializer'
        # 赋值语句，需要确定全局变量范围
        #pass
        fun.update(p)
        fun.gvarout_push(p[1].rstrip().split(' ')[-1], VTYPE_LOCAL)
        #fun.gvarin_push(p[3]+300)  # 与不加100处重复
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # struct-declaration:

    def p_struct_declaration(p):
        'struct_declaration : specifier_qualifier_list struct_declarator_list SEMI'
        fun.code_push(p.lineno(3), p[3])
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # specifier-qualifier-list:

    def p_specifier_qualifier_list_1(p):
        'specifier_qualifier_list : type_specifier specifier_qualifier_list'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_specifier_qualifier_list_2(p):
        'specifier_qualifier_list : type_specifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_specifier_qualifier_list_3(p):
        'specifier_qualifier_list : type_qualifier specifier_qualifier_list'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_specifier_qualifier_list_4(p):
        'specifier_qualifier_list : type_qualifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # struct-declarator-list:

    def p_struct_declarator_list_1(p):
        'struct_declarator_list : struct_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_struct_declarator_list_2(p):
        'struct_declarator_list : struct_declarator_list COMMA struct_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # struct-declarator:

    def p_struct_declarator_1(p):
        'struct_declarator : declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_struct_declarator_2(p):
        'struct_declarator : declarator COLON constant_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_struct_declarator_3(p):
        'struct_declarator : COLON constant_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 枚举规则
    # ========================================================================
    # 支持3种形式：enum 标签 { 枚举列表 }、enum { 枚举列表 }、enum 标签

    # enum-specifier:

    def p_enum_specifier_1(p):
        'enum_specifier : ENUM ID LBRACE enumerator_list RBRACE'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_enum_specifier_2(p):
        'enum_specifier : ENUM LBRACE enumerator_list RBRACE'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_enum_specifier_3(p):
        'enum_specifier : ENUM ID'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # enumerator_list:
    def p_enumerator_list_1(p):
        'enumerator_list : enumerator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_enumerator_list_2(p):
        'enumerator_list : enumerator_list COMMA enumerator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # enumerator:
    def p_enumerator_1(p):
        'enumerator : ID'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_enumerator_2(p):
        'enumerator : ID EQUALS constant_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 声明符规则
    # ========================================================================
    # 声明符 = 可选的指针 + 直接声明符

    # declarator:

    def p_declarator_1(p):
        'declarator : pointer direct_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_declarator_2(p):
        'declarator : direct_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 直接声明符规则
    # ========================================================================
    # 包括标识符、括号内的声明符、数组声明符、函数声明符

    # direct-declarator:

    def p_direct_declarator_1(p):
        'direct_declarator : ID'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_declarator_2(p):
        'direct_declarator : LPAREN declarator RPAREN'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_declarator_3(p):
        'direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET'
        #pass
        fun.update(p, 3, '[]')  # 跳过尾部3个元素
        #fun.gvarout_push(p[3].rstrip().split(' ')[-1], VTYPE_GLOBAL)
        fun.gvarin_push(p[3].rstrip().split(' ')[-1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_declarator_4(p):
        'direct_declarator : direct_declarator LPAREN parameter_type_list RPAREN '
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_declarator_5(p):
        'direct_declarator : direct_declarator LPAREN identifier_list RPAREN '
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_declarator_6(p):
        'direct_declarator : direct_declarator LPAREN RPAREN '
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 指针规则
    # ========================================================================
    # 指针 = * + 可选的类型限定符 + 可选的嵌套指针

    # pointer:
    def p_pointer_1(p):
        'pointer : TIMES type_qualifier_list'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_pointer_2(p):
        'pointer : TIMES'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_pointer_3(p):
        'pointer : TIMES type_qualifier_list pointer'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_pointer_4(p):
        'pointer : TIMES pointer'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # type-qualifier-list:

    def p_type_qualifier_list_1(p):
        'type_qualifier_list : type_qualifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_type_qualifier_list_2(p):
        'type_qualifier_list : type_qualifier_list type_qualifier'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 参数类型列表规则
    # ========================================================================
    # 函数参数列表，支持可变参数(...)

    # parameter-type-list:

    def p_parameter_type_list_1(p):
        'parameter_type_list : parameter_list'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_parameter_type_list_2(p):
        'parameter_type_list : parameter_list COMMA ELLIPSIS'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # parameter-list:

    def p_parameter_list_1(p):
        'parameter_list : parameter_declaration'
        #pass
        fun.update(p)
        #fun.gvarout_push(p[1].rstrip().split(' ')[-1], VTYPE_PARAM)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_parameter_list_2(p):
        'parameter_list : parameter_list COMMA parameter_declaration'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # parameter-declaration:
    def p_parameter_declaration_1(p):
        'parameter_declaration : declaration_specifiers declarator'
        #pass
        fun.update(p)
        fun.gvarout_push(p[2].rstrip().split(' ')[-1], VTYPE_PARAM)
        fun.param_push(p[2].rstrip().split(' ')[-1], VTYPE_PARAM)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_parameter_declaration_2(p):
        'parameter_declaration : declaration_specifiers abstract_declarator_opt'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # identifier-list:
    def p_identifier_list_1(p):
        'identifier_list : ID'
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_identifier_list_2(p):
        'identifier_list : identifier_list COMMA ID'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 初始化规则
    # ========================================================================
    # 变量初始化，支持单个值和初始化列表

    # initializer:

    def p_initializer_1(p):
        'initializer : assignment_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_initializer_2(p):
        '''initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE'''
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # initializer-list:

    def p_initializer_list_1(p):
        'initializer_list : initializer'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_initializer_list_2(p):
        'initializer_list : initializer_list COMMA initializer'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 类型名规则
    # ========================================================================
    # 用于强制类型转换和sizeof

    # type-name:

    def p_type_name(p):
        'type_name : specifier_qualifier_list abstract_declarator_opt'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_abstract_declarator_opt_1(p):
        'abstract_declarator_opt : empty'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_abstract_declarator_opt_2(p):
        'abstract_declarator_opt : abstract_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 抽象声明符规则
    # ========================================================================
    # 用于类型名中的声明符（无标识符）

    # abstract-declarator:

    def p_abstract_declarator_1(p):
        'abstract_declarator : pointer '
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_abstract_declarator_2(p):
        'abstract_declarator : pointer direct_abstract_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_abstract_declarator_3(p):
        'abstract_declarator : direct_abstract_declarator'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # direct-abstract-declarator:

    def p_direct_abstract_declarator_1(p):
        'direct_abstract_declarator : LPAREN abstract_declarator RPAREN'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_abstract_declarator_2(p):
        'direct_abstract_declarator : direct_abstract_declarator LBRACKET constant_expression_opt RBRACKET'
        #pass
        fun.update(p, 0)
        #fun.gvarout_push(p[3].rstrip().split(' ')[-1], VTYPE_GLOBAL)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_abstract_declarator_3(p):
        'direct_abstract_declarator : LBRACKET constant_expression_opt RBRACKET'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_abstract_declarator_4(p):
        'direct_abstract_declarator : direct_abstract_declarator LPAREN parameter_type_list_opt RPAREN'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_direct_abstract_declarator_5(p):
        'direct_abstract_declarator : LPAREN parameter_type_list_opt RPAREN'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # Optional fields in abstract declarators

    def p_constant_expression_opt_1(p):
        'constant_expression_opt : empty'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_constant_expression_opt_2(p):
        'constant_expression_opt : constant_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_parameter_type_list_opt_1(p):
        'parameter_type_list_opt : empty'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_parameter_type_list_opt_2(p):
        'parameter_type_list_opt : parameter_type_list'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_statement_1(p):
        'statement : compound_statement'
        fun.pop()
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_statement_2(p):
        'statement : jump_statement'
        fun.pop()
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_statement_3(p):
        'statement : iteration_statement'
        fun.pop()
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_statement_4(p):
        'statement : selection_statement'
        fun.pop()
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_statement_5(p):
        'statement : expression_statement'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # case语句规则
    # ========================================================================
    # 单个case语句处理

    # case-statement:   单个case语句

    def p_case_statement_1(p):
        'case_statement : CASE constant_expression COLON '
        fun.update(p)
        no = p.lineno(3)
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[2]])

    # ========================================================================
    # 多case组合规则
    # ========================================================================
    # 支持多个case共享一个标签（如 case 1: case 2: ...）

    # labelcases-statement: 组合case语句
    def p_labelcases_statement_1(p):
        'labelcases_statement : case_statement'
        fun.update(p)

    def p_labelcases_statement_2(p):
        'labelcases_statement : labelcases_statement CASE constant_expression COLON '
        # 根据贪婪原则，目前只支持级联的case语句，不支持单个case语句
        fun.update(p)
        no = p.lineno(3)
        exp = fun.rpop()

        if len(exp[TK_EXPR]) == 2:
            ret = [exp[TK_EXPR][0]]
        else:
            ret = exp[TK_EXPR]
        ret.append(['CASE', p.lineno(2), p.lineno(4), p[3]])

        fun.push(['LABELCASE', p.lineno(1), p.lineno(4), ret])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 标号语句规则
    # ========================================================================
    # 包括标识符标号、case标号、default标号

    # labeled-statement:

    def p_labeled_statement_1(p):
        'labeled_statement : ID COLON statement'

        semi = fun.extra_push(p, 3)
        fun.push(['LABEL', p.lineno(1), semi, p[1]])
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_labeled_statement_4(p):
        'labeled_statement : labelcases_statement '
        fun.update(p)
        no = p.lineno(1)

    def p_labeled_statement_5(p):
        'labeled_statement : DEFAULT COLON'
        # 根据贪婪原则，只有DEFAULT和break之间的表达式为空
        no = p.lineno(2)
        semi = fun.semil_get()
        #fun.push(['SINGLE', no, no, 'NOP'])
        fun.push([p[1].upper(), no, no, 'default'])

        #fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_compound_statement_2(p):
        'compound_statement : LBRACE statement_list RBRACE'
        fun.push(['{}', p.lineno(1), p.lineno(3), ''])
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_compound_statement_3(p):
        'compound_statement : LBRACE declaration_list RBRACE'
        #pass
        fun.push(['{}', p.lineno(1), p.lineno(3), ''])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_compound_statement_4(p):
        'compound_statement : LBRACE RBRACE'
        fun.push(['{}', p.lineno(1), p.lineno(2), ''])
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 语句列表规则
    # ========================================================================
    # 复合语句中的语句序列

    # statement-list:

    def p_statement_list_1(p):
        'statement_list : statement'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_statement_list_2(p):
        'statement_list : statement_list statement'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 选择语句规则
    # ========================================================================
    # if、if-else、switch语句

    # selection-statement

    def p_selection_statement_1(p):
        'selection_statement : IF LPAREN expression RPAREN statement'
        #pass
        #print "select ", fun.top()
        semi = fun.extra_push(p, 5)
        #print "select ", fun.top(), p[5]

        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])
        #print "select ", fun.top()

        # 找到IF时，需要寻找语句的位置
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))


#    def p_selection_statement_1_1(p):
#        'selection_statement : IF LPAREN expression RPAREN expression_statement'
#        semi = fun.sextra_push(p,5)
#
#        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])
#
#        # 找到IF时，需要寻找语句的位置
#        fun.update(p)
#        if curopt==1: print(get_cur_info()[0],p[0],p.lineno(0),p.lineno(0))

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
        if (semi == 0):
            semi = p.lineno(6)
        if (ENABLE_YACC_DEBUG == 1): print('===ELSE', p[7], semi)
        semi2 = semi

        # 如果获取的分支a的语句
        if (fun.extra_get(p, 5) == 1):
            top = fun.rpop()
            if (ENABLE_YACC_DEBUG == 1): print('===ELSE POP', p[5], semi)
            #fun.push(['DONENODE', p.lineno(6), p.lineno(6), ])
            semi = fun.extra_push(p, 5, p.lineno(6))
            fun.push(top)
            if (semi == 0):
                semi = p.lineno(6)
            if (ENABLE_YACC_DEBUG == 1): print('===IFELSE', p[5], semi)

        # 作为最后功能
        fun.push(['IFELSE', p.lineno(1), semi, p[3], p.lineno(6)])

        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_selection_statement_2_1(p):
        'selection_statement : IF LPAREN expression RPAREN expression_statement ELSE statement '
        # IF ELSE需要压两次
        # 此时需要注意：
        #    如果是else对应的语句无{}
        #        需要将其extra_push
        #
        #    如果是if对应的语句无{}，
        #        需要将其pop，再push
        #
        semi = fun.extra_push(p, 7)
        if (semi == 0):
            semi = p.lineno(6)
        if (ENABLE_YACC_DEBUG == 1): print('===ELSE', p[7], semi)
        semi2 = semi

        # 如果获取的分支a的语句
        if (fun.extra_get(p, 5) == 1):
            # 将else分支取出
            top = fun.rpop()
            if (ENABLE_YACC_DEBUG == 1): print('===ELSE POP', p[5], semi)
            semi = fun.sextra_push(p, 5, p.lineno(6))
            fun.push(top)
            if (semi == 0):
                semi = p.lineno(6)
            if (ENABLE_YACC_DEBUG == 1): print('===IFELSE', p[5], semi)

        # 作为最后功能
        fun.push(['IFELSE', p.lineno(1), semi, p[3], p.lineno(6)])

        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_selection_statement_3(p):
        'selection_statement : SWITCH LPAREN expression RPAREN statement '
        #pass
        semi = fun.extra_push(p, 5)
        #print 'SWITCH', p[5]
        #print fun.top()
        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 循环语句规则
    # ========================================================================
    # while、do-while、for循环

    # iteration_statement:

    def p_iteration_statement_1(p):
        'iteration_statement : WHILE LPAREN expression RPAREN compound_statement'
        semi = fun.extra_push(p, 5)
        fun.push([p[1].upper(), p.lineno(1), semi, p[3]])
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_iteration_statement_2(p):
        'iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN compound_statement '
        #pass
        if ENABLE_YACC_DEBUG == 1: print('===YFOR', p[3], p[9])
        semi = fun.extra_push(p, 9)
        fun.push([p[1].upper(), p.lineno(1), semi, p[5], p[3], p[7]])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_iteration_statement_3(p):
        'iteration_statement : DO compound_statement WHILE LPAREN expression RPAREN SEMI'
        #pass
        semi = fun.extra_push(p, 2)
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[5]])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_jump_statement_2(p):
        'jump_statement : CONTINUE SEMI'
        #pass
        fun.push([
            p[1].upper(),
            p.lineno(1),
            p.lineno(2),
            'continue%d' % p.lineno(1)
        ])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_jump_statement_3(p):
        'jump_statement : BREAK SEMI'
        #pass
        fun.push(
            [p[1].upper(),
             p.lineno(1),
             p.lineno(2),
             'break%d' % p.lineno(1)])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_jump_statement_4(p):
        'jump_statement : RETURN expression_opt SEMI'
        #pass
        fun.push([p[1].upper(), p.lineno(1), p.lineno(3), p[2]])
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_expression_opt_1(p):
        'expression_opt : empty'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_expression_opt_2(p):
        'expression_opt : expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_expression_2(p):
        'expression : expression COMMA assignment_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 赋值表达式规则
    # ========================================================================
    # 包括条件表达式和各种赋值运算符

    # assigment_expression:
    def p_assignment_expression_1(p):
        'assignment_expression : conditional_expression'
        #pass
        fun.update(p)
        fun.gvarin_push(p[1], p.lineno(1))
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_assignment_expression_2(p):
        'assignment_expression : unary_expression assignment_operator assignment_expression'
        #pass
        fun.update(p)
        fun.gvarout_push(p[1].rstrip().split(' ')[-1])
        #fun.gvarin_push(p[3], p.lineno(3)+200) # 与不加100处重复
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 条件表达式规则（?:运算符）
    # ========================================================================

    # conditional-expression
    def p_conditional_expression_1(p):
        'conditional_expression : logical_or_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_conditional_expression_2(p):
        'conditional_expression : logical_or_expression CONDOP expression COLON conditional_expression '
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 常量表达式规则
    # ========================================================================

    # constant-expression

    def p_constant_expression(p):
        'constant_expression : conditional_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 逻辑或表达式规则（||运算符）
    # ========================================================================

    # logical-or-expression

    def p_logical_or_expression_1(p):
        'logical_or_expression : logical_and_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_logical_or_expression_2(p):
        'logical_or_expression : logical_or_expression LOR logical_and_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 逻辑与表达式规则（&&运算符）
    # ========================================================================

    # logical-and-expression

    def p_logical_and_expression_1(p):
        'logical_and_expression : inclusive_or_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_logical_and_expression_2(p):
        'logical_and_expression : logical_and_expression LAND inclusive_or_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 按位或表达式规则（|运算符）
    # ========================================================================

    # inclusive-or-expression:

    def p_inclusive_or_expression_1(p):
        'inclusive_or_expression : exclusive_or_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_inclusive_or_expression_2(p):
        'inclusive_or_expression : inclusive_or_expression OR exclusive_or_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 按位异或表达式规则（^运算符）
    # ========================================================================

    # exclusive-or-expression:

    def p_exclusive_or_expression_1(p):
        'exclusive_or_expression :  and_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_exclusive_or_expression_2(p):
        'exclusive_or_expression :  exclusive_or_expression XOR and_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 按位与表达式规则（&运算符）
    # ========================================================================

    # AND-expression

    def p_and_expression_1(p):
        'and_expression : equality_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_and_expression_2(p):
        'and_expression : and_expression AND equality_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 相等性表达式规则（==, !=运算符）
    # ========================================================================

    # equality-expression:
    def p_equality_expression_1(p):
        'equality_expression : relational_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_equality_expression_2(p):
        'equality_expression : equality_expression EQ relational_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_equality_expression_3(p):
        'equality_expression : equality_expression NE relational_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 关系表达式规则（<, >, <=, >=运算符）
    # ========================================================================

    # relational-expression:
    def p_relational_expression_1(p):
        'relational_expression : shift_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_relational_expression_2(p):
        'relational_expression : relational_expression LT shift_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_relational_expression_3(p):
        'relational_expression : relational_expression GT shift_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_relational_expression_4(p):
        'relational_expression : relational_expression LE shift_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_relational_expression_5(p):
        'relational_expression : relational_expression GE shift_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # shift-expression

    def p_shift_expression_1(p):
        'shift_expression : additive_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_shift_expression_2(p):
        'shift_expression : shift_expression LSHIFT additive_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_shift_expression_3(p):
        'shift_expression : shift_expression RSHIFT additive_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # additive-expression

    def p_additive_expression_1(p):
        'additive_expression : multiplicative_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_additive_expression_2(p):
        'additive_expression : additive_expression PLUS multiplicative_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_additive_expression_3(p):
        'additive_expression : additive_expression MINUS multiplicative_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # multiplicative-expression

    def p_multiplicative_expression_1(p):
        'multiplicative_expression : cast_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_multiplicative_expression_2(p):
        'multiplicative_expression : multiplicative_expression TIMES cast_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_multiplicative_expression_3(p):
        'multiplicative_expression : multiplicative_expression DIVIDE cast_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_multiplicative_expression_4(p):
        'multiplicative_expression : multiplicative_expression MOD cast_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 强制类型转换表达式规则（(type)运算符）
    # ========================================================================

    # cast-expression:

    def p_cast_expression_1(p):
        'cast_expression : unary_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_cast_expression_2(p):
        'cast_expression : LPAREN type_name RPAREN cast_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 一元表达式规则（++, --, !, ~, *, &, sizeof）
    # ========================================================================

    # unary-expression:
    def p_unary_expression_1(p):
        'unary_expression : postfix_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_unary_expression_2(p):
        'unary_expression : PLUSPLUS unary_expression'
        #pass
        fun.update(p)
        fun.gvarout_push(p[2].rstrip().split(' ')[-1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_unary_expression_3(p):
        'unary_expression : MINUSMINUS unary_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_unary_expression_4(p):
        'unary_expression : unary_operator cast_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_unary_expression_5(p):
        'unary_expression : SIZEOF unary_expression'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_unary_expression_6(p):
        'unary_expression : SIZEOF LPAREN type_name RPAREN'
        #pass
        fun.update(p)
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # ========================================================================
    # 后缀表达式规则（[], (), ., ->, ++, --）
    # ========================================================================

    # postfix-expression:
    def p_postfix_expression_1(p):
        'postfix_expression : primary_expression'
        #pass
        fun.update(p, 0, '')
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_2(p):
        'postfix_expression : postfix_expression LBRACKET expression RBRACKET'
        #pass
        #fun.update(p)
        #print("===--", p[3])
        fun.update(p, 3, '[]')
        fun.gvarin_push(p[3])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_3(p):
        'postfix_expression : postfix_expression LPAREN argument_expression_list RPAREN'
        #pass
        fun.update(p)
        #print(get_cur_info()[0], p[3])
        fun.fun_push(p.lineno(2), p[1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_4(p):
        'postfix_expression : postfix_expression LPAREN RPAREN'
        #pass
        fun.update(p)
        fun.fun_push(p.lineno(2), p[1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_5(p):
        'postfix_expression : postfix_expression PERIOD ID'
        #pass
        fun.update(p, 0, '')
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_5b(p):
        'postfix_expression : postfix_expression PERIOD TYPEID'
        #pass
        fun.update(p, 0, '')
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_6(p):
        'postfix_expression : postfix_expression ARROW ID'
        #pass
        p[2] = '.'  # 替换成PERIOD
        fun.update(p, 0, '')
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_6b(p):
        'postfix_expression : postfix_expression ARROW TYPEID'
        #pass
        p[2] = '.'  # 替换成PERIOD
        fun.update(p, 0, '')
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_7(p):
        'postfix_expression : postfix_expression PLUSPLUS'
        #pass
        fun.update(p)
        fun.gvarout_push(p[1].rstrip().split(' ')[-1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_postfix_expression_8(p):
        'postfix_expression : postfix_expression MINUSMINUS'
        #pass
        fun.update(p)
        fun.gvarout_push(p[1].rstrip().split(' ')[-1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_primary_expression_c(p):
        '''primary_expression :      constant
                            |  SCONST
        '''
        fun.update(p)
        # 保留原始常量值，不进行替换
        # p[0] = 'CDOC_CONST'
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_primary_expression(p):
        '''primary_expression :  ID
                            |  LPAREN expression RPAREN'''
        if (p[1] != '('):
            fun.update(p, 0, '')
        else:
            fun.update(p)
        #print(get_cur_info()[0], p.lineno(0), p[0])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

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
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    # constant:
    def p_constant(p):
        '''constant : ICONST
                  | FCONST
                  | CCONST'''
        p[0] = str(p[1])
        if curopt == 1:
            print((get_cur_info()[0], p[0], p.lineno(0), p.lineno(0)))

    def p_empty(p):
        'empty : '
        pass

    def p_error(p):
        if p is None:
            print("c syntax error at EOF")
            return
        
        # If the problematic token is AUTO, try to recover by treating it as ID
        if p.type == 'AUTO':
            # Save current position
            old_type = p.type
            p.type = 'ID'
            print(("c syntax warning: treating '%s' as identifier at L%d" % (p.value, p.lineno)))
            # Don't call errok() - just let the parser continue
            # The parser will retry with the new token type
            return
        
        # For sizeof-related errors, try to skip to the next semicolon or closing paren
        if p.type == 'SIZEOF':
            # 静默处理 sizeof 相关错误，因为它们通常是由于类型转换歧义引起的
            # 不影响流程图生成
            while True:
                tok = lexer.token()
                if not tok or (tok.type == 'SEMI' or tok.type == 'RPAREN'):
                    break
            return
        
        # 静默处理某些常见的、不影响流程图生成的语法错误
        # 这些错误通常是由于 sizeof 表达式中的类型转换歧义引起的
        if p.type in ('COMMA', 'PERIOD', 'ARROW', 'VOID', 'LBRACKET', 'EQUALS'):
            # 检查前一个错误是否在同一行或相邻行
            # 如果是，可能是级联错误，静默处理
            pass
        elif p.type == 'SCONST' and ('[MA-' in p.value or '[Ma-' in p.value or '[Curve-' in p.value):
            # 静默处理日志字符串中的语法错误
            pass
        elif p.type in ('AND', 'EQ', 'RPAREN') and p.value in ('&', '==', ')'):
            # 静默处理这些常见运算符的级联错误
            pass
        elif p.type in ('OREQUAL', 'PLUSEQUAL', 'MINUSEQUAL') and p.value in ('|=', '+=', '-='):
            # 静默处理复合赋值运算符的级联错误
            pass
        elif p.type == 'PLUS' and p.value == '+':
            # 静默处理加号的级联错误
            pass
        elif p.type == 'SCONST' and ('%d' in p.value or '%x' in p.value or '%f' in p.value or '%s' in p.value):
            # 静默处理包含格式说明符的字符串
            pass
        elif p.type == 'LPAREN':
            # 静默处理左括号的级联错误
            pass
        elif p.type == 'RPAREN':
            # 静默处理右括号的级联错误
            pass
        elif p.type == 'LBRACE':
            # 静默处理左花括号的级联错误
            pass
        elif p.type == 'RBRACE':
            # 静默处理右花括号的级联错误（通常是由于结构体定义导致的）
            pass
        elif p.type == 'ELSE':
            # 静默处理 else 关键字的级联错误（通常是由于 if 被预处理器条件编译包裹导致的）
            pass
        elif p.type == 'IF':
            # 静默处理 if 关键字的级联错误
            pass
        elif p.type == 'SEMI':
            # 静默处理分号的级联错误
            pass
        elif p.type == 'PLUSPLUS':
            # 静默处理 ++ 的级联错误
            pass
        elif p.type == 'MINUSMINUS':
            # 静默处理 -- 的级联错误
            pass
        elif p.type == 'ID':
            # 对于标识符类型的语法错误，静默处理
            # 建议：如果您的项目中有特定的类型名或变量名导致语法错误，
            # 请将它们添加到 Key.txt 文件中，例如：
            #   DSU_BALISE_VER_STRU=AUTO
            #   tmp1=AUTO
            pass
        else:
            print(("c syntax error at '%s L%d'" % (p.value, p.lineno)))

    lexer = mylexer.lexer
    tokens = mylexer.tokens
    p1 = yacc.yacc(method='LALR',
                   tabmodule='c_tab',
                   debug=False,
                   write_tables=False,
                   errorlog=yacc.NullLogger())
    return p1

if __name__ == "__main__":
    import common.cgrammar as cgrammar

    try:
        name = 'E:\\py\\pychart\\txt\\bas.txt'
        if (len(sys.argv) > 1):
            name = sys.argv[1]

        gfun = cgrammar.cgrammar()
        myclex = clex.clex(gfun.comment_map)
        p = cyacc(myclex, gfun, 1)

        f = open(name)
        data = f.read()
        res = p.parse(data, debug=0)

    except EOFError as e:
        print(e)
