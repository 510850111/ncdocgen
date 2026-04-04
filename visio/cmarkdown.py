#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Markdown 文档生成器 (cmarkdown.py)
=================================
将C语言代码和doxygen注释转换为Markdown格式的详细设计文档。

主要功能:
    - 解析C文件，提取函数定义和注释
    - 生成函数说明表（原型、概述、参数、返回值等）
    - 调用puml_drawer生成PlantUML流程图
    - 支持生成内嵌/外链两种模式的流程图

文档模板:
    使用预定义的Markdown模板生成标准化文档

依赖模块:
    - puml_url_generator: PlantUML URL生成器
    - clex, cyacc: C语言解析器
    - cgrammar: C语法处理
    - puml_drawer: 流程图绘制器

作者: ncdocgen团队
"""

import os
import codecs
import logging
import click

# 导入PlantUML URL生成器（用于在线嵌入模式）
from .puml_url_generator import get_full_url

# ========================================================================
# Markdown模板定义
# ========================================================================

# 文档标题
md_dd_head = "# 详细设计"

# 基础模板（不包含图片）
# 使用Python字符串格式化语法 %()s
md_dd_tpl_base = """
## 子函数%(name)s

### 函数说明表

Table: 函数%(name)s描述表

| 条    目 | 内容 | 
|-----|-----|
| 原    型 | %(proto)s | 
| 概    述 | %(brief)s | 
| 参    数 | %(param)s | 
| 返 回 值 | %(return)s | 
| 引    用 | %(fcall)s | 
| 全局变量<br>引用 | %(gvarin)s | 
| 全局变量<br>修改 | %(gvarout)s | 
| 说    明 | %(details)s | 

### 程序流程

"""

# 完整模板（包含本地图片链接）
md_dd_tpl = md_dd_tpl_base + """
![图 函数%(name)s流程图](images/%(name)s.png)

"""


class mddoc:
    """
    Markdown文档类
    
    用于构建Markdown文档内容，提供插入函数文档、
    绘制流程图、保存文件等功能。
    
    Attributes:
        fname: 输出文件名
        embedded_puml_url: 是否嵌入PUML URL（在线图片）
        texts: 文档内容列表（字符串列表）
    """

    def __init__(self, filename='', add_title=False, embedded=False):
        """
        初始化Markdown文档
        
        @param filename: 输出文件名
        @param add_title: 是否自动添加文档标题（详细设计）
        @param embedded: 是否使用在线URL嵌入PUML图片
        """
        self.fname = filename
        self.embedded_puml_url = embedded
        self.reset()
        # 如果需要，添加文档标题
        if add_title:
            self.texts.append(md_dd_head)

    def reset(self):
        """重置文档内容，清空所有已添加的文本"""
        self.texts = []

    def insert_fun(self, title, finfo=None, nopic=False):
        """
        插入函数文档
        
        根据模板生成函数说明表，并添加到文档中。
        
        @param title: 函数名（标题）
        @param finfo: 函数字典，包含proto, brief, param等字段
        @param nopic: 是否不包含图片（使用md_dd_tpl_base模板）
        """
        dinfo = {}
        # 处理函数字典，将换行符替换为HTML的<br>标签
        for k, v in list(finfo.items()):
            dinfo[k] = v.strip().replace('\r', '<br>').replace('\n', '<br>')
        dinfo['name'] = title
        # 根据nopic参数选择模板
        if nopic:
            raw_text = md_dd_tpl_base % dinfo
        else:
            raw_text = md_dd_tpl % dinfo
        self.texts.append(raw_text)

    def save(self, fname=''):
        """
        保存文档到文件
        
        @param fname: 文件名，如果为空则使用初始化时指定的文件名
        """
        fname = fname if fname else self.fname
        try:
            logging.debug('writing md %s', fname)
        except:
            pass
        # 使用UTF-8编码写入文件
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.writelines(self.texts)

    def draw_puml(self, name, puml):
        """
        插入PlantUML流程图
        
        @param name: 函数名
        @param puml: PlantUML代码内容
        """
        # 如果启用了在线URL嵌入模式，将PUML代码转换为在线图片URL
        if self.embedded_puml_url:
            lines = puml.splitlines()
            # 去掉@startuml和@enduml，只保留中间内容
            url = get_full_url('\n'.join(lines[2:-2]))
            puml = f'![图 函数{name}流程图]({url})\n'
        self.texts.append(puml)


# ========================================================================
# 导入C语言解析相关模块
# ========================================================================

import clang.clex as clex
import clang.cyacc as cyacc
from common.cgrammar import cgrammar

from .puml_drawer import puml_drawer
from .cmarkdown import mddoc


def open_file(filename, encode='utf-8'):
    """
    打开文件并读取内容
    
    尝试多种编码格式，确保能正确读取各种编码的文件。
    尝试顺序: 系统默认, utf-8, gbk, gb2312, latin-1
    
    @param filename: 文件名
    @param encode: 首选编码格式
    @return: 文件内容字符串
    """
    ret = ""
    # Try multiple encodings
    for enc in [None, 'utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            if enc:
                ret = codecs.open(filename, 'r', enc).read()
            else:
                ret = codecs.open(filename, 'r').read()
            break
        except:
            continue
    return ret


def write_file(filename, nstr, encode='utf-8'):
    """
    写入文件
    
    @param filename: 文件名
    @param nstr: 要写入的字符串
    @param encode: 文件编码
    """
    with codecs.open(filename, 'w+', encode) as f:
        f.write(nstr)
        f.close()


import glob


def get_glob_files(filelist):
    """
    展开通配符文件列表
    
    将包含*或?的文件路径展开为实际文件列表。
    
    @param filelist: 文件路径列表（可能包含通配符）
    @return: 展开后的实际文件列表
    """
    files = []
    for f in filelist:
        if '*' in f or '?' in f:
            files.extend(glob.glob(f))
        else:
            files.append(f)
    return files


class CMarddownDoc(cgrammar):
    """
    C Markdown文档生成器（主类）
    
    继承cgrammar，整合词法分析、语法分析、文档生成功能。
    这是文档生成的核心类，协调各个模块完成文档生成任务。
    
    Attributes:
        lex: C语言词法分析器
        parser: C语言语法分析器
        puml: PlantUML流程图绘制器
        output: Markdown文档对象
        puml_dict: 函数名到PUML代码的映射字典
    """

    def __init__(self,
                 flag_map={},
                 keyword_file="",
                 output_fname="",
                 embedded=False):
        """
        初始化文档生成器
        
        @param flag_map: 标志位字典（verbose, debug等）
        @param keyword_file: 关键字文件（Key.txt）路径
        @param output_fname: 输出文件名
        @param embedded: 是否嵌入PUML URL
        """
        # 调用父类构造函数
        cgrammar.__init__(self)
        
        # 创建PlantUML绘制器，绑定注释映射
        self.puml = puml_drawer("puml", self.comment_map)
        
        # 设置标志位
        for k, v in flag_map.items():
            self.flag_set(k, v)

        # 构建词法分析器和语法分析器
        self.lex = clex.clex(self.comment_map)
        # 如果指定了关键字文件，加载关键字定义
        if (keyword_file != ""):
            self.lex.load_keyword_from_file(keyword_file)
        # 创建语法分析器，绑定回调函数（self）
        self.parser = cyacc.cyacc(self.lex, self, flag_map.get('debug', False))

        # 初始化文档输出
        outputname = self.init_doc(outputname=output_fname)
        self.output = mddoc(output_fname, embedded=embedded)
        self.reset()

    def save(self, fname=''):
        """保存文档（代理到output.save）"""
        self.output.save(fname)

    def reset(self):
        """重置状态"""
        self.puml_dict = {}
        self.output.reset()

    def init_doc(self, inputname='', outputname=''):
        """
        初始化文档输出路径
        
        设置当前目录和图片输出目录。
        
        @param inputname: 输入文件名（未使用）
        @param outputname: 输出文件名
        @return: 输出文件名
        """
        self.curdir = os.path.abspath(outputname)
        self.image_dir = os.path.join(self.curdir, 'images')

        # 如果未指定输出文件名，使用默认名称
        if outputname == '':
            outputname = os.path.join(self.curdir, '__autodd__.md')
        return outputname

    def extend_printer(self, name, header, exp, depth):
        """
        扩展打印器（核心方法）
        
        当语法分析器完成一个函数的解析后，调用此方法生成该函数的文档。
        
        @param name: 函数名
        @param header: 函数头信息字典
        @param exp: 函数表达式树（AST）
        @param depth: 流程图展开深度
        """
        # 检查是否需要生成文档（通过ignore标志控制）
        word_flag = 'ignore' not in header

        # 显示进度信息
        click.secho(f'-----Adding func:{name} @depth: {depth} Draw word={word_flag}',
               fg='green')

        # 输出Markdown函数说明表
        self.output.insert_fun(name, header, nopic=True)
        # 生成PlantUML流程图
        puml_text = self.puml.draw_fun(name, exp, 0, 0, depth)
        self.output.draw_puml(name, puml_text)
        # 保存到字典（供后续使用）
        self.puml_dict[name] = puml_text
        # 如果启用了详细输出，在控制台显示PUML代码
        if self.flag_get('verbose'):
            click.secho(puml_text, fg='yellow')

    def parse_file(self, filename):
        """
        解析单个C文件
        
        @param filename: C源文件路径
        """
        lines = open_file(filename)
        self.parser.parse(lines, debug=self.flag_get('debug'))

    def parse_files(self, files):
        """
        解析多个C文件
        
        先展开通配符，然后逐个解析。
        
        @param files: 文件路径列表
        """
        expand_files = get_glob_files(files)
        for fn in files:
            self.parse_file(fn)
