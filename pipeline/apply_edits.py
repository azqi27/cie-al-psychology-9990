#!/usr/bin/env python3
"""把题库校对后台导出的 qb-edits.json 应用回 data/questions/*.jsonl。

用法：
    python pipeline/apply_edits.py qb-edits.json
    python pipeline/apply_edits.py qb-edits.json --data data/questions

qb-edits.json 格式：
    {
      "edited_at": "2026-08-30T...",
      "edits": {
        "9990-2024m-12-q1a": {"topics": ["study.baron_cohen"], "type_facet": "sample"},
        "9990-2024s-11-q3":  {"topics": ["study.milgram", "study.piliavin"]}
      }
    }

每个题目的编辑项可包含：topics（实验标签数组）、type_facet（研究切面）、
command_words（命令词数组）、marks（分值数字）。只更新出现的字段，幂等可重复运行。
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.normpath(os.path.join(HERE, "..", "data", "questions"))


def load_edits(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    edits = data.get("edits", {})
    if not isinstance(edits, dict):
        raise SystemExit("edits 必须是对象 {id: {...}}")
    return edits


def apply_edits(edits, data_dir):
    if not os.path.isdir(data_dir):
        raise SystemExit(f"数据目录不存在: {data_dir}")
    files = sorted(f for f in os.listdir(data_dir) if f.endswith(".jsonl"))
    if not files:
        raise SystemExit(f"未找到任何 .jsonl: {data_dir}")

    changed_total = 0
    unmatched = set(edits.keys())

    for fn in files:
        path = os.path.join(data_dir, fn)
        out_lines = []
        file_changed = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                raw = line.rstrip("\n")
                if not raw.strip():
                    out_lines.append(raw)
                    continue
                try:
                    q = json.loads(raw)
                except json.JSONDecodeError:
                    out_lines.append(raw)
                    continue
                qid = q.get("id")
                if qid in edits:
                    unmatched.discard(qid)
                    e = edits[qid]
                    modified = False
                    if isinstance(e.get("topics"), list):
                        q["topics"] = e["topics"]
                        modified = True
                    if isinstance(e.get("type_facet"), str):
                        q["type_facet"] = e["type_facet"]
                        modified = True
                    if isinstance(e.get("command_words"), list):
                        q["command_words"] = e["command_words"]
                        modified = True
                    if e.get("marks") is not None:
                        q["marks"] = e["marks"]
                        modified = True
                    if modified:
                        file_changed += 1
                        changed_total += 1
                out_lines.append(json.dumps(q, ensure_ascii=False))
        if file_changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(out_lines) + "\n")
            print(f"  {fn}: 更新 {file_changed} 题")

    print(f"共更新 {changed_total} 题。")
    if unmatched:
        print(f"警告：以下 {len(unmatched)} 个 id 在数据中未找到，已忽略：")
        for u in sorted(unmatched):
            print(f"  - {u}")


def main():
    ap = argparse.ArgumentParser(description="应用题库校对修改回 JSONL 数据")
    ap.add_argument("edits", help="qb-edits.json 路径")
    ap.add_argument("--data", default=DEFAULT_DATA, help="data/questions 目录")
    args = ap.parse_args()
    edits = load_edits(args.edits)
    if not edits:
        print("edits 为空，无需改动。")
        return
    apply_edits(edits, args.data)


if __name__ == "__main__":
    main()
