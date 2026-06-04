import os
# import subprocess
from collections import defaultdict


def rename_files_by_first_word(folder_path, start_number=0):
    """
    重命名文件夹中的文件
    规则：
    1. 按第一个单词（_前）精确匹配分组
    2. 每组内保持原文件顺序（按原文件名排序）
    3. 在第一个单词后面插入数字（递增，不循环）

    示例：Crouch_xxx.hwk -> Crouch0_xxx.hwk (第1个)
                              Crouch1_xxx.hwk (第2个)
                              Crouch2_xxx.hwk (第3个)
    """
    if not os.path.exists(folder_path):
        print(f"错误：文件夹 {folder_path} 不存在")
        return

    # 获取所有文件
    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    # 按第一个单词精确分组
    groups = defaultdict(list)

    for filename in files:
        name_without_ext, ext = os.path.splitext(filename)
        # 获取第一个单词（_前面的部分）
        parts = name_without_ext.split('_')
        first_word = parts[0]
        rest = '_'.join(parts[1:]) if len(parts) > 1 else ''

        groups[first_word].append((filename, first_word, rest, ext))

    # 记录重命名映射
    rename_mapping = {}
    total_renamed = 0

    # 按第一个单词排序处理（保证输出顺序清晰）
    for first_word, file_list in sorted(groups.items()):
        # 保持原文件顺序（按原文件名排序）
        file_list.sort(key=lambda x: x[0])

        print(f"\n【分组: '{first_word}'】共 {len(file_list)} 个文件")

        for idx, (old_name, first_word, rest, ext) in enumerate(file_list):
            number = start_number + idx  # 递增，不循环

            # 在第一个单词后面插入数字
            new_first_word = first_word + str(number)

            # 重建新文件名
            if rest:
                new_name_without_ext = new_first_word + '_' + rest
            else:
                new_name_without_ext = new_first_word

            new_name = new_name_without_ext + ext

            if new_name != old_name:
                rename_mapping[old_name] = new_name
                print(f"  {old_name:50} -> {new_name}")
                total_renamed += 1
            else:
                print(f"  {old_name:50} -> (无需修改)")

    # 执行重命名
    if not rename_mapping:
        print("\n没有需要重命名的文件。")
        return

    print(f"\n{'=' * 70}")
    print(f"开始执行重命名...")

    success_count = 0
    for old_name, new_name in rename_mapping.items():
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)

        # 检查目标文件是否已存在
        if os.path.exists(new_path):
            print(f"  跳过：{new_name} 已存在，无法重命名 {old_name}")
            continue

        try:
            os.rename(old_path, new_path)
            success_count += 1
        except Exception as e:
            print(f"  失败：{old_name} -> {e}")

    print(f"\n✅ 完成！成功重命名 {success_count} / {total_renamed} 个文件")


def preview_changes(folder_path, start_number=0):
    """
    预览重命名效果，不实际执行
    """
    if not os.path.exists(folder_path):
        print(f"错误：文件夹 {folder_path} 不存在")
        return

    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    groups = defaultdict(list)

    for filename in files:
        name_without_ext, ext = os.path.splitext(filename)
        parts = name_without_ext.split('_')
        first_word = parts[0]
        rest = '_'.join(parts[1:]) if len(parts) > 1 else ''
        groups[first_word].append((filename, first_word, rest, ext))

    print("\n========== 预览重命名效果 ==========\n")

    for first_word, file_list in sorted(groups.items()):
        file_list.sort(key=lambda x: x[0])
        print(f"\n【分组: '{first_word}'】共 {len(file_list)} 个文件")

        for idx, (old_name, first_word, rest, ext) in enumerate(file_list):
            number = start_number + idx

            new_first_word = first_word + str(number)

            if rest:
                new_name_without_ext = new_first_word + '_' + rest
            else:
                new_name_without_ext = new_first_word

            new_name = new_name_without_ext + ext

            if new_name != old_name:
                print(f"  {old_name:50} -> {new_name}")
            else:
                print(f"  {old_name:50} -> (不变)")

# subprocess.run(["pipreqs", os.path.dirname(__file__), "--force"])

if __name__ == "__main__":
    folder = input("请输入文件夹路径: ").strip()

    print("\n选择起始数字：")
    print("1. 从0开始 (0, 1, 2, 3...)")
    print("2. 从1开始 (1, 2, 3, 4...)")
    start_choice = input("请选择 (1/2，默认1): ").strip()

    start_number = 0 if start_choice == '1' else 1

    print("\n选择操作模式：")
    print("1. 预览模式（只查看效果，不实际重命名）")
    print("2. 执行模式（实际重命名文件）")
    mode = input("请选择 (1/2，默认1): ").strip()

    if mode == '2':
        confirm = input(f"\n⚠️  确认要执行重命名吗？(起始数字={start_number}) (yes/no): ").strip().lower()
        if confirm == 'yes':
            rename_files_by_first_word(folder, start_number)
        else:
            print("已取消操作。")
    else:
        preview_changes(folder, start_number)