#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git版本管理工具
用于创建和管理Git标签，支持语义化版本
"""

import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

class GitVersionTool:
    """Git版本管理工具"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def run_git_command(self, cmd, check=True):
        """运行Git命令"""
        try:
            result = subprocess.run(
                ['git'] + cmd,
                capture_output=True, text=True, check=check, cwd=self.project_root
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Git命令失败: {' '.join(cmd)}")
            print(f"错误: {e.stderr}")
            return None
        except FileNotFoundError:
            print("错误: Git未安装或不在PATH中")
            return None
    
    def get_current_version(self):
        """获取当前版本信息"""
        result = self.run_git_command(['describe', '--tags', '--always', '--dirty'])
        if result and result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def get_all_tags(self):
        """获取所有标签"""
        result = self.run_git_command(['tag', '--list'])
        if result and result.returncode == 0:
            tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
            return sorted(tags, key=self.parse_version)
        return []
    
    def parse_version(self, version_str):
        """解析版本号为可排序的元组"""
        # 移除v前缀
        if version_str.startswith('v'):
            version_str = version_str[1:]
        
        # 分割版本号
        parts = version_str.split('.')
        numeric_parts = []
        
        for part in parts:
            # 处理数字和字母混合的部分
            match = re.match(r'(\d+)([a-zA-Z]*)', part)
            if match:
                numeric_parts.append(int(match.group(1)))
                # 字母部分用于排序（alpha < beta < rc）
                suffix = match.group(2).lower()
                if suffix == 'alpha':
                    numeric_parts.append(1)
                elif suffix == 'beta':
                    numeric_parts.append(2)
                elif suffix == 'rc':
                    numeric_parts.append(3)
                else:
                    numeric_parts.append(0)  # 正式版本
            else:
                numeric_parts.append(0)
        
        # 填充到3位（主版本.次版本.修订版本）
        while len(numeric_parts) < 3:
            numeric_parts.append(0)
        
        return tuple(numeric_parts[:3])
    
    def suggest_next_version(self, bump_type='patch'):
        """建议下一个版本号"""
        current_tags = self.get_all_tags()
        if not current_tags:
            return "v0.1.0"  # 第一个版本
        
        latest_tag = current_tags[-1]
        current_version = latest_tag[1:] if latest_tag.startswith('v') else latest_tag
        
        # 解析当前版本
        parts = current_version.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        
        # 根据bump类型递增版本
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"v{major}.{minor}.{patch}"
    
    def create_tag(self, tag_name, message=None, force=False):
        """创建Git标签"""
        if not message:
            message = f"Release {tag_name}"
        
        cmd = ['tag', '-a', tag_name, '-m', message]
        if force:
            cmd.append('-f')
        
        result = self.run_git_command(cmd)
        if result and result.returncode == 0:
            print(f"✓ 标签创建成功: {tag_name}")
            return True
        return False
    
    def push_tags(self):
        """推送标签到远程仓库"""
        result = self.run_git_command(['push', '--tags'])
        if result and result.returncode == 0:
            print("✓ 标签推送成功")
            return True
        return False
    
    def show_status(self):
        """显示当前版本状态"""
        current_version = self.get_current_version()
        tags = self.get_all_tags()
        
        print("=" * 60)
        print("Git版本状态")
        print("=" * 60)
        print(f"当前版本: {current_version or '无标签'}")
        print(f"标签数量: {len(tags)}")
        
        if tags:
            print("\n所有标签:")
            for tag in tags[-10:]:  # 显示最近10个标签
                print(f"  - {tag}")
        
        # 显示建议的下一个版本
        for bump_type in ['patch', 'minor', 'major']:
            suggested = self.suggest_next_version(bump_type)
            print(f"建议{bump_type}版本: {suggested}")
        
        # 检查是否有未提交的更改
        status_result = self.run_git_command(['status', '--porcelain'])
        if status_result and status_result.stdout.strip():
            print("\n⚠️  有未提交的更改")
        else:
            print("\n✓ 工作区干净")
    
    def interactive_create_tag(self):
        """交互式创建标签"""
        self.show_status()
        
        print("\n请选择版本增量类型:")
        print("1. patch (修订版本，向后兼容的bug修复)")
        print("2. minor (次版本，向后兼容的新功能)")
        print("3. major (主版本，不兼容的API修改)")
        print("4. 自定义版本号")
        
        choice = input("请输入选项 (1-4): ").strip()
        
        if choice == '1':
            tag_name = self.suggest_next_version('patch')
        elif choice == '2':
            tag_name = self.suggest_next_version('minor')
        elif choice == '3':
            tag_name = self.suggest_next_version('major')
        elif choice == '4':
            tag_name = input("请输入自定义版本号 (例如 v1.2.3): ").strip()
            if not tag_name.startswith('v'):
                tag_name = 'v' + tag_name
        else:
            print("无效选项")
            return False
        
        message = input(f"请输入发布说明 (默认: Release {tag_name}): ").strip()
        if not message:
            message = f"Release {tag_name}"
        
        # 确认创建
        confirm = input(f"确认创建标签 {tag_name}? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("取消操作")
            return False
        
        if self.create_tag(tag_name, message):
            # 询问是否推送
            push_confirm = input("是否推送标签到远程仓库? (y/n): ").strip().lower()
            if push_confirm in ['y', 'yes']:
                self.push_tags()
            return True
        
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git版本管理工具")
    parser.add_argument("--status", action="store_true", help="显示版本状态")
    parser.add_argument("--create", action="store_true", help="交互式创建标签")
    parser.add_argument("--tag", type=str, help="创建指定标签")
    parser.add_argument("--message", type=str, help="标签说明")
    parser.add_argument("--push", action="store_true", help="推送标签")
    parser.add_argument("--suggest", choices=['patch', 'minor', 'major'], 
                       help="建议下一个版本号")
    
    args = parser.parse_args()
    
    tool = GitVersionTool()
    
    if args.status:
        tool.show_status()
    elif args.suggest:
        suggested = tool.suggest_next_version(args.suggest)
        print(f"建议{args.suggest}版本: {suggested}")
    elif args.tag:
        success = tool.create_tag(args.tag, args.message)
        if success and args.push:
            tool.push_tags()
    elif args.create:
        tool.interactive_create_tag()
    elif args.push:
        tool.push_tags()
    else:
        # 默认显示状态
        tool.show_status()

if __name__ == "__main__":
    main()
