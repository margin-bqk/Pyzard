# Pyzard 测试使用说明

## 概述

本文档介绍如何使用 Pyzard 的综合测试脚本和 VSCode 调试配置来验证程序功能。

## 测试脚本功能

### 测试模式

测试脚本支持多种测试模式：

- **完整测试** (`--full`)：运行所有功能测试（默认模式）
- **快速测试** (`--quick`)：只运行核心功能测试
- **编码测试** (`--encoding`)：专门测试编码处理功能
- **性能测试** (`--performance`)：性能基准测试

### 命令行使用

```bash
# 完整测试（默认）
python test_pyzard_comprehensive.py

# 快速测试
python test_pyzard_comprehensive.py --quick

# 编码测试
python test_pyzard_comprehensive.py --encoding

# 性能测试
python test_pyzard_comprehensive.py --performance

# 生成HTML报告
python test_pyzard_comprehensive.py --report test_report.html

# 测试后清理临时文件
python test_pyzard_comprehensive.py --clean
```

## VSCode 调试配置

### 配置说明

项目包含 `.vscode/launch.json` 配置文件，提供以下调试配置：

1. **Pyzard 完整测试** - 运行所有功能测试
2. **Pyzard 快速测试** - 运行核心功能测试  
3. **Pyzard 编码测试** - 专门测试编码处理
4. **Pyzard 性能测试** - 性能基准测试
5. **运行 Pyzard 主程序** - 直接运行主程序

### 使用方法

1. 打开 VSCode
2. 切换到调试面板（Ctrl+Shift+D）
3. 选择相应的测试配置
4. 点击运行按钮或按 F5

### 快捷键

- `F5`：启动当前选中的调试配置
- `Ctrl+F5`：运行但不调试
- `Shift+F5`：停止调试

## 测试环境规范

### 临时文件命名

测试脚本使用规范化的临时文件命名：

- 测试目录：`pyzard_test_YYYYMMDD_HHMMSS_*`
- CSV文件：`test_[功能]_[编码].csv`
- 报告文件：`test_report_YYYYMMDD_HHMMSS.html`

### Gitignore 配置

以下文件已被添加到 `.gitignore`：

```
# Pyzard测试相关
.pyzard_test_*/
test_*.csv
test_report_*.html
.pyzard_history.json
.pyzard_backup/
.temp_backup/

# VSCode配置（可选保留）
# .vscode/launch.json
# .vscode/tasks.json
# .vscode/settings.json
```

## 测试覆盖范围

### 核心功能测试

1. **CSV编码检测**
   - UTF-8 with BOM
   - GBK 编码
   - UTF-8 无 BOM

2. **文件操作功能**
   - 文件搜索复制
   - 文件重命名（原地）
   - 文件夹提取
   - CSV路径复制

3. **冲突处理**
   - 创建副本模式
   - 文件冲突检测

4. **错误处理**
   - 文件不存在处理
   - 空文件处理

### 测试报告

测试完成后会生成详细报告，包括：
- 测试用例执行结果
- 执行时间统计
- 通过率分析
- 错误信息（如有）

## 开发工作流

### 日常开发测试

```bash
# 快速验证核心功能
python test_pyzard_comprehensive.py --quick

# 或在VSCode中运行"Pyzard 快速测试"配置
```

### 版本发布测试

```bash
# 完整功能验证
python test_pyzard_comprehensive.py --full

# 生成测试报告
python test_pyzard_comprehensive.py --full --report release_test.html
```

### 编码问题排查

```bash
# 专门测试编码处理
python test_pyzard_comprehensive.py --encoding
```

## 故障排除

### 常见问题

1. **导入错误**
   - 确保 `PYTHONPATH` 包含项目根目录
   - 检查 `Pyzard.py` 文件是否存在

2. **权限错误**
   - 确保有足够的文件操作权限
   - 检查临时目录是否可写

3. **编码错误**
   - 测试脚本会自动处理各种编码
   - 如仍有问题，使用 `--encoding` 模式专门测试

### 调试技巧

1. **使用 VSCode 断点**
   - 在测试脚本中设置断点
   - 使用调试模式运行

2. **查看详细日志**
   - 测试脚本会输出详细的操作日志
   - 关注警告和错误信息

3. **检查临时文件**
   - 测试目录会在测试完成后自动清理
   - 如需保留，可注释清理代码

## 扩展开发

### 添加新测试用例

1. 在 `PyzardTester` 类中添加新的测试方法
2. 在 `run_all_tests()` 方法中注册测试用例
3. 更新命令行参数解析（如需要）

### 自定义测试配置

修改 `.vscode/launch.json` 可以：
- 添加新的调试配置
- 调整环境变量
- 修改启动参数

## 版本历史

- **v1.0** - 初始版本，包含完整测试功能
- **v1.1** - 添加 VSCode 调试配置
- **v1.2** - 规范化测试环境命名

## 联系方式

如有问题或建议，请参考项目文档或联系开发团队。
