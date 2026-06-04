# import subprocess
import os
import re
import shutil
import pandas as pd
from fuzzywuzzy import fuzz
from pathlib import Path

# ===== 配置 =====
EXCEL_FILE = "<Your.xlsx contain Lines and ID in difn col>.xlsx"
SHEET_NAME = 0
COL_DIALOGUE = "<Lines(col's caption name)>"
COL_ID = "<Filename ID(col's caption name)>"

WAV_DIR = "./wav_files"
OUTPUT_DIR = "./sorted_by_role"

# 完整的角色列表（包括三字母缩写）
ROLE_NAMES = [
    "ActorName1", "ActorName2", "ActorName3", "ActorName4"
]
THREE_LETTER_CODES = ["ActorNameAbbr1", "ActorNameAbbr2", "ActorNameAbbr4"]  # 请根据实际补充
ALL_ROLES = ROLE_NAMES + THREE_LETTER_CODES

SIMILARITY_THRESHOLD = 80


# =========================

def normalize_text(text):
    # SFRMOD 先把省略号 ... 转成单点
    text = re.sub(r'\.{2,}', '.', text)
    """标准化：小写、去标点（保留字母数字和空格）"""
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_role_and_dialogue(filename, known_roles):
    """
    关键改进：角色名后面必须紧跟着 '-'
    返回 (角色, 台词原文)
    """
    name = filename.rsplit('.', 1)[0]

    for role in sorted(known_roles, key=len, reverse=True):
        idx = name.find(role)
        if idx == -1:
            continue

        after_role = idx + len(role)
        if after_role >= len(name):
            continue

        # 关键：角色名后面必须是 '-'
        if name[after_role] == '-':
            dialogue = name[after_role + 1:]
            return role, dialogue

    # 备用方案：如果已知角色都没匹配到，尝试启发式（找最后一个 '-'）
    if '-' in name:
        last_hyphen = name.rfind('-')
        # 尝试把最后一个 '-' 前面的部分当作角色
        potential_role = name[:last_hyphen]
        # 从右向左取连续的字母、下划线、短横作为角色名（简单处理）
        role_match = re.search(r'[\w_-]+$', potential_role)
        if role_match:
            role = role_match.group()
            dialogue = name[last_hyphen + 1:]
            return role, dialogue

    return None, None


def load_id_mapping(excel_path, sheet_name, col_dialogue, col_id):
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df[col_dialogue] = df[col_dialogue].astype(str).fillna("").str.strip()

    mapping = {}
    for _, row in df.iterrows():
        raw = row[col_dialogue]
        if raw:
            norm = normalize_text(raw)
            if norm not in mapping:
                mapping[norm] = row[col_id]
    return mapping, df


def find_best_match(dialogue_raw, mapping, threshold):
    norm_input = normalize_text(dialogue_raw)
    if norm_input in mapping:
        return mapping[norm_input], 100

    best_score = 0
    best_id = None
    for norm_ref, ref_id in mapping.items():
        score = fuzz.token_sort_ratio(norm_input, norm_ref)
        if score > best_score:
            best_score = score
            best_id = ref_id

    if best_score >= threshold:
        return best_id, best_score
    return None, best_score


def main():
    print("加载 Excel 映射...")
    mapping, df = load_id_mapping(EXCEL_FILE, SHEET_NAME, COL_DIALOGUE, COL_ID)
    print(f"共 {len(mapping)} 条台词映射")

    wav_dir = Path(WAV_DIR)
    if not wav_dir.exists():
        print(f"目录不存在: {WAV_DIR}")
        return

    wav_files = list(wav_dir.glob("*.wav")) + list(wav_dir.glob("*.WAV"))
    print(f"找到 {len(wav_files)} 个 wav 文件")

    success = 0
    fail = 0
    fail_details = []

    for wav_path in wav_files:
        filename = wav_path.name
        print(f"\n处理: {filename}")

        role, dialogue_raw = extract_role_and_dialogue(filename, ALL_ROLES)
        if not role or not dialogue_raw:
            print(f"  失败：无法提取角色或台词")
            fail += 1
            fail_details.append((filename, "角色/台词提取失败"))
            continue

        print(f"  角色: {role}")
        print(f"  台词: {dialogue_raw[:80]}...")

        matched_id, score = find_best_match(dialogue_raw, mapping, SIMILARITY_THRESHOLD)
        if not matched_id:
            print(f"  匹配失败 (最高相似度 {score})")
            fail += 1
            fail_details.append((filename, f"匹配失败 ({score})"))
            continue

        print(f"  匹配 ID: {matched_id} (相似度 {score})")

        role_dir = Path(OUTPUT_DIR) / role
        role_dir.mkdir(parents=True, exist_ok=True)

        new_name = f"{matched_id}.wav"
        new_path = role_dir / new_name
        counter = 1
        while new_path.exists():
            new_name = f"{matched_id}_{counter}.wav"
            new_path = role_dir / new_name
            counter += 1

        shutil.move(str(wav_path), str(new_path))
        print(f"  已移至: {new_path}")
        success += 1

    print("\n" + "=" * 50)
    print(f"成功: {success}, 失败: {fail}")
    if fail_details:
        print("\n失败列表：")
        for fn, reason in fail_details:
            print(f"  {fn} -> {reason}")
        pd.DataFrame(fail_details, columns=["文件名", "原因"]).to_excel("rename_failures.xlsx", index=False)
        print("\n失败清单已保存至 rename_failures.xlsx")

# subprocess.run(["pipreqs", os.path.dirname(__file__), "--force"])

if __name__ == "__main__":
    main()