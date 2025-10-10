#!/usr/bin/env python3
"""
测试撤回功能是否支持冲突处理模式
"""

import os
import tempfile
import shutil
import csv
from Pyzard import search_and_copy_files, undo_last_operation

def test_undo_with_conflict_modes():
    """测试撤回功能是否支持冲突处理模式"""
    print("=== 测试撤回功能支持冲突处理模式 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建测试目录: {temp_dir}")
    
    # 创建源目录结构
    source_dir = os.path.join(temp_dir, "source")
    os.makedirs(source_dir)
    
    # 创建测试文件
    with open(os.path.join(source_dir, "test_file.txt"), "w") as f:
        f.write("这是测试文件的内容")
    
    # 创建目标目录并添加冲突文件
    target_dir = os.path.join(temp_dir, "target")
    os.makedirs(target_dir)
    
    # 在目标目录中创建冲突文件
    with open(os.path.join(target_dir, "test_file.txt"), "w") as f:
        f.write("这是目标目录中已存在的文件")
    
    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["test_file.txt", "test_file.txt"])
    
    try:
        # 测试副本模式
        print("\n1. 测试副本模式操作")
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False, conflict_mode="copy")
        print(f"操作结果: {result}")
        
        # 验证副本是否被创建
        if len(result) == 1 and "副本" in result[0]:
            print("✓ 副本文件创建成功")
            
            # 测试撤回操作
            print("\n2. 测试撤回操作")
            undo_success = undo_last_operation()
            if undo_success:
                print("✓ 撤回操作成功")
                
                # 验证撤回结果
                if not os.path.exists(result[0]):
                    print("✓ 副本文件已被正确删除")
                else:
                    print("✗ 副本文件未被删除")
                    
                # 验证源文件是否恢复
                if os.path.exists(os.path.join(source_dir, "test_file.txt")):
                    print("✓ 源文件保持原样")
                else:
                    print("✗ 源文件状态异常")
            else:
                print("✗ 撤回操作失败")
        else:
            print("✗ 副本文件创建失败")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    finally:
        # 清理
        shutil.rmtree(temp_dir)
        print(f"清理测试目录: {temp_dir}")

if __name__ == "__main__":
    test_undo_with_conflict_modes()
    print("\n=== 撤回功能测试完成 ===")
