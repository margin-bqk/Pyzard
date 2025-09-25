# Pyzard 构建系统说明

## 概述

本构建系统使用 PyInstaller 的 `--onefile` 模式，自动生成名为 `Pyzard_{版本号}.exe` 的可执行文件。

## 文件结构

```
项目根目录/
├── version.py          # 版本信息文件
├── Pyzard.spec         # PyInstaller 配置文件 (已配置onefile模式)
├── build.py            # Python构建脚本
├── build.bat           # Windows批处理构建脚本
├── test_build_system.py # 构建系统测试脚本
└── BUILD_README.md     # 本说明文档
```

## 构建方法

### 方法1: 使用批处理文件 (推荐Windows用户)

双击运行 `build.bat` 文件，或使用命令行：

```cmd
.\build.bat
```

批处理文件提供以下选项：
1. **完整构建** - 清理并重新构建
2. **增量构建** - 不清理构建目录
3. **显示构建信息** - 查看当前配置
4. **退出**

### 方法2: 使用Python脚本

```bash
# 完整构建
python build.py

# 增量构建 (不清理构建目录)
python build.py --no-clean

# 显示构建信息
python build.py --info

# 显示版本信息
python build.py --version
```

## 输出文件

构建完成后，可执行文件将生成在 `dist/` 目录中：
- `Pyzard_1.0.0.exe` (根据版本号命名)
- `build_info.json` (构建信息文件)

## 版本管理（基于Git标签）

### 自动版本检测

构建系统现在优先使用Git标签来自动确定版本号：

- **格式**: `{最新标签}-{提交数}-g{提交哈希}` (例如: `0.0.2-2-g2489c7a`)
- **无标签时**: 使用 `0.0.0-dev` 作为默认版本
- **工作区脏时**: 自动添加 `-dirty` 后缀

### Git版本管理工具

使用 `git_version_tool.py` 管理版本：

```bash
# 显示当前版本状态
python git_version_tool.py --status

# 建议下一个版本号
python git_version_tool.py --suggest patch
python git_version_tool.py --suggest minor  
python git_version_tool.py --suggest major

# 交互式创建标签
python git_version_tool.py --create

# 创建指定标签
python git_version_tool.py --tag v1.2.3 --message "重要更新"

# 推送标签到远程仓库
python git_version_tool.py --push
```

### 版本命名规范

建议使用语义化版本规范：
- **主版本 (major)**: 不兼容的API修改
- **次版本 (minor)**: 向后兼容的新功能
- **修订版本 (patch)**: 向后兼容的bug修复

示例：`v1.2.3`

## 构建配置

### PyInstaller 配置 (Pyzard.spec)

- **onefile模式**: 启用，生成单个可执行文件
- **控制台模式**: 启用，显示命令行界面
- **UPX压缩**: 启用，减小文件大小
- **版本命名**: 自动包含版本号

### 自定义配置

如需修改构建配置，可以编辑 `Pyzard.spec` 文件：

```python
# 修改图标
icon='path/to/icon.ico'

# 修改控制台模式
console=False  # 改为False创建无控制台窗口程序

# 添加数据文件
datas=[('data/*', 'data')]
```

## 测试构建系统

运行测试脚本验证构建系统功能：

```bash
python test_build_system.py
```

## 常见问题

### 1. PyInstaller 未安装

构建脚本会自动检查并提示安装：

```bash
pip install pyinstaller
```

### 2. 构建失败

检查以下项目：
- Python 环境是否正常
- 项目文件是否完整
- 磁盘空间是否充足

### 3. 文件大小过大

这是正常的，因为 onefile 模式会将所有依赖打包到一个文件中。可以使用 UPX 压缩来减小文件大小。

## 技术支持

如果遇到问题，请检查：
1. 错误信息输出
2. 构建日志文件
3. PyInstaller 文档

构建成功后，可执行文件即可独立运行，无需Python环境。
