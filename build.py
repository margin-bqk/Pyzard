#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyzard构建脚本
使用pyinstaller --onefile模式构建可执行文件
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# 导入版本信息
try:
    from version import get_version
except ImportError:
    print("警告: 无法导入version模块，使用默认版本号")
    def get_version() -> str:
        return "1.0.0"

class PyzardBuilder:
    """Pyzard构建器"""
    
    def __init__(self):
        self.version = get_version()
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.spec_file = self.project_root / "Pyzard.spec"
        self.exe_name = f"Pyzard_{self.version}.exe"
        
    def print_header(self):
        """打印构建头信息"""
        print("=" * 60)
        print(f"Pyzard 构建工具")
        print(f"版本: {self.version}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    def check_environment(self):
        """检查构建环境"""
        print("检查构建环境...")
        
        # 检查Python环境
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查PyInstaller是否安装
        try:
            import PyInstaller
            print(f"PyInstaller版本: {PyInstaller.__version__}")
        except ImportError:
            print("错误: PyInstaller未安装，请运行: pip install pyinstaller")
            return False
            
        # 检查spec文件是否存在
        if not self.spec_file.exists():
            print(f"错误: spec文件不存在: {self.spec_file}")
            return False
            
        # 检查主程序文件是否存在
        main_file = self.project_root / "Pyzard.py"
        if not main_file.exists():
            print(f"错误: 主程序文件不存在: {main_file}")
            return False
            
        print("✓ 环境检查通过")
        return True
        
    def clean_build_dirs(self):
        """清理构建目录"""
        print("清理构建目录...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    print(f"✓ 已清理: {dir_path}")
                except Exception as e:
                    print(f"警告: 清理失败 {dir_path}: {e}")
            else:
                print(f"✓ 目录不存在: {dir_path}")
                
    def run_pyinstaller(self):
        """运行PyInstaller构建"""
        print("开始构建可执行文件...")
        
        try:
            # 使用spec文件构建
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(self.spec_file)
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ PyInstaller构建成功")
                return True
            else:
                print(f"错误: PyInstaller构建失败")
                print(f"标准输出: {result.stdout}")
                print(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"错误: PyInstaller进程异常: {e}")
            print(f"标准输出: {e.stdout}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"错误: 执行PyInstaller时发生异常: {e}")
            return False
            
    def verify_output(self):
        """验证输出文件"""
        print("验证输出文件...")
        
        # 处理Git版本号中的特殊字符（如连字符）
        # Git版本格式可能包含连字符，需要替换为下划线或其他合法字符
        safe_version = self.version.replace('-', '_').replace('.', '_')
        
        # 检查dist目录中的文件
        expected_exe = self.dist_dir / f"Pyzard_{safe_version}.exe"
        
        # 同时检查原始版本命名的文件（兼容性）
        original_exe = self.dist_dir / f"Pyzard_{self.version}.exe"
        
        exe_file = None
        if expected_exe.exists():
            exe_file = expected_exe
        elif original_exe.exists():
            exe_file = original_exe
            print(f"注意: 使用原始版本命名: {original_exe.name}")
        
        if exe_file and exe_file.exists():
            file_size = exe_file.stat().st_size
            print(f"✓ 可执行文件已生成: {exe_file}")
            print(f"✓ 文件大小: {file_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print(f"错误: 预期文件不存在: {expected_exe}")
            print(f"备选文件: {original_exe}")
            
            # 列出dist目录中的所有文件
            if self.dist_dir.exists():
                files = list(self.dist_dir.glob("Pyzard_*.exe"))
                if files:
                    print("dist目录中的Pyzard文件:")
                    for file in files:
                        print(f"  - {file.name}")
                else:
                    files = list(self.dist_dir.glob("*"))
                    if files:
                        print("dist目录中的文件:")
                        for file in files:
                            print(f"  - {file.name}")
                    else:
                        print("dist目录为空")
                    
            return False
            
    def create_build_info(self):
        """创建构建信息文件"""
        print("创建构建信息...")
        
        build_info = {
            "project": "Pyzard",
            "version": self.version,
            "build_time": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "build_mode": "onefile"
        }
        
        info_file = self.dist_dir / "build_info.json"
        try:
            import json
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(build_info, f, indent=2, ensure_ascii=False)
            print(f"✓ 构建信息已保存: {info_file}")
        except Exception as e:
            print(f"警告: 无法保存构建信息: {e}")
            
    def build(self, clean=True):
        """执行完整构建流程"""
        self.print_header()
        
        # 检查环境
        if not self.check_environment():
            return False
            
        # 清理构建目录
        if clean:
            self.clean_build_dirs()
            
        # 运行PyInstaller
        if not self.run_pyinstaller():
            return False
            
        # 验证输出
        if not self.verify_output():
            return False
            
        # 创建构建信息
        self.create_build_info()
        
        print("\n" + "=" * 60)
        print("🎉 构建完成!")
        print(f"可执行文件位置: {self.dist_dir / self.exe_name}")
        print("=" * 60)
        return True
        
    def show_info(self):
        """显示构建信息"""
        self.print_header()
        print("构建配置:")
        print(f"  项目根目录: {self.project_root}")
        print(f"  构建目录: {self.build_dir}")
        print(f"  输出目录: {self.dist_dir}")
        print(f"  Spec文件: {self.spec_file}")
        print(f"  输出文件名: {self.exe_name}")
        print(f"  版本号: {self.version}")
        
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Pyzard构建工具")
    parser.add_argument("--no-clean", action="store_true", 
                       help="不清理构建目录（增量构建）")
    parser.add_argument("--info", action="store_true",
                       help="显示构建信息")
    parser.add_argument("--version", action="store_true",
                       help="显示版本信息")
    
    args = parser.parse_args()
    
    builder = PyzardBuilder()
    
    if args.version:
        print(f"Pyzard版本: {builder.version}")
        return
        
    if args.info:
        builder.show_info()
        return
        
    # 执行构建
    success = builder.build(clean=not args.no_clean)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
