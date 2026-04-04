"""
common 包 - 公共模块
==================
提供通用的工具函数和常量定义。

子模块:
    cglobal         - 全局常量和节点索引定义
    cgrammar        - C语法处理函数
    key_generator   - Key.txt生成器
    config          - 配置管理（标签翻译、默认值）

使用示例:
    from common.cglobal import TV_ID, TK_TYPE, make_node
    from common.key_generator import update_key_file
    
    # 创建语法树节点
    node = make_node('DONEIF', id=1, start=10, end=20)
    
    # 更新Key.txt
    count = update_key_file(project_path='./src', output_path='Key.txt')

作者: ncdocgen团队
"""

import sys

# 添加父目录到路径，支持从子目录直接运行模块
if sys.path[0] != '..':
    sys.path.insert(0, "..")
