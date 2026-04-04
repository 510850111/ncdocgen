# 贡献指南

感谢您对 ncdocgen 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请通过 [Issue](../../issues) 提交。

提交Issue时请包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 系统环境（Windows版本、Python版本等）
- 相关代码片段或截图

### 提交代码

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 代码规范

- 遵循 PEP 8 Python 编码规范
- 添加适当的代码注释
- 确保代码能在 Windows 10/11 上正常运行
- 不要破坏向后兼容性

### 开发流程

```bash
# 克隆仓库
git clone https://github.com/[你的用户名]/ncdocgen.git
cd ncdocgen

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m ncdocgen

# 打包测试
python build_exe.py
```

## 联系方式

如有疑问，请联系：hekuan_oscar@qq.com
