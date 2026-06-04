# import os
# import subprocess

def merge_split_lines(input_file, output_file=None):
    """
    将文本中被折成连续两行的句子合并回同一行

    规则：
    - 不同句子之间用空行分隔
    - 如果两行连续（中间无空行），且第一行不是空行，则合并
    - 保留原有的空行作为句子分隔符

    参数:
        input_file: 输入文件路径
        output_file: 输出文件路径（如果不指定，自动生成）
    """
    if output_file is None:
        name, ext = os.path.splitext(input_file)
        output_file = f"{name}_merged{ext}"

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 去除每行末尾的换行符，但保留空行信息
    lines = [line.rstrip('\n\r') for line in lines]

    merged_lines = []
    i = 0
    total_lines = len(lines)

    while i < total_lines:
        current_line = lines[i]

        # 情况1：当前行是空行
        if current_line == '':
            merged_lines.append('')
            i += 1
            continue

        # 情况2：当前行非空，检查下一行是否非空且非空行（需要合并）
        if i + 1 < total_lines and lines[i + 1] != '':
            # 下一行非空，说明是连续的两行，需要合并
            merged_line = current_line + ' ' + lines[i + 1]
            merged_lines.append(merged_line)
            i += 2  # 跳过下一行
        else:
            # 下一行是空行或不存在，当前行单独保留
            merged_lines.append(current_line)
            i += 1

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_lines))

    print(f"处理完成！")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"原始行数: {total_lines}")
    print(f"处理后行数: {len(merged_lines)}")

    return output_file


# 更精细的版本：支持连续多行合并（如果折成3行或更多）
def merge_split_lines_advanced(input_file, output_file=None):
    """
    将文本中被折成连续多行的句子合并回同一行（支持2行以上的折行）
    """
    if output_file is None:
        name, ext = os.path.splitext(input_file)
        output_file = f"{name}_merged{ext}"

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [line.rstrip('\n\r') for line in lines]

    merged_lines = []
    i = 0
    total_lines = len(lines)

    while i < total_lines:
        current_line = lines[i]

        # 空行直接保留
        if current_line == '':
            merged_lines.append('')
            i += 1
            continue

        # 收集连续的非空行
        continuous_lines = [current_line]
        j = i + 1
        while j < total_lines and lines[j] != '':
            continuous_lines.append(lines[j])
            j += 1

        # 将连续的非空行合并成一行
        merged_line = ''.join(continuous_lines)
        merged_lines.append(merged_line)

        # 跳过已处理的行
        i = j

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_lines))

    print(f"处理完成！")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"原始行数: {total_lines}")
    print(f"处理后行数: {len(merged_lines)}")

    return output_file

# subprocess.run(["pipreqs", os.path.dirname(__file__), "--force"])

if __name__ == "__main__":
    import os

    # 使用示例
    input_file = input("请输入文本文件路径: ").strip()

    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
    else:
        print("\n选择处理模式：")
        print("1. 基础模式（只合并连续的两行）")
        print("2. 高级模式（合并连续的多行，支持折成3行以上）")
        mode = input("请选择 (1/2，默认2): ").strip()

        if mode == '1':
            merge_split_lines(input_file)
        else:
            merge_split_lines_advanced(input_file)