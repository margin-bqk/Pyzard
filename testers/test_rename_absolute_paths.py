#!/usr/bin/env python3
"""
测试改进后的 rename_files_in_place 函数
支持绝对路径-绝对路径形式，处理源路径重复的情况
"""

import os
import tempfile
import shutil
from Pyzard import rename_files_in_place

def create_test_files():
    """创建测试文件和目录结构"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建测试目录: {temp_dir}")
    
    # 创建测试文件结构
    test_files = [
        os.path.join(temp_dir, "file1.txt"),
        os.path.join(temp_dir, "file2.txt"),
        os.path.join(temp_dir, "subdir1", "file1.txt"),  # 同名文件在不同目录
        os.path.join(temp_dir, "subdir2", "file2.txt"),  # 同名文件在不同目录
        os.path.join(temp_dir, "unique_file.txt")
    ]
    
    # 创建目录和文件
    for file_path in test_files:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文件: {os.path.basename(file_path)}")
        print(f"创建文件: {file_path}")
    
    return temp_dir

def create_test_csv(temp_dir, csv_path):
    """创建测试CSV文件"""
    test_data = [
        # 正常重命名
        [os.path.join(temp_dir, "file1.txt"), os.path.join(temp_dir, "renamed_file1.txt")],
        [os.path.join(temp_dir, "file2.txt"), os.path.join(temp_dir, "renamed_file2.txt")],
        
        # 不同目录中的同名文件
        [os.path.join(temp_dir, "subdir1", "file1.txt"), os.path.join(temp_dir, "subdir1", "renamed_subdir1_file1.txt")],
        [os.path.join(temp_dir, "subdir2", "file2.txt"), os.path.join(temp_dir, "subdir2", "renamed_subdir2_file2.txt")],
        
        # 唯一文件
        [os.path.join(temp_dir, "unique_file.txt"), os.path.join(temp_dir, "renamed_unique.txt")],
        
        # 测试重复源路径（目标路径相同）- 应该正常处理
        [os.path.join(temp_dir, "file1.txt"), os.path.join(temp_dir, "duplicate_same_target.txt")],
        
        # 测试重复源路径（目标路径不同）- 应该跳过
        [os.path.join(temp_dir, "file1.txt"), os.path.join(temp_dir, "duplicate_different_target.txt")],
    ]
    
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        import csv
        writer = csv.writer(f)
        for row in test_data:
            writer.writerow(row)
    
    print(f"创建CSV文件: {csv_path}")
    return test_data

def main():
    """主测试函数"""
    temp_dir = None
    try:
        # 创建测试环境
        temp_dir = create_test_files()
        csv_path = os.path.join(temp_dir, "test_rename.csv")
        test_data = create_test_csv(temp_dir, csv_path)
        
        print("\n" + "="*50)
        print("开始测试改进后的 rename_files_in_place 函数")
        print("="*50)
        
        # 执行重命名操作
        result = rename_files_in_place(temp_dir, csv_path, conflict_mode="copy")
        
        print("\n" + "="*50)
        print("测试结果:")
        print("="*50)
        
        # 检查结果
        if result:
            print(f"成功重命名了 {len(result)} 个文件:")
            for old_name, new_name, source_path, target_path in result:
                print(f"  {old_name} -> {new_name}")
                print(f"    源: {source_path}")
                print(f"    目标: {target_path}")
                
                # 验证文件是否存在
                if os.path.exists(target_path):
                    print(f"    ✓ 目标文件存在")
                else:
                    print(f"    ✗ 目标文件不存在")
                
                # 验证源文件是否已重命名（不存在）
                if not os.path.exists(source_path):
                    print(f"    ✓ 源文件已正确重命名")
                else:
                    print(f"    ✗ 源文件仍然存在")
                
                print()
        
        # 检查目录结构
        print("最终目录结构:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = '  ' * (level + 1)
            for file in files:
                print(f"{sub_indent}{file}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            print(f"\n清理测试目录: {temp_dir}")
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
