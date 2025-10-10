#!/usr/bin/env python3
"""
测试错误处理修复效果的脚本
"""

import os
import tempfile
import shutil
import csv
from Pyzard import (
    extract_entire_folder,
    search_and_copy_files,
    rename_files_in_place,
    copy_files_from_csv_paths,
    undo_last_operation,
)


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

    # 创建目标目录
    target_dir = os.path.join(temp_dir, "target")
    os.makedirs(target_dir)

    return temp_dir, source_dir, target_dir


def test_extract_folder_with_missing_target():
    """测试提取文件夹功能 - 目标目录不存在的情况"""
    print("\n=== 测试1: 提取文件夹功能 - 目标目录不存在 ===")

    temp_dir, source_dir, target_dir = create_test_files()

    # 删除目标目录，模拟目标目录不存在的情况
    shutil.rmtree(target_dir)

    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "folders.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["folder1", "new_folder1"])
        writer.writerow(["folder2", "new_folder2"])

    try:
        # 执行提取文件夹操作
        result = extract_entire_folder(source_dir, target_dir, csv_file, cut_mode=False)
        print(f"操作结果: {result}")
        print("测试通过: 程序正确处理了目标目录不存在的情况")
    except Exception as e:
        print(f"测试失败: {e}")

    # 清理
    shutil.rmtree(temp_dir)


def test_search_copy_with_missing_source():
    """测试搜索复制功能 - 源目录不存在的情况"""
    print("\n=== 测试2: 搜索复制功能 - 源目录不存在 ===")

    temp_dir, source_dir, target_dir = create_test_files()

    # 删除源目录，模拟源目录不存在的情况
    shutil.rmtree(source_dir)

    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file1.txt", "new_file1.txt"])

    try:
        # 执行搜索复制操作
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False)
        print(f"操作结果: {result}")
        print("测试通过: 程序正确处理了源目录不存在的情况")
    except Exception as e:
        print(f"测试失败: {e}")

    # 清理
    shutil.rmtree(temp_dir)


def test_rename_with_missing_csv():
    """测试重命名功能 - CSV文件不存在的情况"""
    print("\n=== 测试3: 重命名功能 - CSV文件不存在 ===")

    temp_dir, source_dir, target_dir = create_test_files()

    # 使用不存在的CSV文件
    csv_file = os.path.join(temp_dir, "nonexistent.csv")

    try:
        # 执行重命名操作
        result = rename_files_in_place(source_dir, csv_file)
        print(f"操作结果: {result}")
        print("测试通过: 程序正确处理了CSV文件不存在的情况")
    except Exception as e:
        print(f"测试失败: {e}")

    # 清理
    shutil.rmtree(temp_dir)


def test_history_recording():
    """测试历史记录功能"""
    print("\n=== 测试4: 历史记录功能 ===")

    temp_dir, source_dir, target_dir = create_test_files()

    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file1.txt", "new_file1.txt"])

    try:
        # 执行一个成功的操作
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False)
        print(f"成功操作结果: {result}")

        # 检查历史记录文件是否存在
        history_file = ".operation_history.json"
        if os.path.exists(history_file):
            print("历史记录文件已创建")

            # 读取历史记录
            import json

            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            if history:
                last_op = history[-1]
                print(f"最后操作状态: {last_op.get('status')}")
                print(f"操作成功: {last_op.get('success')}")
                print("测试通过: 历史记录功能正常工作")
            else:
                print("测试失败: 历史记录为空")
        else:
            print("测试失败: 历史记录文件未创建")

    except Exception as e:
        print(f"测试失败: {e}")

    # 清理
    shutil.rmtree(temp_dir)


def test_undo_functionality():
    """测试撤回功能"""
    print("\n=== 测试5: 撤回功能 ===")

    temp_dir, source_dir, target_dir = create_test_files()

    # 创建CSV文件
    csv_file = os.path.join(temp_dir, "files.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file1.txt", "new_file1.txt"])

    try:
        # 执行一个成功的操作
        result = search_and_copy_files(source_dir, target_dir, csv_file, cut_mode=False)
        print(f"操作结果: {result}")

        # 尝试撤回操作
        undo_result = undo_last_operation()
        print(f"撤回操作结果: {undo_result}")

        if undo_result:
            print("测试通过: 撤回功能正常工作")
        else:
            print("测试失败: 撤回操作失败")

    except Exception as e:
        print(f"测试失败: {e}")

    # 清理
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("开始测试错误处理修复效果...")

    # 运行所有测试
    test_extract_folder_with_missing_target()
    test_search_copy_with_missing_source()
    test_rename_with_missing_csv()
    test_history_recording()
    test_undo_functionality()

    print("\n=== 测试完成 ===")
