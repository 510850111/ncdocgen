"""
visio 包 - 输出生成模块
======================
提供文档生成和流程图绘制功能。

子模块:
    cmarkdown           - Markdown文档生成器
    puml_drawer         - PlantUML流程图绘制器
    puml_url_generator  - PlantUML URL生成器

使用示例:
    from visio.cmarkdown import CMarddownDoc
    from visio.puml_drawer import puml_drawer
    
    doc = CMarddownDoc(amap, keyword_file='Key.txt', output_fname='out.md')
    doc.parse_files(['code.c'])
    doc.save('out.md')

作者: ncdocgen团队
"""

import sys

# 添加父目录到路径，支持从子目录直接运行模块
if sys.path[-1] != '..':
    sys.path.append('..')
