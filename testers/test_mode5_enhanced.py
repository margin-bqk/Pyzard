#!/usr/bin/env python3
"""
测试改进后的模式5功能：从CSV路径复制文件/文件夹到目标路径
测试新的路径类型识别和冲突解决机制
"""

import os
import shutil
import csv
import tempfile
import sys

# 添加当前目录到Python路径，以便导入Pyzard模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Pyzard import (
    copy_files_from_csv_paths,
    identify_path_type,
    build_final_target_path,
    resolve_conflict,
    CONFLICT_MODES
)


def create_test_environment():
    """创建测试环境"""
    test_dir = tempfile.mkdtemp(prefix="pyzard_test_")
    print(f"创建测试目录: {test_dir}")
    
    # 创建源目录结构
    source_dir = os.path.join(test_dir, "source")
    os.makedirs(source_dir)
    
    # 创建目标目录
    target_dir = os.path.join(test_dir, "target")
    os.makedirs(target_dir)
    
    # 创建测试文件
    test_files = [
        "file1.txt",
        "document.pdf",
        "image.jpg"
    ]
    
    for file in test_files:
        file_path = os.path.join(source_dir, file)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文件: {file}")
    
    # 创建测试文件夹
    test_folders = [
        "folder1",
        "folder2",
        "subfolder"
    ]
    
    for folder in test_folders:
        folder_path = os.path.join(source_dir, folder)
        os.makedirs(folder_path)
        
        # 在文件夹中创建一些文件
        for i in range(2):
            sub_file = os.path.join(folder_path, f"subfile_{i}.txt")
            with open(sub_file, 'w', encoding='utf-8') as f:
                f.write(f"子文件夹 {folder} 中的文件 {i}")
    
    return test_dir, source_dir, target_dir


def test_path_type_identification():
    """测试路径类型识别功能"""
    print("\n=== 测试路径类型识别 ===")
    
    test_cases = [
        ("D:\\target\\", "directory"),  # 明确目录
        ("D:\\target", "directory"),    # 推断为目录
        ("D:\\file.txt", "file"),       # 有扩展名
        ("D:\\file", "directory"),      # 无扩展名
        ("D:\\folder\\subfolder", "directory"),  # 多级路径
    ]
    
    for path, expected in test_cases:
        result = identify_path_type(path)
        status = "✓" if result == expected else "✗"
        print(f"{status} {path} -> {result} (期望: {expected})")


def test_build_final_target_path():
    """测试目标路径构建功能"""
    print("\n=== 测试目标路径构建 ===")
    
    test_cases = [
        # (源路径, 目标路径, 期望结果模式)
        ("D:\\source\\file.txt", "D:\\target\\", "file_to_dir"),
        ("D:\\source\\file.txt", "D:\\target\\new.txt", "file_to_file"),
        ("D:\\source\\folder", "D:\\target\\", "folder_to_dir"),
        ("D:\\source\\folder", "D:\\target\\newfolder", "folder_to_folder"),
    ]
    
    for source, target, expected_mode in test_cases:
        result = build_final_target_path(source, target, "copy")
        print(f"源: {source}")
        print(f"目标: {target}")
        print(f"结果: {result}")
        print(f"模式: {expected_mode}")
        print("-" * 50)


def test_csv_scenarios():
    """测试各种CSV场景"""
    print("\n=== 测试CSV场景 ===")
    
    test_dir, source_dir, target_dir = create_test_environment()
    
    try:
        # 场景1: 文件复制到目录
        csv_file1 = os.path.join(test_dir, "scenario1.csv")
        with open(csv_file1, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([os.path.join(source_dir, "file1.txt"), target_dir + "\\"])
            writer.writerow([os.path.join(source_dir, "document.pdf"), target_dir + "\\"])
        
        print(f"\n场景1: 文件复制到目录")
        print(f"CSV文件: {csv_file1}")
        result1 = copy_files_from_csv_paths(csv_file1, cut_mode=False, conflict_mode="copy")
        print(f"结果: {len(result1)} 个文件已复制")
        
        # 场景2: 文件复制并重命名
        csv_file2 = os.path.join(test_dir, "scenario2.csv")
        with open(csv_file2, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([os.path.join(source_dir, "file1.txt"), os.path.join(target_dir, "renamed_file.txt")])
        
        print(f"\n场景2: 文件复制并重命名")
        print(f"CSV文件: {csv_file2}")
        result2 = copy_files_from_csv_paths(csv_file2, cut_mode=False, conflict_mode="copy")
        print(f"结果: {len(result2)} 个文件已复制")
        
        # 场景3: 文件夹复制到目录
        csv_file3 = os.path.join(test_dir, "scenario3.csv")
        with open(csv_file3, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([os.path.join(source_dir, "folder1"), target_dir + "\\"])
        
        print(f"\n场景3: 文件夹复制到目录")
        print(f"CSV文件: {csv_file3}")
        result3 = copy_files_from_csv_paths(csv_file3, cut_mode=False, conflict_mode="copy")
        print(f"结果: {len(result3)} 个文件夹已复制")
        
        # 场景4: 文件夹复制并重命名
        csv_file4 = os.path.join(test_dir, "scenario4.csv")
        with open(csv_file4, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([os.path.join(source_dir, "folder2"), os.path.join(target_dir, "renamed_folder")])
        
        print(f"\n场景4: 文件夹复制并重命名")
        print(f"CSV文件: {csv_file4}")
        result4 = copy_files_from_csv_paths(csv_file4, cut_mode=False, conflict_mode="copy")
        print(f"结果: {len(result4)} 个文件夹已复制")
        
        # 场景5: 混合场景
        csv_file5 = os.path.join(test_dir, "scenario5.csv")
        with open(csv_file5, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([os.path.join(source_dir, "image.jpg"), target_dir + "\\"])
            writer.writerow([os.path.join(source_dir, "subfolder"), os.path.join(target_dir, "custom_subfolder")])
        
        print(f"\n场景5: 混合场景（文件+文件夹）")
        print(f"CSV文件: {csv_file5}")
        result5 = copy_files_from_csv_paths(csv_file5, cut_mode=False, conflict_mode="copy")
        print(f"结果: {len(result5)} 个项目已复制")
        
        # 验证结果
        print(f"\n=== 验证结果 ===")
        print(f"目标目录内容:")
        for root, dirs, files in os.walk(target_dir):
            level = root.replace(target_dir, '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = '  ' * (level + 1)
            for file in files:
                print(f"{sub_indent}{file}")
        
    finally:
        # 清理测试环境
        shutil.rmtree(test_dir)
        print(f"\n清理测试目录: {test_dir}")


def test_conflict_resolution():
    """测试冲突解决机制"""
    print("\n=== 测试冲突解决机制 ===")
    
    test_dir, source_dir, target_dir = create_test_environment()
    
    try:
        # 先复制一个文件到目标目录
        source_file = os.path.join(source_dir, "file1.txt")
        target_file = os.path.join(target_dir, "file1.txt")
        shutil.copy2(source_file, target_file)
        
        # 测试各种冲突解决模式
        for mode_name, mode_desc in CONFLICT_MODES.items():
            print(f"\n测试冲突模式: {mode_name} ({mode_desc})")
            
            csv_file = os.path.join(test_dir, f"conflict_{mode_name}.csv")
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([source_file, target_dir + "\\"])
            
            result = copy_files_from_csv_paths(csv_file, cut_mode=False, conflict_mode=mode_name)
            print(f"结果: {len(result)} 个文件已处理")
            
            # 重置目标文件
            shutil.copy2(source_file, target_file)
    
    finally:
        shutil.rmtree(test_dir)
        print(f"\n清理测试目录: {test_dir}")


def main():
    """主测试函数"""
    print("开始测试改进后的模式5功能")
    print("=" * 60)
    
    # 测试路径类型识别
    test_path_type_identification()
    
    # 测试目标路径构建
    test_build_final_target_path()
    
    # 测试CSV场景
    test_csv_scenarios()
    
    # 测试冲突解决
    test_conflict_resolution()
    
    print("\n" + "=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    main()
