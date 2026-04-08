# ncdocgen 发布指南

本文档详细说明如何将 ncdocgen 打包并发布到 GitHub Releases。

## 📋 发布前准备

### 1. 确认发布版本号

版本号格式：`主版本.次版本.修订号`（如 `1.0.0`）

需要更新版本号的文件：

| 文件 | 更新位置 | 示例 |
|------|----------|------|
| `cdocgen.py` | `__version__ = "x.x.x"` | `__version__ = "1.0.1"` |
| `gui.py` | `PROJECT_VERSION = "x.x.x"` | `PROJECT_VERSION = "1.0.1"` |
| `README.md` | 版本徽章、底部版本声明 | `version-1.0.1-blue` |
| `docs/CHANGELOG.md` | 新增版本条目 | `## [1.0.1] - YYYY-MM-DD` |

### 2. 更新 CHANGELOG.md

在 `docs/CHANGELOG.md` 中添加新版本条目：

```markdown
## [1.0.1] - 2026-04-04

### 新增
- 新功能描述

### 改进
- 改进点描述

### 修复
- 修复的bug描述
```

### 3. 提交所有更改

```bash
# 检查状态
git status

# 添加所有修改
git add .

# 提交
git commit -m "chore: 准备发布 v1.0.1"

# 推送到远程
git push origin main
```

---

## 🔨 打包 EXE

### 运行打包脚本

```bash
# 进入项目目录
cd ncdocgen

# 运行打包脚本
python build_exe.py
```

### 打包过程说明

脚本会自动完成以下操作：
1. ✅ 清理旧的构建文件
2. ✅ 检查并安装 PyInstaller
3. ✅ 打包为单文件 EXE
4. ✅ 包含 ctags 工具
5. ✅ 清理临时文件

### 输出文件

打包成功后生成：
```
dist/
├── ncdocgen.exe      # GUI 可执行程序（约 15-20MB）
└── ncdocgen-cli.exe  # CLI 可执行程序（约 15-20MB）
```

---

## 🧪 发布前测试

### 测试清单

- [ ] **GUI 功能测试**
  - [ ] 双击运行 `dist\ncdocgen.exe`，GUI 正常显示
  - [ ] 版本号显示正确
  - [ ] 选择输入文件功能正常
  - [ ] 生成 Key.txt 功能正常
  - [ ] 生成文档功能正常
  - [ ] 关于对话框显示正确

- [ ] **CLI 功能测试**
  ```bash
  # 测试帮助信息
  dist\ncdocgen-cli.exe --help
  
  # 测试文档生成
  dist\ncdocgen-cli.exe test.c -o test_out.md -v
  
  # 测试 Key.txt 生成
  dist\ncdocgen-cli.exe --update-key --project-path . -v
  ```

- [ ] **独立运行测试**
  - [ ] 将 `ncdocgen.exe` 复制到全新目录
  - [ ] 在新目录中运行，确认无依赖错误
  - [ ] 确认自动创建 `log/` 目录

- [ ] **中文支持测试**
  - [ ] 测试中文注释解析
  - [ ] 测试中文字符串解析

---

## 🏷️ 创建 Git Tag

```bash
# 创建带注释的标签（推荐）
git tag -a v1.0.1 -m "Release version 1.0.1"

# 或者创建轻量标签
git tag v1.0.1

# 推送标签到远程
git push origin v1.0.1
```

### 标签命名规范

- 格式：`v主版本.次版本.修订号`
- 示例：`v1.0.0`, `v1.0.1`, `v1.1.0`

---

## 🚀 创建 GitHub Release

### 方式一：通过 GitHub Web 界面

1. 打开项目页面：`https://github.com/510850111/ncdocgen`
2. 点击右侧 **Releases** → **Create a new release**
3. 选择标签：`v1.0.1`
4. 填写发布信息：

**标题**：`ncdocgen v1.0.1`

**描述**：
```markdown
## ncdocgen v1.0.1

### 新增功能
- 功能1描述
- 功能2描述

### 改进
- 改进1描述

### 修复
- 修复1描述

### 下载
- `ncdocgen.exe` - Windows GUI 可执行程序
- `ncdocgen-cli.exe` - Windows CLI 可执行程序

### 使用说明
1. 下载 `ncdocgen.exe` 或 `ncdocgen-cli.exe`
2. 双击运行 GUI 版本，或在命令行使用 CLI 版本（无需安装）
3. 首次使用请先生成 Key.txt

### 系统要求
- Windows 10/11
- 512MB 内存
- 100MB 磁盘空间

---
**完整更新日志**: [CHANGELOG.md](https://github.com/510850111/ncdocgen/blob/main/docs/CHANGELOG.md)
```

5. 上传文件：将 `dist\ncdocgen.exe` 和 `dist\ncdocgen-cli.exe` 拖放到附件区域
6. 如果是预发布版本，勾选 **This is a pre-release**
7. 点击 **Publish release**

### 方式二：通过 GitHub CLI

```bash
# 创建发布（需要安装 gh）
gh release create v1.0.1 \
  --title "ncdocgen v1.0.1" \
  --notes-file release_notes.md \
  dist\ncdocgen.exe dist\ncdocgen-cli.exe
```

---

## 📢 发布后

### 验证发布

- [ ] Release 页面显示正常：`https://github.com/510850111/ncdocgen/releases`
- [ ] 附件 `ncdocgen.exe` 和 `ncdocgen-cli.exe` 可正常下载
- [ ] 下载的文件能正常运行

### 更新文档

- [ ] 更新 README.md 中的版本号
- [ ] 更新文档中的下载链接

### 通知用户（可选）

- 在相关社区/论坛发布更新公告
- 发送邮件通知关注用户

---

## 🔁 完整发布流程（快速参考）

```bash
# 1. 更新版本号
# 修改 cdocgen.py, gui.py, README.md, docs/CHANGELOG.md

# 2. 提交更改
git add .
git commit -m "chore: 发布 v1.0.1"
git push origin main

# 3. 打包
python build_exe.py

# 4. 测试
dist\ncdocgen.exe        # 测试 GUI
dist\ncdocgen-cli.exe --help  # 测试 CLI

# 5. 打标签
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1

# 6. 创建 GitHub Release（通过 Web 界面或 CLI）
# 上传 dist\ncdocgen.exe 和 dist\ncdocgen-cli.exe
```

---

## ❓ 常见问题

### Q: 打包失败怎么办？

**A:** 
1. 检查 PyInstaller 是否安装：`pip install pyinstaller`
2. 查看错误日志，常见问题：
   - 文件被占用：关闭运行的 ncdocgen.exe 或 ncdocgen-cli.exe
   - 权限问题：以管理员身份运行

### Q: 打包后的 EXE 太大？

**A:**
- 正常现象，单文件 EXE 约 15-20MB
- 包含 Python 运行时、所有依赖、ctags 工具

### Q: 如何发布预发布版本？

**A:**
- 版本号使用 `-alpha`, `-beta` 后缀，如 `v1.1.0-beta`
- 在 GitHub Release 页面勾选 "This is a pre-release"

### Q: 如何修复已发布的版本？

**A:**
- 不建议修改已发布的标签
- 应该发布新版本，如 `v1.0.2` 替代 `v1.0.1`

---

**文档版本**: v1.0  
**更新日期**: 2026-04-04
