#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建系统测试脚本
测试构建系统的各个组件是否正常工作
"""

import os
import sys
from pathlib import Path

def test_version_module():
    """测试版本模块"""
    print("测试版本模块...")
    try:
        from version import get_version, get_version_info
        version = get_version()
        info = get_version_info()
        
        print(f"✓ 版本号: {version}")
        print(f"✓ 版本信息: {info}")
        return True
    except Exception as e:
        print(f"✗ 版本模块测试失败: {e}")
        return False

def test_spec_file():
    """测试spec文件"""
    print("测试spec文件...")
    try:
        spec_file = Path("Pyzard.spec")
        if not spec_file.exists():
            print("✗ spec文件不存在")
            return False
            
        content = spec_file.read_text(encoding='utf-8')
        if 'onefile=True' in content:
            print("✓ spec文件包含onefile模式配置")
        else:
            print("✗ spec文件缺少onefile模式配置")
            return False
            
        if 'Pyzard_' in content:
            print("✓ spec文件包含版本号命名")
        else:
            print("✗ spec文件缺少版本号命名")
            return False
            
        return True
    except Exception as e:
        print(f"✗ spec文件测试失败: {e}")
        return False

def test_build_script():
    """测试构建脚本"""
    print("测试构建脚本...")
    try:
        build_file = Path("build.py")
        if not build_file.exists():
            print("✗ 构建脚本不存在")
            return False
            
        # 测试构建脚本的基本功能
        import subprocess
        result = subprocess.run([sys.executable, "build.py", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and "Pyzard版本:" in result.stdout:
            print("✓ 构建脚本版本检查功能正常")
        else:
            print("✗ 构建脚本版本检查功能异常")
            return False
            
        # 测试信息显示功能
        result = subprocess.run([sys.executable, "build.py", "--info"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and "Pyzard 构建工具" in result.stdout:
            print("✓ 构建脚本信息显示功能正常")
        else:
            print("✗ 构建脚本信息显示功能异常")
            return False
            
        return True
    except Exception as e:
        print(f"✗ 构建脚本测试失败: {e}")
        return False

def test_batch_script():
    """测试批处理脚本"""
    print("测试批处理脚本...")
    try:
        batch_file = Path("build.bat")
        if not batch_file.exists():
            print("✗ 批处理脚本不存在")
            return False
            
        # 检查批处理脚本内容
        content = batch_file.read_text(encoding='utf-8')
        if 'Pyzard 构建工具' in content:
            print("✓ 批处理脚本包含正确的标题")
        else:
            print("✗ 批处理脚本标题不正确")
            return False
            
        if 'python build.py' in content:
            print("✓ 批处理脚本包含Python调用")
        else:
            print("✗ 批处理脚本缺少Python调用")
            return False
            
        return True
    except Exception as e:
        print(f"✗ 批处理脚本测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Pyzard构建系统测试")
    print("=" * 60)
    
    tests = [
        test_version_module,
        test_spec_file,
        test_build_script,
        test_batch_script
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! 构建系统准备就绪。")
        print("\n使用方法:")
        print("1. 使用 build.bat (Windows批处理文件)")
        print("2. 使用 python build.py (Python脚本)")
        print("3. 使用 python build.py --info 查看构建信息")
        print("4. 使用 python build.py --no-clean 进行增量构建")
    else:
        print("⚠️ 部分测试失败，请检查构建系统配置。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
