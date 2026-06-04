# import os
# import subprocess
import pandas as pd
from fuzzywuzzy import fuzz
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox

# ===== 配置 =====
FILE_A = "<Your.xlsx To Be Fill ID>.xlsx"  # 你的A表文件名
FILE_B = "<Your.xlsx Imported CK-dialogueExportQuest.txt>.xlsx"  # 你的B表文件名
SHEET_A = 0
SHEET_B = 0
COL_A_TEXT = "<Lines(col's caption name)>"
COL_B_TEXT = "<Lines(col's caption name; Can be different)>"
COL_B_ID = "<Filename ID(col's caption name)>"
OUTPUT_FILE = "<.xlsx filename you want for Output(new .xlsx)>.xlsx"
SIMILARITY_THRESHOLD = 70  # 低于此值的不会进入人工确认（直接算失败）
AUTO_MATCH_THRESHOLD = 92  # 高于此值的自动确认，不弹窗


# =================

class DialogueMatcher:
    def __init__(self, dfA, dfB):
        self.dfA = dfA.copy()
        self.dfB = dfB.copy()
        self.used_b_indices = set()
        self.matches = {}  # {a_idx: (b_idx, bid)}

        # 初始化 tkinter
        self.root = tk.Tk()
        self.root.title("台词匹配确认")
        self.root.geometry("800x500")

    def preprocess(self):
        """数据预处理"""
        for df in [self.dfA, self.dfB]:
            df[COL_A_TEXT if df is self.dfA else COL_B_TEXT] = (
                df[COL_A_TEXT if df is self.dfA else COL_B_TEXT]
                    .astype(str).fillna("").str.strip()
            )
        if COL_B_ID in self.dfB.columns:
            self.dfB[COL_B_ID] = self.dfB[COL_B_ID].astype(str)

        # 为 A 表添加 ID 列
        if "ID" not in self.dfA.columns:
            self.dfA.insert(0, "ID", "")

    def match_exact_same_in_order(self):
        """完全相同台词按顺序匹配"""
        exact_map = defaultdict(list)
        for idx, text in enumerate(self.dfB[COL_B_TEXT]):
            if text:
                exact_map[text].append(idx)

        # 统计每个相同台词在 A 中出现的次数，按顺序取 B
        for text, b_indices in exact_map.items():
            a_indices = [idx for idx, row in self.dfA.iterrows()
                         if row[COL_A_TEXT] == text and idx not in self.matches]
            # 按顺序一一对应
            for a_idx, b_idx in zip(a_indices, b_indices):
                if b_idx not in self.used_b_indices:
                    self.matches[a_idx] = (b_idx, self.dfB.at[b_idx, COL_B_ID])
                    self.used_b_indices.add(b_idx)

    def fuzzy_candidates(self, a_text, b_candidates):
        """返回按相似度排序的候选B列表"""
        scores = []
        for b_idx, b_text, bid in b_candidates:
            score = fuzz.token_sort_ratio(a_text, b_text)
            scores.append((score, b_idx, b_text, bid))
        scores.sort(reverse=True)
        return scores[:5]  # 最多返回5个候选

    def ask_user_choice(self, a_idx, a_text, candidates):
        """弹窗让用户选择"""
        dialog = tk.Toplevel(self.root)
        dialog.title("选择匹配的台词")
        dialog.geometry("900x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # 说明标签
        tk.Label(dialog, text=f"请为以下 A 台词选择匹配的 B 台词：",
                 font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(dialog, text=f"「{a_text}」", font=("Arial", 11),
                 fg="blue", wraplength=800).pack(pady=5)

        # 候选列表
        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, height=8,
                             font=("Arial", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 添加选项
        listbox.insert(tk.END, "━━━━ 跳过此条（稍后手动处理）━━━━")
        for i, (score, b_idx, b_text, bid) in enumerate(candidates, 1):
            display = f"[相似度 {score}] ID: {bid} | 台词: {b_text[:100]}"
            listbox.insert(tk.END, display)
            # 存储额外信息
            if not hasattr(listbox, 'candidates_data'):
                listbox.candidates_data = []
            listbox.candidates_data.append((b_idx, bid))

        result = [None]

        def on_select():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                if idx == 0:  # 跳过
                    result[0] = ("skip", None, None)
                else:
                    b_idx, bid = listbox.candidates_data[idx - 1]
                    result[0] = ("match", b_idx, bid)
                dialog.destroy()
            else:
                messagebox.showwarning("提示", "请先选择一个选项")

        tk.Button(dialog, text="确 定", command=on_select,
                  font=("Arial", 11), bg="#4CAF50", fg="white",
                  padx=20, pady=5).pack(pady=15)

        self.root.wait_window(dialog)
        return result[0]

    def run_interactive_matching(self):
        """交互式匹配主流程"""
        # 1. 获取未匹配的A和B
        all_a_indices = [idx for idx in self.dfA.index
                         if idx not in self.matches and self.dfA.at[idx, COL_A_TEXT] != ""]

        remaining_b = [(idx, self.dfB.at[idx, COL_B_TEXT], self.dfB.at[idx, COL_B_ID])
                       for idx in self.dfB.index if idx not in self.used_b_indices
                       and self.dfB.at[idx, COL_B_TEXT] != ""]

        for a_idx in all_a_indices:
            a_text = self.dfA.at[a_idx, COL_A_TEXT]

            # 计算候选
            candidates = self.fuzzy_candidates(a_text, remaining_b)
            if not candidates:
                continue

            best_score, best_b_idx, best_b_text, best_bid = candidates[0]

            # 高相似度自动确认
            if best_score >= AUTO_MATCH_THRESHOLD:
                self.matches[a_idx] = (best_b_idx, best_bid)
                self.used_b_indices.add(best_b_idx)
                remaining_b = [(i, t, bid) for i, t, bid in remaining_b if i != best_b_idx]
                print(f"自动匹配: '{a_text}' → {best_bid} (相似度 {best_score})")
                continue

            # 需要人工确认
            choice, b_idx, bid = self.ask_user_choice(a_idx, a_text, candidates)

            if choice == "match":
                self.matches[a_idx] = (b_idx, bid)
                self.used_b_indices.add(b_idx)
                remaining_b = [(i, t, bid) for i, t, bid in remaining_b if i != b_idx]
                print(f"人工确认: '{a_text}' → {bid}")
            else:
                print(f"跳过: '{a_text}'")

        self.root.destroy()

    def apply_matches(self):
        """将匹配结果写回 dfA"""
        for a_idx, (b_idx, bid) in self.matches.items():
            self.dfA.at[a_idx, "ID"] = bid

    def export_results(self):
        """导出结果"""
        self.dfA.to_excel(OUTPUT_FILE, index=False)

        unmatched_a = self.dfA[(self.dfA["ID"] == "") & (self.dfA[COL_A_TEXT] != "")]
        unused_b = self.dfB[~self.dfB.index.isin(self.used_b_indices)]

        print(f"\n✅ 匹配完成：{len(self.matches)} / {len(self.dfA)}")
        print(f"⚠️ 未匹配的A台词数：{len(unmatched_a)}")
        print(f"📋 未使用的B台词数：{len(unused_b)}")

        if len(unmatched_a) > 0:
            unmatched_a.to_excel("未匹配的A台词.xlsx", index=False)
            print("未匹配的A台词已导出到：未匹配的A台词.xlsx")
        if len(unused_b) > 0:
            unused_b.to_excel("未使用的B台词.xlsx", index=False)
            print("未使用的B台词已导出到：未使用的B台词.xlsx")

        print(f"\n主结果已保存到：{OUTPUT_FILE}")

    def run(self):
        self.preprocess()
        self.match_exact_same_in_order()
        self.run_interactive_matching()
        self.apply_matches()
        self.export_results()

# subprocess.run(["pipreqs", os.path.dirname(__file__), "--force"])

# ===== 主程序 =====
if __name__ == "__main__":
    print("正在加载表格...")
    dfA = pd.read_excel(FILE_A, sheet_name=SHEET_A)
    dfB = pd.read_excel(FILE_B, sheet_name=SHEET_B)

    matcher = DialogueMatcher(dfA, dfB)
    matcher.run()

    input("\n按回车键退出...")