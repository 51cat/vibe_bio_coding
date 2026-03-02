"""
测试脚本: 使用FormatTransferAgent处理money.xlsx文件
"""

import sys
import os
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, str(Path(__file__).parent / "agents" / "format_transfer"))

from agent import FormatTransferAgent


def test_list_sheets(agent, excel_file):
    print("\n" + "=" * 60)
    print("测试1: 列出Excel文件的所有sheet名称")
    print("=" * 60)
    agent.run_stream(f"列出文件 {excel_file} 中的所有sheet名称")
    print()


def test_excel_to_csv(agent, excel_file, output_csv):
    print("\n" + "=" * 60)
    print("测试2: 将Excel转换为CSV")
    print("=" * 60)
    agent.run_stream(f"将 {excel_file} 转换为CSV格式,输出到 {output_csv},强制覆盖")
    print()


def test_excel_to_tsv(agent, excel_file, output_tsv):
    print("\n" + "=" * 60)
    print("测试3: 将Excel转换为TSV")
    print("=" * 60)
    agent.run_stream(f"将 {excel_file} 转换为TSV格式,输出到 {output_tsv},强制覆盖")
    print()


def main():
    print("=" * 60)
    print("FormatTransferAgent 测试")
    print("=" * 60)

    excel_file = r"D:\Desktop\code\money.xlsx"
    output_csv = r"D:\Desktop\code\money_output.csv"
    output_tsv = r"D:\Desktop\code\money_output.tsv"

    agent = FormatTransferAgent(debug=False)

    test_list_sheets(agent, excel_file)
    test_excel_to_csv(agent, excel_file, output_csv)
    test_excel_to_tsv(agent, excel_file, output_tsv)

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
