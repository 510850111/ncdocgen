#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 调试配置模块 (debug.py)
# -----------------------------------------------------------------------------
# 定义全局调试标志和常量，用于控制各模块的调试输出。
#
# 调试标志说明:
#     ENABLE_DRAW         - 绘图调试标志（0=关闭, 1=开启）
#     ENABLE_GENERIC_DEBUG- cglobal模块调试标志
#     ENABLE_HANDLE_DEBUG - chandler模块调试标志
#     ENABLE_DRAW_DEBUG   - cvisiodraw模块调试标志
#     ENABLE_VISIOD_DEBUG - visioflow模块调试标志
#     ENABLE_YACC_DEBUG   - yacc解析器调试标志
#     ENABLE_YTOOL_DEBUG  - YTOOL工具调试标志
#     CURINFO             - 打印yacc堆栈调用信息
#     DEBUG_DOXYYACC      - doxygen yacc解析调试标志
#
# 使用示例:
#     from common.debug import ENABLE_HANDLE_DEBUG, ENABLE_YACC_DEBUG
#     
#     if ENABLE_HANDLE_DEBUG == 1:
#         print("调试信息")
#
# 注意:
#     这些标志在开发调试时使用，生产环境应全部设为0
#
# 作者: ncdocgen团队
# -----------------------------------------------------------------------------

# 绘图调试标志
ENABLE_DRAW = 0

# cglobal打印标志
ENABLE_GENERIC_DEBUG = 0

# chandler打印标志
ENABLE_HANDLE_DEBUG = 0

# cvisiodraw打印标志
ENABLE_DRAW_DEBUG = 0

# visioflow打印标志
ENABLE_VISIOD_DEBUG = 0

# yacc打印标志
ENABLE_YACC_DEBUG = 0

# YTOOL打印标志
ENABLE_YTOOL_DEBUG = 0

# 打印 yacc 中的堆栈调用信息
CURINFO = 0

# 是否打印doxy yacc的解析
DEBUG_DOXYYACC = 0
