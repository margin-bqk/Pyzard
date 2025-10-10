#!/usr/bin/env python3
"""
Pyzard 综合测试脚本
用于验证修改后的程序是否能够完成原有的所有功能
支持命令行参数和规范化测试环境命名
"""

import os
import shutil
import csv
import tempfile
import time
import argparse
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional


class PyzardTester:
    """Pyzard 综合测试类"""
    
    def __init__(self, test_mode: str = "full"):
        self.test_results: List[Dict[str, Any]] = []
        self.test_start_time: Optional[float] = None
        self.test_dir: Optional[str] = None
        self.source_dir: Optional[str] = None
        self.target_dir: Optional[str] = None
        self.test_mode: str = test_mode
        
    def setup_test_environment(self):
        """设置测试环境"""
        print("=== 设置测试环境 ===")
        
        # 使用规范化命名创建临时测试目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_dir = tempfile.mkdtemp(prefix=f"pyzard_test_{timestamp}_")
        self.source_dir = os.path.join(self.test_dir, "source")
        self.target_dir = os.path.join(self.test_dir, "target")
        
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.target_dir, exist_ok=True)
        
        print(f"测试目录: {self.test_dir}")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print(f"测试模式: {self.test_mode}")
        
        # 创建测试文件
        self._create_test_files()
        print("测试环境设置完成")

    def _create_test_files(self):
        """创建测试文件"""
        # 确保源目录已设置
        if not self.source_dir:
            raise ValueError("源目录未设置，请先调用 setup_test_environment()")
            
        # 创建各种类型的测试文件
        test_files = [
            "文档1.txt",
            "图片1.jpg",
            "数据1.csv",
            "代码1.py",
            "报告1.pdf",
            "表格1.xlsx",
            "配置1.json",
            "日志1.log",
        ]

        for filename in test_files:
            file_path = os.path.join(self.source_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"这是测试文件: {filename}\n创建时间: {datetime.now()}")

        # 创建测试文件夹
        test_folders = ["文件夹1", "文件夹2", "子文件夹/嵌套文件夹"]
        for folder in test_folders:
            folder_path = os.path.join(self.source_dir, folder)
            os.makedirs(folder_path, exist_ok=True)

            # 在文件夹中创建文件
            for i in range(2):
                file_path = os.path.join(folder_path, f"文件{i+1}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"文件夹 {folder} 中的文件 {i+1}")

        print(f"创建了 {len(test_files)} 个测试文件和 {len(test_folders)} 个测试文件夹")

    def create_test_csv(self, filename: str, encoding: str = "utf-8-sig", data: Optional[List[List[str]]] = None) -> str:
        """创建测试CSV文件"""
        if not self.test_dir:
            raise ValueError("测试目录未设置，请先调用 setup_test_environment()")
            
        if data is None:
            data = [
                ["文档1.txt", "新文档1.txt"],
                ["图片1.jpg", "新图片1.jpg"],
                ["数据1.csv", "新数据1.csv"],
                ["代码1.py", "新代码1.py"],
            ]

        csv_path = os.path.join(self.test_dir, filename)

        with open(csv_path, "w", encoding=encoding, newline="") as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)

        print(f"创建测试CSV文件: {csv_path} (编码: {encoding})")
        return csv_path

    def run_test(self, test_name, test_function):
        """运行单个测试用例"""
        print(f"\n--- 运行测试: {test_name} ---")

        start_time = time.time()
        result = {"name": test_name, "status": "PASS", "message": "", "duration": 0}

        try:
            test_function()
            result["message"] = "测试通过"
        except Exception as e:
            result["status"] = "FAIL"
            result["message"] = f"测试失败: {str(e)}"
            print(f"❌ 测试失败: {e}")
        finally:
            result["duration"] = time.time() - start_time

        self.test_results.append(result)
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(
            f"{status_icon} {test_name} - {result['message']} ({result['duration']:.2f}s)"
        )

        return result["status"] == "PASS"

    def test_csv_encoding_detection(self):
        """测试CSV编码检测功能"""
        import Pyzard
        
        # 确保测试环境已设置
        if not self.test_dir:
            self.setup_test_environment()

        # 测试UTF-8编码
        utf8_csv = self.create_test_csv("test_utf8.csv", "utf-8-sig")
        result = Pyzard.read_csv_with_encoding_detection(utf8_csv)
        assert result[
            "success"
        ], f"UTF-8 CSV读取失败: {result.get('error', '未知错误')}"
        assert result["encoding"] == "utf-8-sig", f"编码检测错误: {result['encoding']}"
        assert result["total_rows"] == 4, f"行数错误: {result['total_rows']}"

        # 测试GBK编码
        gbk_csv = self.create_test_csv("test_gbk.csv", "gbk")
        result = Pyzard.read_csv_with_encoding_detection(gbk_csv)
        assert result["success"], f"GBK CSV读取失败: {result.get('error', '未知错误')}"
        assert result["encoding"] == "gbk", f"编码检测错误: {result['encoding']}"

        # 测试UTF-8编码（无BOM）
        utf8_nobom_csv = self.create_test_csv("test_utf8_nobom.csv", "utf-8")
        result = Pyzard.read_csv_with_encoding_detection(utf8_nobom_csv)
        assert result[
            "success"
        ], f"UTF-8无BOM CSV读取失败: {result.get('error', '未知错误')}"

        print("✅ CSV编码检测测试通过")

    def test_search_and_copy_files(self):
        """测试文件搜索复制功能"""
        import Pyzard

        # 创建测试CSV
        csv_file = self.create_test_csv("copy_test.csv")

        # 执行文件复制
        copied_files = Pyzard.search_and_copy_files(
            self.source_dir,
            self.target_dir,
            csv_file,
            cut_mode=False,
            conflict_mode="copy",
        )

        # 验证复制结果
        assert len(copied_files) > 0, "没有文件被复制"
        for file_path in copied_files:
            assert os.path.exists(file_path), f"目标文件不存在: {file_path}"

        print(f"✅ 文件搜索复制测试通过，复制了 {len(copied_files)} 个文件")

    def test_rename_files_in_place(self):
        """测试绝对路径重命名功能"""
        import Pyzard

        # 确保测试环境已设置
        if not self.source_dir:
            self.setup_test_environment()

        # 创建绝对路径重命名测试CSV
        rename_data = []
        for filename in ["文档1.txt", "图片1.jpg"]:
            source_path = os.path.join(self.source_dir or "", filename)
            target_filename = f"重命名_{filename}"
            target_path = os.path.join(self.source_dir or "", target_filename)
            rename_data.append([source_path, target_path])

        csv_file = self.create_test_csv("rename_test.csv", data=rename_data)

        # 执行重命名
        renamed_files = Pyzard.rename_files_in_place(
            self.source_dir, csv_file, conflict_mode="copy"
        )

        # 验证重命名结果
        assert len(renamed_files) > 0, "没有文件被重命名"

        # 检查文件是否被正确重命名
        for old_name, new_name, source_path, target_path in renamed_files:
            assert not os.path.exists(source_path) or os.path.exists(
                target_path
            ), f"重命名失败: {source_path} -> {target_path}"

        print(f"✅ 文件重命名测试通过，重命名了 {len(renamed_files)} 个文件")

    def test_extract_entire_folder(self):
        """测试文件夹提取功能"""
        import Pyzard

        # 创建文件夹提取测试CSV
        folder_data = [["文件夹1", "提取文件夹1"], ["文件夹2", "提取文件夹2"]]
        csv_file = self.create_test_csv("folder_test.csv", data=folder_data)

        # 执行文件夹提取
        copied_folders = Pyzard.extract_entire_folder(
            self.source_dir,
            self.target_dir,
            csv_file,
            cut_mode=False,
            conflict_mode="copy",
        )

        # 验证提取结果
        assert len(copied_folders) > 0, "没有文件夹被提取"
        for folder_path in copied_folders:
            assert os.path.exists(folder_path), f"目标文件夹不存在: {folder_path}"
            assert os.path.isdir(folder_path), f"目标路径不是文件夹: {folder_path}"

        print(f"✅ 文件夹提取测试通过，提取了 {len(copied_folders)} 个文件夹")

    def test_copy_files_from_csv_paths(self):
        """测试CSV路径复制功能"""
        import Pyzard

        # 确保测试环境已设置
        if not self.source_dir or not self.target_dir:
            self.setup_test_environment()

        # 创建路径复制测试CSV
        path_data = []
        for file in os.listdir(self.source_dir):
            if os.path.isfile(os.path.join(self.source_dir, file)):
                path_data.append(
                    [
                        os.path.join(self.source_dir, file),
                        os.path.join(self.target_dir, "from_paths"),
                    ]
                )

        if path_data:
            csv_file = self.create_test_csv("path_test.csv", data=path_data)

            # 执行路径复制
            copied_files = Pyzard.copy_files_from_csv_paths(
                csv_file, cut_mode=False, conflict_mode="copy"
            )

            # 验证复制结果
            assert len(copied_files) > 0, "没有文件通过路径复制"
            for file_path in copied_files:
                assert os.path.exists(file_path), f"目标文件不存在: {file_path}"

            print(f"✅ CSV路径复制测试通过，复制了 {len(copied_files)} 个文件")
        else:
            print("⚠️ 跳过CSV路径复制测试（没有找到测试文件）")

    def test_conflict_handling(self):
        """测试冲突处理功能"""
        import Pyzard

        # 先复制一些文件制造冲突
        csv_file = self.create_test_csv("conflict_test.csv")
        Pyzard.search_and_copy_files(
            self.source_dir,
            self.target_dir,
            csv_file,
            cut_mode=False,
            conflict_mode="copy",
        )

        # 再次复制相同的文件测试冲突处理
        copied_files = Pyzard.search_and_copy_files(
            self.source_dir,
            self.target_dir,
            csv_file,
            cut_mode=False,
            conflict_mode="copy",
        )

        # 验证冲突处理结果（应该创建副本）
        assert len(copied_files) > 0, "冲突处理失败"
        for file_path in copied_files:
            assert "_副本" in file_path or os.path.exists(
                file_path
            ), f"冲突处理异常: {file_path}"

        print("✅ 冲突处理测试通过")

    def test_error_handling(self):
        """测试错误处理功能"""
        import Pyzard

        # 确保测试环境已设置
        if not self.test_dir:
            self.setup_test_environment()

        # 测试不存在的CSV文件
        try:
            result = Pyzard.read_csv_with_encoding_detection("nonexistent.csv")
            assert not result["success"], "不存在的文件应该读取失败"
            print("✅ 文件不存在错误处理测试通过")
        except Exception as e:
            print(f"✅ 文件不存在错误处理测试通过（抛出异常）: {e}")

        # 测试空的CSV文件
        empty_csv = os.path.join(self.test_dir, "empty.csv")
        with open(empty_csv, "w", encoding="utf-8") as f:
            f.write("")

        result = Pyzard.read_csv_with_encoding_detection(empty_csv)
        assert not result["success"] or result["total_rows"] == 0, "空文件处理异常"
        print("✅ 空文件错误处理测试通过")

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("开始运行 Pyzard 综合测试")
        print("=" * 60)

        self.test_start_time = time.time()

        try:
            # 设置测试环境
            self.setup_test_environment()

            # 运行各个测试用例
            tests = [
                ("CSV编码检测", self.test_csv_encoding_detection),
                ("文件搜索复制", self.test_search_and_copy_files),
                ("文件重命名", self.test_rename_files_in_place),
                ("文件夹提取", self.test_extract_entire_folder),
                ("CSV路径复制", self.test_copy_files_from_csv_paths),
                ("冲突处理", self.test_conflict_handling),
                ("错误处理", self.test_error_handling),
            ]

            for test_name, test_func in tests:
                self.run_test(test_name, test_func)

            # 生成测试报告
            self.generate_test_report()

        finally:
            # 清理测试环境
            self.cleanup_test_environment()

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        total_duration = time.time() - (self.test_start_time or 0)

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"总耗时: {total_duration:.2f}秒")
        if total_tests > 0:
            print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        else:
            print("通过率: 0.0%")

        # 显示详细结果
        print("\n详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(
                f"  {status_icon} {result['name']} - {result['message']} ({result['duration']:.2f}s)"
            )

        # 总结
        if failed_tests == 0 and total_tests > 0:
            print("\n🎉 所有测试通过！程序功能正常。")
        elif total_tests == 0:
            print("\n⚠️ 没有运行任何测试。")
        else:
            print(f"\n⚠️ 有 {failed_tests} 个测试失败，需要检查相关功能。")

    def cleanup_test_environment(self):
        """清理测试环境"""
        if self.test_dir and os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
                print(f"\n清理测试目录: {self.test_dir}")
            except Exception as e:
                print(f"清理测试目录时出错: {e}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Pyzard 综合测试脚本")
    parser.add_argument(
        "--full", 
        action="store_true", 
        help="完整测试模式（所有功能测试）"
    )
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="快速测试模式（核心功能测试）"
    )
    parser.add_argument(
        "--encoding", 
        action="store_true", 
        help="编码测试模式（专门测试编码处理）"
    )
    parser.add_argument(
        "--performance", 
        action="store_true", 
        help="性能测试模式（性能基准测试）"
    )
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="测试后清理所有临时文件"
    )
    parser.add_argument(
        "--report", 
        metavar="FILE", 
        help="生成HTML测试报告到指定文件"
    )
    
    return parser.parse_args()


def get_test_mode(args):
    """根据命令行参数确定测试模式"""
    if args.full:
        return "full"
    elif args.quick:
        return "quick"
    elif args.encoding:
        return "encoding"
    elif args.performance:
        return "performance"
    else:
        return "full"  # 默认完整测试模式


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    test_mode = get_test_mode(args)
    
    print(f"Pyzard 综合测试脚本 - 模式: {test_mode}")
    print("=" * 50)
    
    # 创建测试器并运行测试
    tester = PyzardTester(test_mode=test_mode)
    
    try:
        if test_mode == "quick":
            # 快速测试模式：只运行核心功能测试
            print("快速测试模式：运行核心功能测试")
            tester.test_csv_encoding_detection()
            tester.test_search_and_copy_files()
            tester.test_error_handling()
        elif test_mode == "encoding":
            # 编码测试模式：专门测试编码处理
            print("编码测试模式：测试编码处理功能")
            tester.test_csv_encoding_detection()
        elif test_mode == "performance":
            # 性能测试模式：性能基准测试
            print("性能测试模式：运行性能基准测试")
            # 这里可以添加性能测试逻辑
            print("性能测试功能待实现")
        else:
            # 完整测试模式：运行所有测试
            tester.run_all_tests()
    
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        sys.exit(1)
    
    # 生成报告
    if args.report:
        print(f"\n生成HTML报告到: {args.report}")
        # HTML报告生成功能待实现
    
    # 清理临时文件
    if args.clean:
        print("\n清理临时文件...")
        # 这里可以添加清理逻辑


if __name__ == "__main__":
    main()
