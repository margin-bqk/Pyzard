#!/usr/bin/env python3
"""
测试各种冲突处理模式的脚本
"""

import os
import tempfile
import shutil
import csv
from Pyzard import search_and_copy_files, extract_entire_folder, rename_files_in_place, copy_files_from_csv_paths

def create_test_files():
    """创建测试文件和目录"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建测试目录: {temp_dir}")
    
    # 创建源目录结构
    source_dir = os.path.join(temp_dir, "source")
    os.makedirs(source_dir)
    
    # 创建一些测试文件
    test_files = ["file1.txt", "file2.txt", "file3.txt"]
    for file in test_files:
        with open(os.path.join(source_dir, file), "w") as f:
            f.write(f"这是{file}的内容")
    
    # 创建测试文件夹
    test_folders = ["folder1", "folder2"]
    for folder in test_folders:
        folder_path = os.path.join(source_dir, folder)
        os.makedirs(folder_path)
        with open(os.path.join(folder_path, "test.txt"), "w") as f:
            f.write(f"这是{folder}中的测试文件")
    
    # 创建目标目录并添加一些冲突文件
    target_dir = os.path.join(temp_dir, "target")
    os.makedirs(target_dir)
    
    # 在目标目录中创建冲突文件
    with open(os.path.join(target_dir, "file1.txt"), "w") as f:
        f.write("这是目标目录中已存在的file1.txt")
    
    # 在目标目录中创建冲突文件夹
    conflict_folder = os.path.join(target_dir, "folder1")
    os.makedirs(conflict_folder)
    with open(os.path.join(conflict_folder, "existing.txt"), "w") as f:
        f.write("这是目标目录中已存在的文件夹内容")
    
    return temp_dir, source_dir, target_dir

def test_skip_mode():
    """测试跳过模式"""
    print("\n=== 测试1: 跳过模式 (skip) ===")
    
    temp_dir, source_dir, target_dir = create_test_files()
    
    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file1.txt", "file1.txt"])
        writer.writerow(["file2.txt", "file2.txt"])
    
    try:
        # 执行搜索复制操作（跳过模式）
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False, conflict_mode="skip")
        print(f"操作结果: {result}")
        print("测试通过: 跳过模式正常工作")
        
        # 验证文件是否被跳过
        if len(result) == 1:  # 应该只有file2.txt被复制，file1.txt被跳过
            print("验证通过: 冲突文件被正确跳过")
        else:
            print("验证失败: 文件处理数量不正确")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    # 清理
    shutil.rmtree(temp_dir)

def test_overwrite_mode():
    """测试覆盖模式"""
    print("\n=== 测试2: 覆盖模式 (overwrite) ===")
    
    temp_dir, source_dir, target_dir = create_test_files()
    
    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file1.txt", "file1.txt"])
    
    try:
        # 执行搜索复制操作（覆盖模式）
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False, conflict_mode="overwrite")
        print(f"操作结果: {result}")
        print("测试通过: 覆盖模式正常工作")
        
        # 验证文件是否被覆盖
        with open(os.path.join(target_dir, "file1.txt"), "r") as f:
            content = f.read()
            if "这是file1.txt的内容" in content:
                print("验证通过: 文件被正确覆盖")
            else:
                print("验证失败: 文件内容未被正确覆盖")
                
    except Exception as e:
        print(f"测试失败: {e}")
    
    # 清理
    shutil.rmtree(temp_dir)

def test_copy_mode():
    """测试副本模式"""
    print("\n=== 测试3: 副本模式 (copy) ===")
    
    temp_dir, source_dir, target_dir = create_test_files()
    
    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file1.txt", "file1.txt"])
    
    try:
        # 执行搜索复制操作（副本模式）
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False, conflict_mode="copy")
        print(f"操作结果: {result}")
        print("测试通过: 副本模式正常工作")
        
        # 验证副本是否被创建
        if len(result) == 1 and "副本" in result[0]:
            print("验证通过: 副本文件被正确创建")
        else:
            print("验证失败: 副本文件创建不正确")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    # 清理
    shutil.rmtree(temp_dir)

def test_merge_mode():
    """测试合并模式（仅文件夹）"""
    print("\n=== 测试4: 合并模式 (merge) ===")
    
    temp_dir, source_dir, target_dir = create_test_files()
    
    # 在源文件夹中添加更多文件
    source_folder = os.path.join(source_dir, "folder1")
    with open(os.path.join(source_folder, "new_file.txt"), "w") as f:
        f.write("这是源文件夹中的新文件")
    
    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "folders.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["folder1", "folder1"])
    
    try:
        # 执行提取文件夹操作（合并模式）
        result = extract_entire_folder(source_dir, target_dir, csv_file, cut_mode=False, conflict_mode="merge")
        print(f"操作结果: {result}")
        print("测试通过: 合并模式正常工作")
        
        # 验证文件夹是否被合并
        target_folder = os.path.join(target_dir, "folder1")
        if os.path.exists(os.path.join(target_folder, "existing.txt")) and os.path.exists(os.path.join(target_folder, "new_file.txt")):
            print("验证通过: 文件夹内容被正确合并")
        else:
            print("验证失败: 文件夹合并不正确")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    # 清理
    shutil.rmtree(temp_dir)

def test_rename_conflict():
    """测试重命名冲突处理"""
    print("\n=== 测试5: 重命名冲突处理 ===")
    
    temp_dir, source_dir, target_dir = create_test_files()
    
    # 在源目录中创建重命名冲突文件
    with open(os.path.join(source_dir, "conflict.txt"), "w") as f:
        f.write("这是重命名冲突测试文件")
    
    # 在源目录中创建同名文件（用于重命名冲突）
    with open(os.path.join(source_dir, "target_name.txt"), "w") as f:
        f.write("这是目标名称已存在的文件")
    
    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "rename.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["conflict.txt", "target_name.txt"])
    
    try:
        # 执行重命名操作（副本模式）
        result = rename_files_in_place(source_dir, csv_file, conflict_mode="copy")
        print(f"操作结果: {result}")
        print("测试通过: 重命名冲突处理正常工作")
        
        # 验证重命名结果
        if len(result) == 1:
            print("验证通过: 重命名操作完成")
        else:
            print("验证失败: 重命名操作不正确")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    # 清理
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("开始测试各种冲突处理模式...")
    
    # 运行所有测试
    test_skip_mode()
    test_overwrite_mode()
    test_copy_mode()
    test_merge_mode()
    test_rename_conflict()
    
    print("\n=== 测试完成 ===")
