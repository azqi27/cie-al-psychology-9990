#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_questions.py — 题目正文清洗（幂等，可重复运行）

目标（来自用户校对需求）：
  1) 题干里仍残留的卷面冗余信息（页脚、页码、分值标记等）清洗掉；
  2) 题干末尾没有句号的，补一个句号；
  3) 题目内容里仍带的开头题号，删除；
  4) 大题干(stem_text)如果“只有题号、没有正文”，清空它（小题号由卡片上的 (a)(b) 呈现）。

只修改 text / stem_text 两个字段，其余字段原样保留。
仅当内容确有变化时重写该行，避免无谓的大 diff。
"""
import json
import glob
import os
import re
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions')

# —— 冗余卷面信息的整段/片段移除（大小写不敏感）——
REDUNDANT_PATTERNS = [
    r'For Examiner’?s Use',
    r'Turn over',
    r'BLANK PAGE',
    r'© UCLES',
    r'UCLES',
    r'Cambridge (International )?Assessment',
    r'Cambridge International',
    r'Total \d+ marks?',
    r'—\s*\d+\s*—',          # 页码 —— 12 ——
    r'Page \d+',
    r'\[ DO NOT WRITE \]',
    r'DO NOT WRITE',
]

# 结尾残留的分值标记，如 " 1" 或 " [4]" 或 " (4 marks)"
TRAILING_MARK = re.compile(r'(?:\s*\[\s*\d{1,2}\s*(?:marks?)?\s*\]|\s*[\(\[]?\d{1,2}\s*\)?)\s*$', re.IGNORECASE)
# 开头题号，如 "5 " "5. " "12) "
LEADING_NUM = re.compile(r'^\s*\d{1,3}\s*[.)]?\s*')
# 仅由数字组成的“大题干”（只含题号）
NUMERIC_ONLY = re.compile(r'^\d+$')


def strip_redundant(s: str) -> str:
    for pat in REDUNDANT_PATTERNS:
        s = re.sub(pat, ' ', s, flags=re.IGNORECASE)
    return s


def add_period(s: str) -> str:
    s = s.rstrip()
    if not s:
        return s
    # 已以句末标点结束则不补
    if s[-1] in '.!?)}\"”’»…':
        return s
    return s + '.'


def clean_field(s: str, part: str | None = None) -> str:
    if s is None:
        return ''
    s = strip_redundant(s)
    # 去结尾残留分值
    s = TRAILING_MARK.sub('', s).strip()
    # 去开头题号（仅数字列表号）
    s = LEADING_NUM.sub('', s).strip()
    # 若正文开头仍带着小题号（如 "(a) "），且能对应上本题 part，则去掉，避免与卡片 (a) 重复
    if part:
        for pat in [rf'^\(?{re.escape(part)}\)?\.\s*', rf'^\(?{re.escape(part)}\)?\s*']:
            s = re.sub(pat, '', s).strip()
    # 合并多余空白
    s = re.sub(r'\s+', ' ', s).strip()
    # 补句号
    s = add_period(s)
    return s


def clean_stem(s: str) -> str:
    if s is None:
        return ''
    s = strip_redundant(s)
    s = TRAILING_MARK.sub('', s).strip()
    s = LEADING_NUM.sub('', s).strip()
    s = re.sub(r'\s+', ' ', s).strip()
    # 大题干若“只有题号没有正文”，清空（小题号由卡片 (a)(b) 呈现）
    if NUMERIC_ONLY.match(s):
        return ''
    return s


def main():
    dry = '--dry' in sys.argv
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.jsonl')))
    total = changed = 0
    for f in files:
        out_lines = []
        file_changed = False
        with open(f, encoding='utf-8') as fh:
            for raw in fh:
                line = raw.rstrip('\n')
                if not line.strip():
                    out_lines.append(line)
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    out_lines.append(line)
                    continue
                total += 1
                orig_text = obj.get('text', '')
                orig_stem = obj.get('stem_text', '')
                new_text = clean_field(orig_text, obj.get('part'))
                new_stem = clean_stem(orig_stem)
                if new_text != orig_text or new_stem != orig_stem:
                    changed += 1
                    file_changed = True
                    obj['text'] = new_text
                    obj['stem_text'] = new_stem
                    out_lines.append(json.dumps(obj, ensure_ascii=False))
                else:
                    out_lines.append(line)
        if file_changed and not dry:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(out_lines) + '\n')
    print(f"[clean_questions] scanned={total} changed={changed} dry={dry}")


if __name__ == '__main__':
    main()
