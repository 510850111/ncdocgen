# ncdocgen 开发文档

## 目录

1. [开发环境搭建](#开发环境搭建)
2. [项目结构](#项目结构)
3. [开发规范](#开发规范)
4. [调试技巧](#调试技巧)
5. [打包发布](#打包发布)
6. [贡献指南](#贡献指南)

## 开发环境搭建

### 系统要求

- Python 3.10+
- Windows/Linux/macOS
- Git

### 安装步骤

```bash
# 1. 克隆仓库
git clone <repository-url>
cd ncdocgen

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 验证安装
python -c "import ncdocgen; print('OK')"
```

### 依赖列表

```
ply~=3.0       # Python Lex-Yacc 词法/语法分析库
click>=7.0    # 命令行参数解析
```

## 项目结构

```
ncdocgen/
├── docs/                       # 项目文档
│   ├── README.md              # 文档索引
│   ├── USER_GUIDE.md          # 用户手册
│   ├── ARCHITECTURE.md        # 架构设计
│   ├── DEVELOPMENT.md         # 开发文档（本文档）
│   ├── FAQ.md                 # 常见问题
│   └── CHANGELOG.md           # 更新日志
│
├── clang/                     # C语言解析模块
│   ├── __init__.py
│   ├── clex.py               # C语言词法分析器
│   ├── cyacc.py              # C语言语法分析器
│   ├── vlex.py               # 变量表达式词法分析器（继承clex）
│   ├── doxylex.py            # Doxygen注释词法分析器
│   ├── doxyyacc.py           # Doxygen注释语法分析器
│   ├── c_tab.py              # PLY生成的C parser表
│   └── doxy_tab.py           # PLY生成的Doxygen parser表
│
├── common/                    # 公共模块
│   ├── __init__.py
│   ├── cglobal.py            # 全局常量和工具函数
│   ├── cgrammar.py           # C语法处理函数
│   ├── key_generator.py      # Key.txt生成器
│   └── config.py             # 配置管理
│
├── visio/                     # 输出生成模块
│   ├── __init__.py
│   ├── cmarkdown.py          # Markdown文档生成器
│   ├── puml_drawer.py        # PlantUML流程图绘制器
│   └── puml_url_generator.py # PlantUML URL生成器
│
├── ctags/                     # 第三方工具
│   └── ctags.exe             # universal-ctags
│
├── __main__.py               # 程序入口（支持python -m）
├── cdocgen.py                # 命令行入口
├── gui.py                    # GUI入口
├── build_exe.py              # 打包脚本
├── README.md                 # 项目说明
├── LICENSE                   # 许可证
└── requirements.txt          # 依赖列表
```

## 开发规范

### 代码风格

遵循 PEP 8 规范：

```python
# 正确的代码风格示例

# 1. 导入顺序：标准库 -> 第三方库 -> 本地模块
import os
import sys

import click

from common.cglobal import *

# 2. 类名使用大驼峰
class NcdocgenGUI:
    """类的文档字符串"""
    
    # 3. 常量使用大写
    MAX_DEPTH = 10
    
    # 4. 函数名使用小写下划线
    def _create_widgets(self):
        """函数的文档字符串"""
        pass

# 5. 变量名使用小写下划线
input_files = []
file_count = 0

# 6. 私有成员以下划线开头
self._comment_cache = {}
```

### 注释规范

```python
# 文件头注释
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块名称 - 简短描述

详细功能说明：
    - 功能点1
    - 功能点2

使用示例:
    >>> from module import Class
    >>> obj = Class()
    >>> obj.method()

作者: ncdocgen团队
版本: v1.0.0
"""

# 函数/方法注释
def example_function(param1, param2):
    """
    函数功能的简要说明
    
    详细说明，包括算法逻辑、注意事项等。
    
    Args:
        param1 (str): 参数1的说明
        param2 (int): 参数2的说明
        
    Returns:
        bool: 返回值的说明
        
    Raises:
        ValueError: 什么情况下抛出此异常
        
    Example:
        >>> result = example_function('test', 123)
        >>> print(result)
        True
    """
    pass

# 行内注释
x = x + 1  # 补偿边界偏移
```

### Git提交规范

提交信息格式：

```
<type>: <subject>

<body>

<footer>
```

Type类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

示例：
```
feat: 增加对switch语句的流程图支持

- 添加DONESWITCH节点类型
- 实现case和default分支绘制
- 修复switch嵌套时的连接线问题

Closes #123
```

## 调试技巧

### 1. 启用详细日志

```python
# 在代码中设置日志级别
import logging
logging.basicConfig(level=logging.DEBUG)
```

或在GUI中勾选"详细日志"选项。

### 2. 使用IDE调试

PyCharm/VSCode 配置：

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "GUI Debug",
            "type": "python",
            "request": "launch",
            "module": "ncdocgen",
            "console": "integratedTerminal"
        },
        {
            "name": "CLI Debug",
            "type": "python",
            "request": "launch",
            "module": "ncdocgen",
            "args": ["--cli", "test.c", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

### 3. 单元测试

```python
# tests/test_clex.py
import unittest
from clang.clex import clex

class TestClex(unittest.TestCase):
    
    def test_identifier(self):
        cm = {}
        lexer = clex(cm)
        lexer.build()
        lexer.lexer.input('int x = 10;')
        tokens = []
        while True:
            tok = lexer.lexer.token()
            if not tok:
                break
            tokens.append(tok.type)
        self.assertIn('ID', tokens)
```

运行测试：
```bash
python -m pytest tests/
```

### 4. 常见问题调试

#### 词法分析错误

```python
# 在clex.py中添加调试输出
def t_error(self, t):
    print(f"非法字符: {t.value[0]} 在行 {t.lexer.lineno}")
    t.lexer.skip(1)
```

#### 语法分析错误

```python
# 在cyacc.py中启用调试
parser = yacc.yacc(debug=True, debuglog=yacc.PlyLogger(sys.stdout))
```

#### 流程图生成错误

```python
# 在puml_drawer.py中添加打印
print(f"节点类型: {ttype}, 内容: {node}")
```

## 打包发布

详细的发布流程请参阅 [RELEASE_GUIDE.md](RELEASE_GUIDE.md)。

### 快速发布流程

```bash
# 1. 更新版本号（cdocgen.py, gui.py, README.md, CHANGELOG.md）

# 2. 提交更改
git add .
git commit -m "chore: 准备发布 v1.0.1"
git push origin main

# 3. 打包
python build_exe.py

# 4. 测试
dist\ncdocgen.exe --cli --help

# 5. 打标签
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1

# 6. 创建 GitHub Release（上传 dist\ncdocgen.exe）
```

### 发布检查清单

- [ ] 版本号已更新（cdocgen.py, gui.py, README.md）
- [ ] CHANGELOG.md 已更新
- [ ] 所有测试通过
- [ ] GUI功能验证正常
- [ ] 命令行功能验证正常
- [ ] Key.txt生成功能正常
- [ ] 文档生成功能正常
- [ ] 打包后的exe可独立运行
- [ ] Git tag 已推送
- [ ] GitHub Release 已创建

## 贡献指南

### 提交Issue

发现bug或有新功能建议时，请提交Issue：

1. 使用清晰的标题
2. 详细描述问题或需求
3. 提供复现步骤（如果是bug）
4. 提供环境信息（OS、Python版本等）
5. 附上相关日志或截图

### 提交PR

1. **Fork仓库**到自己的账号

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码**
   - 遵循代码风格规范
   - 添加必要的注释
   - 编写单元测试

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 你的提交信息"
   ```

5. **推送到Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request**
   - 描述更改内容
   - 关联相关Issue
   - 等待Review

### 代码Review标准

- 代码是否遵循项目规范
- 是否有适当的注释
- 是否影响向后兼容性
- 是否有性能问题
- 是否有安全风险

---

**文档版本**: v1.0  
**更新日期**: 2026-04-03
