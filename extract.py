import os
import shutil
import csv
import json
import uuid
import time
from datetime import datetime


def search_and_copy_files(source, target, csv_file, cut_mode=False):
    """搜索并复制/剪切匹配的文件"""
    copied_files = []
    renamed_files = []
    backup_paths = []
    source_paths = []
    temp_backup_dir = ".temp_backup"
    os.makedirs(temp_backup_dir, exist_ok=True)

    # 生成操作ID
    operation_id = str(uuid.uuid4())
    operation_type = "剪切" if cut_mode else "复制"

    # 读取CSV里的文件名和目标替换名
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:  # 跳过空行
                continue
                
            file_name = row[0].strip()
            target_name = row[1].strip() if len(row) > 1 else file_name
            
            print(f"正在搜索文件: {file_name} -> {target_name} ({operation_type}模式)")

            # 遍历source目录
            found = False
            for root, dirs, files in os.walk(source):
                for file in files:
                    if file.lower() == file_name.lower():
                        # 构建源文件路径和目标文件路径
                        source_file = os.path.join(root, file)
                        dest_file = os.path.join(target, target_name)
                        
                        print(f"  找到: {source_file}")
                        print(f"  正在{operation_type}到: {dest_file}")

                        # 确保目标目录存在
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        
                        if cut_mode:
                            # 剪切模式：先备份再移动
                            temp_backup = os.path.join(temp_backup_dir, f"backup_{os.path.basename(source_file)}_{os.urandom(4).hex()}")
                            try:
                                # 检查源文件是否存在
                                if not os.path.exists(source_file):
                                    print(f"  警告: 源文件不存在: {source_file}")
                                    continue
                                
                                # 检查目标文件是否已存在（避免意外覆盖）
                                if os.path.exists(dest_file) and source_file != dest_file:
                                    print(f"  警告: 目标文件已存在: {dest_file}")
                                    # 可以选择跳过或覆盖，这里选择跳过以避免数据丢失
                                    print(f"  跳过{operation_type}操作以避免覆盖现有文件")
                                    continue
                                
                                # 1. 备份到临时位置
                                print(f"  正在创建备份: {source_file} -> {temp_backup}")
                                shutil.copy2(source_file, temp_backup)
                                print(f"  备份创建成功: {temp_backup}")
                                backup_paths.append(temp_backup)
                                source_paths.append(source_file)
                                
                                # 2. 移动文件（在相同目录下实际上是重命名）
                                print(f"  正在移动文件: {source_file} -> {dest_file}")
                                shutil.move(source_file, dest_file)
                                copied_files.append(dest_file)
                                
                                # 验证移动是否成功
                                if os.path.exists(dest_file) and not os.path.exists(source_file):
                                    print(f"  {operation_type}成功: 文件已移动到 {dest_file}")
                                else:
                                    print(f"  警告: {operation_type}操作可能未完全成功")
                                    print(f"  源文件存在: {os.path.exists(source_file)}")
                                    print(f"  目标文件存在: {os.path.exists(dest_file)}")
                                
                            except Exception as e:
                                print(f"  {operation_type}操作发生异常: {e}")
                                # 恢复备份
                                if os.path.exists(temp_backup):
                                    try:
                                        shutil.move(temp_backup, source_file)
                                        print(f"  {operation_type}失败，已从备份恢复文件到原位置")
                                    except Exception as restore_error:
                                        print(f"  恢复备份失败: {restore_error}")
                                        print(f"  备份文件位置: {temp_backup}")
                                else:
                                    print(f"  备份文件不存在，无法恢复: {temp_backup}")
                                raise e
                                
                        else:
                            # 复制模式
                            shutil.copy2(source_file, dest_file)
                            copied_files.append(dest_file)
                            source_paths.append(source_file)
                        
                        # 如果目标名称与原名称不同，记录重命名信息
                        if target_name != file_name:
                            renamed_files.append((file_name, target_name))
                        
                        found = True
                        break
                if found:
                    break
            
            if not found:
                print(f"  警告: 文件 '{file_name}' 在源路径中未找到")

    # 保存操作历史记录
    if copied_files:
        save_operation_history(
            operation_type=operation_type,
            source_paths=source_paths,
            target_paths=copied_files,
            backup_paths=backup_paths if cut_mode else None,
            operation_id=operation_id
        )

    # 输出重命名信息
    if renamed_files:
        print("\n重命名统计:")
        for old_name, new_name in renamed_files:
            print(f"  {old_name} -> {new_name}")

    return copied_files


def rename_files_in_place(source, csv_file):
    """在原地重命名文件（不移动到其他目录）"""
    renamed_files = []
    backup_paths = []
    source_paths = []
    temp_backup_dir = ".temp_backup"
    os.makedirs(temp_backup_dir, exist_ok=True)

    # 生成操作ID
    operation_id = str(uuid.uuid4())
    operation_type = "重命名"

    # 读取CSV里的文件名和目标替换名
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:  # 跳过空行
                continue
                
            file_name = row[0].strip()
            target_name = row[1].strip() if len(row) > 1 else file_name
            
            print(f"正在搜索文件: {file_name} -> {target_name} (重命名模式)")

            # 遍历source目录
            found = False
            for root, dirs, files in os.walk(source):
                for file in files:
                    if file.lower() == file_name.lower():
                        # 构建源文件路径和目标文件路径（在同一目录）
                        source_file = os.path.join(root, file)
                        dest_file = os.path.join(root, target_name)
                        
                        print(f"  找到: {source_file}")
                        print(f"  正在重命名到: {dest_file}")

                        # 重命名模式：先备份再重命名
                        temp_backup = os.path.join(temp_backup_dir, f"backup_{os.path.basename(source_file)}_{os.urandom(4).hex()}")
                        try:
                            # 检查源文件是否存在
                            if not os.path.exists(source_file):
                                print(f"  警告: 源文件不存在: {source_file}")
                                continue
                            
                            # 检查目标文件是否已存在（避免意外覆盖）
                            if os.path.exists(dest_file) and source_file != dest_file:
                                print(f"  警告: 目标文件已存在: {dest_file}")
                                print(f"  跳过重命名操作以避免覆盖现有文件")
                                continue
                            
                            # 1. 备份到临时位置
                            print(f"  正在创建备份: {source_file} -> {temp_backup}")
                            shutil.copy2(source_file, temp_backup)
                            print(f"  备份创建成功: {temp_backup}")
                            backup_paths.append(temp_backup)
                            source_paths.append(source_file)
                            
                            # 2. 重命名文件（在同一目录下）
                            print(f"  正在重命名文件: {source_file} -> {dest_file}")
                            shutil.move(source_file, dest_file)
                            
                            # 验证重命名是否成功
                            if os.path.exists(dest_file) and not os.path.exists(source_file):
                                print(f"  重命名成功: 文件已重命名为 {dest_file}")
                            else:
                                print(f"  警告: 重命名操作可能未完全成功")
                                print(f"  源文件存在: {os.path.exists(source_file)}")
                                print(f"  目标文件存在: {os.path.exists(dest_file)}")
                            
                        except Exception as e:
                            print(f"  重命名操作发生异常: {e}")
                            # 恢复备份
                            if os.path.exists(temp_backup):
                                try:
                                    shutil.move(temp_backup, source_file)
                                    print(f"  重命名失败，已从备份恢复文件到原位置")
                                except Exception as restore_error:
                                    print(f"  恢复备份失败: {restore_error}")
                                    print(f"  备份文件位置: {temp_backup}")
                            else:
                                print(f"  备份文件不存在，无法恢复: {temp_backup}")
                            raise e
                        
                        # 记录重命名信息
                        if target_name != file_name:
                            renamed_files.append((file_name, target_name))
                        
                        found = True
                        break
                if found:
                    break
            
            if not found:
                print(f"  警告: 文件 '{file_name}' 在源路径中未找到")

    # 保存操作历史记录
    if renamed_files:
        save_operation_history(
            operation_type=operation_type,
            source_paths=source_paths,
            target_paths=[os.path.join(os.path.dirname(src), new_name) for src, (old_name, new_name) in zip(source_paths, renamed_files)],
            backup_paths=backup_paths,
            operation_id=operation_id
        )

    # 输出重命名信息
    if renamed_files:
        print("\n重命名统计:")
        for old_name, new_name in renamed_files:
            print(f"  {old_name} -> {new_name}")

    return renamed_files


def extract_entire_folder(source, target, csv_file, cut_mode=False):
    """提取整个文件夹到指定目录（支持遍历文件树）"""
    copied_folders = []
    renamed_files = []
    backup_paths = []
    source_paths = []
    temp_backup_dir = ".temp_backup"
    os.makedirs(temp_backup_dir, exist_ok=True)

    # 生成操作ID
    operation_id = str(uuid.uuid4())
    operation_type = "剪切" if cut_mode else "复制"

    # 读取CSV里的文件夹名字和目标替换名
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        folder_targets = []
        for row in reader:
            if not row:  # 跳过空行
                continue
                
            folder_name = row[0].strip()
            target_name = row[1].strip() if len(row) > 1 else folder_name
            folder_targets.append((folder_name, target_name))
            
            print(f"正在搜索文件夹: {folder_name} -> {target_name} ({operation_type}模式)")

    # 遍历整个源目录树来查找文件夹
    found_folders = {}
    for root, dirs, files in os.walk(source):
        for dir_name in dirs:
            # 检查当前目录是否在要搜索的文件夹列表中
            for folder_name, target_name in folder_targets:
                if dir_name.lower() == folder_name.lower():
                    source_folder = os.path.join(root, dir_name)
                    # 构建目标路径（直接放在目标目录下，不保持相对路径）
                    dest_path = os.path.join(target, target_name)
                    
                    found_folders[source_folder] = (folder_name, target_name, dest_path)
                    break

    # 处理找到的文件夹
    for source_folder, (folder_name, target_name, dest_path) in found_folders.items():
        print(f"  找到: {source_folder}")
        print(f"  正在{operation_type}到: {dest_path}")

        # 确保目标目录的父目录存在
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        if cut_mode:
            # 剪切模式：先备份再移动
            temp_backup = os.path.join(temp_backup_dir, f"backup_{os.path.basename(source_folder)}_{os.urandom(4).hex()}")
            try:
                # 1. 备份到临时位置
                shutil.copytree(source_folder, temp_backup)
                print(f"  已创建备份: {temp_backup}")
                backup_paths.append(temp_backup)
                source_paths.append(source_folder)
                
                # 2. 移动文件夹
                shutil.move(source_folder, dest_path)
                copied_folders.append(dest_path)
                
                print(f"  {operation_type}成功")
                
            except Exception as e:
                # 恢复备份
                if os.path.exists(temp_backup):
                    shutil.move(temp_backup, source_folder)
                    print(f"  {operation_type}失败，已从备份恢复文件夹")
                raise e
                
        else:
            # 复制模式
            # 如果目标已经存在，先删除（避免冲突）
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(source_folder, dest_path)
            copied_folders.append(dest_path)
            source_paths.append(source_folder)
        
        # 如果目标名称与原名称不同，记录重命名信息
        if target_name != folder_name:
            renamed_files.append((folder_name, target_name))

    # 保存操作历史记录
    if copied_folders:
        save_operation_history(
            operation_type=operation_type,
            source_paths=source_paths,
            target_paths=copied_folders,
            backup_paths=backup_paths if cut_mode else None,
            operation_id=operation_id
        )

    # 检查是否有未找到的文件夹
    found_folder_names = {name for name, _, _ in found_folders.values()}
    for folder_name, target_name in folder_targets:
        if folder_name not in found_folder_names:
            print(f"  警告: 文件夹 '{folder_name}' 在源路径中未找到")

    # 输出重命名信息
    if renamed_files:
        print("\n重命名统计:")
        for old_name, new_name in renamed_files:
            print(f"  {old_name} -> {new_name}")

    return copied_folders


def export_structure_to_csv(target, log_csv):
    with open(log_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Level", "Type", "Name", "FullPath"])

        for root, dirs, files in os.walk(target):
            # 计算层级（相对target）
            rel_path = os.path.relpath(root, target)
            if rel_path == ".":
                level = 0
                folder_name = os.path.basename(target.rstrip("\\/"))
            else:
                level = rel_path.count(os.sep) + 1
                folder_name = os.path.basename(root)

            indent = "    " * level
            writer.writerow([level, "Folder", f"{indent}{folder_name}", root])

            # 列出文件
            for file in files:
                file_level = level + 1
                indent_file = "    " * file_level
                full_path = os.path.join(root, file)
                writer.writerow([file_level, "File", f"{indent_file}{file}", full_path])


def save_operation_history(operation_type, source_paths, target_paths, backup_paths=None, operation_id=None):
    """保存操作历史记录"""
    history_file = ".operation_history.json"
    
    # 读取现有历史记录
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # 创建新操作记录
    if operation_id is None:
        operation_id = str(uuid.uuid4())
    
    operation_record = {
        "id": operation_id,
        "type": operation_type,
        "source_paths": source_paths,
        "target_paths": target_paths,
        "backup_paths": backup_paths or [],
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }
    
    # 添加到历史记录
    history.append(operation_record)
    
    # 保存历史记录
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return operation_id


def undo_last_operation():
    """撤回上一次操作"""
    history_file = ".operation_history.json"
    
    if not os.path.exists(history_file):
        print("没有操作历史记录")
        return False
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        print("无法读取操作历史记录")
        return False
    
    if not history:
        print("没有可撤回的操作")
        return False
    
    # 找到最近未撤回的操作
    last_operation = None
    for op in reversed(history):
        if op.get("status") == "completed":
            last_operation = op
            break
    
    if not last_operation:
        print("没有可撤回的操作")
        return False
    
    print(f"正在撤回操作: {last_operation['type']} (ID: {last_operation['id']})")
    
    try:
        if last_operation["type"] == "剪切":
            # 撤回剪切操作：从备份恢复，删除目标文件
            success_count = 0
            for i, (backup_path, target_path) in enumerate(zip(last_operation["backup_paths"], last_operation["target_paths"])):
                try:
                    if os.path.exists(backup_path):
                        # 恢复文件到对应的源路径
                        source_path = last_operation["source_paths"][i]
                        
                        # 确保源目录存在
                        os.makedirs(os.path.dirname(source_path), exist_ok=True)
                        
                        if os.path.isfile(backup_path):
                            shutil.move(backup_path, source_path)
                        elif os.path.isdir(backup_path):
                            shutil.move(backup_path, source_path)
                        
                        # 删除目标文件
                        if os.path.exists(target_path) and target_path != source_path:
                            if os.path.isfile(target_path):
                                os.remove(target_path)
                            elif os.path.isdir(target_path):
                                shutil.rmtree(target_path)
                        
                        success_count += 1
                        print(f"  已撤回: {target_path} -> {source_path}")
                    else:
                        print(f"  警告: 备份文件不存在: {backup_path}")
                        
                except Exception as e:
                    print(f"  撤回文件失败 {target_path}: {e}")
            
            if success_count > 0:
                print(f"撤回操作完成，成功撤回 {success_count} 个文件")
            else:
                print("撤回操作失败，没有文件被成功撤回")
                return False
        
        elif last_operation["type"] == "复制":
            # 撤回复制操作：删除目标文件
            for target_path in last_operation["target_paths"]:
                if os.path.exists(target_path):
                    if os.path.isfile(target_path):
                        os.remove(target_path)
                    elif os.path.isdir(target_path):
                        shutil.rmtree(target_path)
        
        elif last_operation["type"] == "重命名":
            # 撤回重命名操作：从备份恢复，删除重命名后的文件
            success_count = 0
            for i, (backup_path, target_path) in enumerate(zip(last_operation["backup_paths"], last_operation["target_paths"])):
                try:
                    if os.path.exists(backup_path):
                        # 恢复文件到对应的源路径
                        source_path = last_operation["source_paths"][i]
                        
                        # 确保源目录存在
                        os.makedirs(os.path.dirname(source_path), exist_ok=True)
                        
                        if os.path.isfile(backup_path):
                            shutil.move(backup_path, source_path)
                        elif os.path.isdir(backup_path):
                            shutil.move(backup_path, source_path)
                        
                        # 删除重命名后的文件
                        if os.path.exists(target_path) and target_path != source_path:
                            if os.path.isfile(target_path):
                                os.remove(target_path)
                            elif os.path.isdir(target_path):
                                shutil.rmtree(target_path)
                        
                        success_count += 1
                        print(f"  已撤回: {target_path} -> {source_path}")
                    else:
                        print(f"  警告: 备份文件不存在: {backup_path}")
                        
                except Exception as e:
                    print(f"  撤回文件失败 {target_path}: {e}")
            
            if success_count > 0:
                print(f"撤回操作完成，成功撤回 {success_count} 个文件")
            else:
                print("撤回操作失败，没有文件被成功撤回")
                return False
        
        # 更新操作状态
        last_operation["status"] = "undone"
        last_operation["undo_timestamp"] = datetime.now().isoformat()
        
        # 保存更新后的历史记录
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        print("撤回操作成功")
        return True
        
    except Exception as e:
        print(f"撤回操作失败: {e}")
        return False


def cleanup_backup_files(keep_recent=False):
    """清理备份文件
    Args:
        keep_recent: 是否保留最近操作的备份文件（用于撤回功能）
    """
    temp_backup_dir = ".temp_backup"
    if not os.path.exists(temp_backup_dir):
        return
    
    try:
        if keep_recent:
            # 只清理非最近操作的备份文件
            # 读取历史记录找到最近操作的备份文件
            history_file = ".operation_history.json"
            recent_backups = set()
            
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                    
                    # 找到最近未撤回的操作
                    for op in reversed(history):
                        if op.get("status") == "completed":
                            recent_backups.update(op.get("backup_paths", []))
                            break
                except:
                    pass
            
            # 清理非最近备份
            for item in os.listdir(temp_backup_dir):
                item_path = os.path.join(temp_backup_dir, item)
                if item_path not in recent_backups:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            print("已清理旧备份文件，保留最近操作的备份")
        else:
            # 清理所有备份文件
            shutil.rmtree(temp_backup_dir)
            print("已清理所有备份文件")
            
    except Exception as e:
        print(f"清理备份文件失败: {e}")


def copy_files_from_csv_paths(csv_file, cut_mode=False):
    """从CSV路径复制文件到目标文件夹
    Args:
        csv_file: CSV文件路径，第一列为源文件路径，第二列为目标文件夹路径
        cut_mode: 是否为剪切模式
    """
    copied_files = []
    backup_paths = []
    source_paths = []
    temp_backup_dir = ".temp_backup"
    os.makedirs(temp_backup_dir, exist_ok=True)

    # 生成操作ID
    operation_id = str(uuid.uuid4())
    operation_type = "剪切" if cut_mode else "复制"

    # 读取CSV里的文件路径和目标文件夹路径
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        file_targets = []
        for row_num, row in enumerate(reader, 1):
            if not row:  # 跳过空行
                continue
                
            if len(row) < 2:
                print(f"警告: 第 {row_num} 行数据不完整，需要至少两列数据")
                continue
                
            source_path = row[0].strip()
            target_folder = row[1].strip()
            file_targets.append((source_path, target_folder))
            
            print(f"正在处理: {source_path} -> {target_folder} ({operation_type}模式)")

    # 处理文件复制
    for source_path, target_folder in file_targets:
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            print(f"  警告: 源文件不存在: {source_path}")
            continue
            
        if not os.path.isfile(source_path):
            print(f"  警告: 源路径不是文件: {source_path}")
            continue
            
        # 构建目标文件路径（保持原文件名）
        file_name = os.path.basename(source_path)
        dest_path = os.path.join(target_folder, file_name)
        
        print(f"  源文件: {source_path}")
        print(f"  目标文件: {dest_path}")

        # 确保目标目录存在
        os.makedirs(target_folder, exist_ok=True)
        
        if cut_mode:
            # 剪切模式：先备份再移动
            temp_backup = os.path.join(temp_backup_dir, f"backup_{os.path.basename(source_path)}_{os.urandom(4).hex()}")
            try:
                # 检查源文件是否存在
                if not os.path.exists(source_path):
                    print(f"  警告: 源文件不存在: {source_path}")
                    continue
                
                # 检查目标文件是否已存在（避免意外覆盖）
                if os.path.exists(dest_path) and source_path != dest_path:
                    print(f"  警告: 目标文件已存在: {dest_path}")
                    print(f"  跳过{operation_type}操作以避免覆盖现有文件")
                    continue
                
                # 1. 备份到临时位置
                print(f"  正在创建备份: {source_path} -> {temp_backup}")
                shutil.copy2(source_path, temp_backup)
                print(f"  备份创建成功: {temp_backup}")
                backup_paths.append(temp_backup)
                source_paths.append(source_path)
                
                # 2. 移动文件
                print(f"  正在移动文件: {source_path} -> {dest_path}")
                shutil.move(source_path, dest_path)
                copied_files.append(dest_path)
                
                # 验证移动是否成功
                if os.path.exists(dest_path) and not os.path.exists(source_path):
                    print(f"  {operation_type}成功: 文件已移动到 {dest_path}")
                else:
                    print(f"  警告: {operation_type}操作可能未完全成功")
                    print(f"  源文件存在: {os.path.exists(source_path)}")
                    print(f"  目标文件存在: {os.path.exists(dest_path)}")
                
            except Exception as e:
                print(f"  {operation_type}操作发生异常: {e}")
                # 恢复备份
                if os.path.exists(temp_backup):
                    try:
                        shutil.move(temp_backup, source_path)
                        print(f"  {operation_type}失败，已从备份恢复文件到原位置")
                    except Exception as restore_error:
                        print(f"  恢复备份失败: {restore_error}")
                        print(f"  备份文件位置: {temp_backup}")
                else:
                    print(f"  备份文件不存在，无法恢复: {temp_backup}")
                raise e
                
        else:
            # 复制模式
            try:
                # 检查目标文件是否已存在（避免意外覆盖）
                if os.path.exists(dest_path) and source_path != dest_path:
                    print(f"  警告: 目标文件已存在: {dest_path}")
                    print(f"  跳过复制操作以避免覆盖现有文件")
                    continue
                
                shutil.copy2(source_path, dest_path)
                copied_files.append(dest_path)
                source_paths.append(source_path)
                print(f"  复制成功: 文件已复制到 {dest_path}")
                
            except Exception as e:
                print(f"  复制操作发生异常: {e}")
                raise e

    # 保存操作历史记录
    if copied_files:
        save_operation_history(
            operation_type=operation_type,
            source_paths=source_paths,
            target_paths=copied_files,
            backup_paths=backup_paths if cut_mode else None,
            operation_id=operation_id
        )

    return copied_files


def export_directory_to_csv(target_dir, output_csv, recursive=True):
    """导出目录结构到CSV文件
    Args:
        target_dir: 目标目录路径
        output_csv: 输出CSV文件路径
        recursive: 是否递归遍历子目录
    """
    try:
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(["名称", "类型", "完整路径", "大小(字节)", "修改时间", "层级"])
            
            if recursive:
                # 递归遍历模式
                for root, dirs, files in os.walk(target_dir):
                    # 计算层级（相对target_dir）
                    rel_path = os.path.relpath(root, target_dir)
                    if rel_path == ".":
                        level = 0
                    else:
                        level = rel_path.count(os.sep) + 1
                    
                    # 处理当前目录
                    if root != target_dir or level == 0:
                        dir_name = os.path.basename(root)
                        dir_stat = os.stat(root)
                        writer.writerow([
                            dir_name,
                            "文件夹",
                            root,
                            "",
                            datetime.fromtimestamp(dir_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            level
                        ])
                    
                    # 处理文件
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_stat = os.stat(file_path)
                            writer.writerow([
                                file,
                                "文件",
                                file_path,
                                file_stat.st_size,
                                datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                level + 1
                            ])
                        except Exception as e:
                            print(f"  警告: 无法获取文件信息 {file_path}: {e}")
                            writer.writerow([file, "文件", file_path, "无法访问", "", level + 1])
                            
            else:
                # 仅根目录模式
                level = 0
                
                # 处理根目录本身
                root_stat = os.stat(target_dir)
                writer.writerow([
                    os.path.basename(target_dir.rstrip("\\/")),
                    "文件夹",
                    target_dir,
                    "",
                    datetime.fromtimestamp(root_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    level
                ])
                
                # 处理根目录下的文件和文件夹
                try:
                    items = os.listdir(target_dir)
                    for item in items:
                        item_path = os.path.join(target_dir, item)
                        try:
                            item_stat = os.stat(item_path)
                            if os.path.isdir(item_path):
                                writer.writerow([
                                    item,
                                    "文件夹",
                                    item_path,
                                    "",
                                    datetime.fromtimestamp(item_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                    level + 1
                                ])
                            else:
                                writer.writerow([
                                    item,
                                    "文件",
                                    item_path,
                                    item_stat.st_size,
                                    datetime.fromtimestamp(item_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                    level + 1
                                ])
                        except Exception as e:
                            print(f"  警告: 无法获取项目信息 {item_path}: {e}")
                            item_type = "文件夹" if os.path.isdir(item_path) else "文件"
                            writer.writerow([item, item_type, item_path, "无法访问", "", level + 1])
                            
                except Exception as e:
                    print(f"无法列出目录内容 {target_dir}: {e}")
                    return False
        
        print(f"目录结构已成功导出到: {output_csv}")
        return True
        
    except Exception as e:
        print(f"导出目录结构失败: {e}")
        return False


def cleanup_old_history(max_entries=50):
    """清理旧的历史记录，防止JSON文件过大
    Args:
        max_entries: 最大保留的历史记录条数
    """
    history_file = ".operation_history.json"
    
    if not os.path.exists(history_file):
        return
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 如果历史记录超过最大限制，删除最旧的部分
        if len(history) > max_entries:
            # 保留最近的 max_entries 条记录
            history = history[-max_entries:]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            print(f"已清理历史记录，保留最近 {max_entries} 条操作")
            
    except Exception as e:
        print(f"清理历史记录失败: {e}")


if __name__ == "__main__":
    while True:
        try:
            # ===== 功能选择界面 =====
            print("\n" + "="*50)
            print("请选择要使用的功能:")
            print("1. 搜索并复制匹配的文件")
            print("2. 提取整个文件夹到指定目录")
            print("3. 撤回上一次操作")
            print("4. 重命名文件（原地）")
            print("5. 从CSV路径复制文件到目标文件夹")
            print("6. 导出目录结构到CSV")
            print("7. 退出程序")
            
            while True:
                choice = input("请输入选项 (1, 2, 3, 4, 5, 6 或 7): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    break
                print("无效选项，请重新输入")
            
            if choice == '7':
                print("程序退出")
                break
                
            if choice == '3':
                # 撤回操作
                undo_last_operation()
            else:
                if choice == '4':
                    # 重命名模式
                    source = input("请输入源路径 (例如 D:\\SourcePath): ").strip('"')
                    csv_file = input("请输入文件名CSV路径 (例如 D:\\items.csv): ").strip('"')
                    log_csv = input("请输入导出结果CSV路径 (例如 D:\\result.csv): ").strip('"')
                    
                    print("\n=== 执行重命名文件功能 ===")
                    renamed = rename_files_in_place(source, csv_file)
                    print(f"\n重命名完成，以下文件已重命名:")
                    for old_name, new_name in renamed:
                        print(f" - {old_name} -> {new_name}")
                
                elif choice == '5':
                    # 从CSV路径复制文件模式
                    csv_file = input("请输入CSV文件路径 (例如 D:\\file_paths.csv): ").strip('"')
                    
                    # ===== 剪切模式选择 =====
                    cut_mode = False
                    cut_choice = input("是否使用剪切模式？(y/n, 默认n): ").strip().lower()
                    if cut_choice == 'y' or cut_choice == 'yes':
                        cut_mode = True
                        print("已启用剪切模式（文件将被移动而不是复制）")
                    else:
                        print("使用复制模式")

                    operation = "剪切" if cut_mode else "复制"
                    print(f"\n=== 执行从CSV路径{operation}文件功能 ===")
                    copied = copy_files_from_csv_paths(csv_file, cut_mode)
                    print(f"\n{operation}完成，以下文件已{operation}:")
                    for file in copied:
                        print(" -", file)
                
                elif choice == '6':
                    # 导出目录结构到CSV模式
                    target_dir = input("请输入目标目录路径 (例如 D:\\TargetPath): ").strip('"')
                    output_csv = input("请输入输出CSV路径 (例如 D:\\directory_structure.csv): ").strip('"')
                    
                    # ===== 遍历模式选择 =====
                    recursive = False
                    recursive_choice = input("是否递归遍历子目录？(y/n, 默认n): ").strip().lower()
                    if recursive_choice == 'y' or recursive_choice == 'yes':
                        recursive = True
                        print("递归遍历所有子目录")
                    else:
                        print("仅导出根目录内容")
                    
                    print(f"\n=== 执行导出目录结构功能 ===")
                    success = export_directory_to_csv(target_dir, output_csv, recursive)
                    if success:
                        print(f"目录结构已成功导出到: {output_csv}")
                    else:
                        print("导出目录结构失败")
                
                else:
                    # ===== 通用输入 =====
                    source = input("请输入源路径 (例如 D:\\SourcePath): ").strip('"')
                    target = input("请输入目标路径 (例如 D:\\TargetPath): ").strip('"')
                    csv_file = input("请输入文件名/文件夹名CSV路径 (例如 D:\\items.csv): ").strip('"')
                    log_csv = input("请输入导出结果CSV路径 (例如 D:\\result.csv): ").strip('"')
                    
                    # ===== 剪切模式选择 =====
                    cut_mode = False
                    cut_choice = input("是否使用剪切模式？(y/n, 默认n): ").strip().lower()
                    if cut_choice == 'y' or cut_choice == 'yes':
                        cut_mode = True
                        print("已启用剪切模式（文件将被移动而不是复制）")
                    else:
                        print("使用复制模式")

                    os.makedirs(target, exist_ok=True)

                    # ===== 执行选择的功能 =====
                    if choice == '1':
                        operation = "剪切" if cut_mode else "复制"
                        print(f"\n=== 执行搜索并{operation}文件功能 ===")
                        copied = search_and_copy_files(source, target, csv_file, cut_mode)
                        print(f"\n{operation}完成，以下文件已{operation}:")
                        for file in copied:
                            print(" -", file)
                    else:
                        operation = "剪切" if cut_mode else "复制"
                        print(f"\n=== 执行提取整个文件夹功能 ({operation}模式) ===")
                        copied = extract_entire_folder(source, target, csv_file, cut_mode)
                        print(f"\n{operation}完成，以下文件夹已{operation}:")
                        for folder in copied:
                            print(" -", folder)

                # 对于选项5和6，不进行结构导出
                if choice not in ['5', '6']:
                    print("\n正在导出最终结构到:", log_csv)
                    export_structure_to_csv(target if choice != '4' else source, log_csv)
                    print("导出完成！")
        
        except Exception as e:
            print(f"操作过程中发生错误: {e}")
            print("请检查输入参数并重试")
        
        finally:
            # 每次操作后只清理旧备份，保留最近操作的备份
            cleanup_backup_files(keep_recent=True)
            # 清理旧的历史记录
            cleanup_old_history()
            
        # 询问是否继续
        continue_choice = input("\n是否继续其他操作？(y/n, 默认y): ").strip().lower()
        if continue_choice == 'n' or continue_choice == 'no':
            # 程序退出时清理所有备份
            cleanup_backup_files(keep_recent=False)
            print("程序退出")
            break
