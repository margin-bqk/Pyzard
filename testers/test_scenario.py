#!/usr/bin/env python3
"""
测试脚本：模拟原目录和目标目录相同时的剪切模式操作
"""

import os
import shutil
import csv

# 创建测试目录和文件
test_dir = "test_scenario"
source_target_dir = os.path.join(test_dir, "same_directory")
csv_file = os.path.join(test_dir, "test_files.csv")

# 清理并创建测试环境
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)
os.makedirs(source_target_dir, exist_ok=True)

# 创建测试图片文件
test_files = [
    "image1.jpg",
    "photo2.png", 
    "picture3.bmp"
]

for file_name in test_files:
    with open(os.path.join(source_target_dir, file_name), 'w') as f:
        f.write(f"Content of {file_name}")

# 创建CSV文件（原目录和目标目录相同，但文件名不同）
csv_content = [
    ["image1.jpg", "renamed_image1.jpg"],
    ["photo2.png", "new_photo2.png"],
    ["picture3.bmp", "updated_picture3.bmp"]
]

with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerows(csv_content)

print("测试环境创建完成！")
print(f"源目录/目标目录: {source_target_dir}")
print(f"CSV文件: {csv_file}")
print("原始文件:")
for file in test_files:
    print(f"  - {file}")
print("目标文件名:")
for old_name, new_name in csv_content:
    print(f"  - {old_name} -> {new_name}")
