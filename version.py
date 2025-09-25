# 版本信息文件
import subprocess
import sys
from pathlib import Path

__author__ = "Pyzard Team"
__description__ = "文件管理和提取工具"

def get_git_version():
    """从Git标签获取版本信息"""
    try:
        # 使用git describe获取版本信息
        result = subprocess.run(
            ['git', 'describe', '--tags', '--always', '--dirty'],
            capture_output=True, text=True, check=True, cwd=Path(__file__).parent
        )
        git_version = result.stdout.strip()
        
        # 如果没有标签，git describe会返回提交哈希
        if git_version and not git_version.startswith('fatal:'):
            return git_version
        else:
            return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git不可用或命令失败
        return None

def get_version():
    """获取版本信息，优先使用Git标签"""
    git_version = get_git_version()
    if git_version:
        return git_version
    else:
        # 回退到固定版本
        return "0.0.0-dev"

def get_version_info():
    """获取完整的版本信息"""
    git_version = get_git_version()
    
    version_info = {
        "version": git_version if git_version else "0.0.0-dev",
        "author": __author__,
        "description": __description__,
        "source": "git" if git_version else "fixed"
    }
    
    # 添加Git详细信息（如果可用）
    if git_version:
        try:
            # 获取提交哈希
            commit_hash = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True, text=True, check=True, cwd=Path(__file__).parent
            ).stdout.strip()
            
            # 获取提交时间
            commit_date = subprocess.run(
                ['git', 'log', '-1', '--format=%cd', '--date=short'],
                capture_output=True, text=True, check=True, cwd=Path(__file__).parent
            ).stdout.strip()
            
            version_info["commit_hash"] = commit_hash
            version_info["commit_date"] = commit_date
            version_info["is_dirty"] = str("-dirty" in git_version)
        except:
            pass
    
    return version_info

if __name__ == "__main__":
    print(f"Pyzard版本: {get_version()}")
    print(f"作者: {__author__}")
    print(f"描述: {__description__}")
