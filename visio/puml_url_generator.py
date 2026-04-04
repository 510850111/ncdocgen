###################################################################################
#
#    Copyright (C) Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

"""
PlantUML URL 生成器
==================
将PlantUML文本转换为可以在线访问的图片URL。

编码原理:
    1. 将PlantUML文本使用Deflate算法压缩
    2. 去掉zlib头(前2字节)和adler32校验(后4字节)
    3. 对剩余数据进行Base64编码
    4. 将Base64字符集转换为PlantUML特殊字符集
    
PlantUML特殊字符集:
    0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_
    
使用示例:
    puml_text = "@startuml\\nA -> B\\n@enduml"
    url = get_full_url(puml_text)
    # 结果: http://www.plantuml.com/plantuml/svg/...
    
    生成的URL可直接在Markdown中使用:
    ![流程图](url)

在线服务:
    - 官方服务器: www.plantuml.com/plantuml
    - 支持格式: PNG, SVG

作者: ncdocgen团队 (基于Cetmix的开源实现)
"""

import base64
import string
from zlib import compress

# 字符集转换表
# PlantUML使用特殊的字符集，不同于标准Base64
maketrans = bytes.maketrans

# PlantUML使用的64个字符
plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'

# 标准Base64使用的64个字符
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'

# 创建转换表：将Base64字符映射到PlantUML字符
b64_to_plantuml = maketrans(base64_alphabet.encode('utf-8'),
                            plantuml_alphabet.encode('utf-8'))


def get_url(plantuml_text):
    """
    将PlantUML文本编码为URL路径部分
    
    编码步骤:
    1. 将文本转为UTF-8字节
    2. 使用Deflate算法压缩(zlib)
    3. 去掉zlib头(2字节)和adler32校验(4字节)
    4. Base64编码
    5. 字符集转换为PlantUML格式
    
    Args:
        plantuml_text: PlantUML代码文本
        
    Returns:
        str: 编码后的URL路径字符串
        
    Example:
        >>> text = "@startuml\\nA->B\\n@enduml"
        >>> url = get_url(text)
        >>> print(url)
        'SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKifpStXuWfGSQcP...'
    """
    # 压缩PlantUML文本
    # compress()使用deflate算法，返回zlib格式的压缩数据
    zipped_str = compress(plantuml_text.encode('utf-8'))
    
    # 去掉zlib头(前2字节)和adler32校验(后4字节)
    # 只保留中间的deflate压缩数据
    compressed_string = zipped_str[2:-4]
    
    # Base64编码并转换字符集
    # 先进行标准Base64编码，然后映射到PlantUML字符集
    return base64.b64encode(compressed_string).translate(
        b64_to_plantuml).decode('utf-8')


def get_full_url(plantuml_text, server=''):
    """
    获取完整的PlantUML图片URL
    
    Args:
        plantuml_text: PlantUML代码文本
        server: PlantUML服务器地址，默认使用官方服务器
        
    Returns:
        str: 完整的图片URL，可直接在浏览器或Markdown中使用
        
    Example:
        >>> text = "@startuml\\nstart\\n:Hello;\\nstop\\n@enduml"
        >>> url = get_full_url(text)
        >>> print(url)
        'http://www.plantuml.com/plantuml/svg/...'
        
        # 在Markdown中使用
        >>> print(f"![流程图]({url})")
        '![流程图](http://www.plantuml.com/plantuml/svg/...)'
    """
    # 使用官方服务器或自定义服务器
    server = server or "http://www.plantuml.com/plantuml/svg/"
    
    # 拼接服务器地址和编码后的路径
    return server + get_url(plantuml_text)
