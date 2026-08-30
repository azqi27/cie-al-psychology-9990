# -*- coding: utf-8 -*-
"""
remap_clean.py — 一次性变换脚本（transform, idempotent）
作用（对应网站 7 项调整）：
  req3: 把 topics 维度从「视角/研究/辩论」统一收敛为「仅 12 篇核心实验」；
        通过 (1) 研究者姓氏(含变音归一) (2) 研究内容关键词 (3) 视角级题目回溯到该视角下全部实验
        实现「每道 P1 题都对应 ≥1 个实验」；对比题(两个具名实验)→ 可多选(两个都标)。
  req6: 清洗题干文本：去点阵填空行、页码/UCLES 页脚、DO NOT WRITE/FOR EXAMINER'S USE/TURN OVER、
        行尾 [n] 分值、修复 PDF 导致的不必要换行。
  （req1/2/4/5/7 的文本标签在 taxonomy.ts / loadQuestions.ts / index.astro 中处理，本脚本只产出干净数据）

输入：data/questions/*.jsonl（git-as-db）
输出：原地覆盖同一批 jsonl；并写 data/review/remap_pending.csv 供人工复核。
"""
import os, re, json, glob, csv, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- 文本清洗 (req6) ----------------
ANSWER_LINE = re.compile(r'^[\s.\-_·‐‑‒–—_{}()\[\]]+$')   # 纯点阵/下划线/括号行
NOISE = re.compile(r'UCLES|Turn over|©|Cambridge International|For Examiner|Examiner.{0,6}Use|'
                   r'DO NOT WRITE|Blank page|This page is intentionally|www\.Cambridge|'
                   r'Maximum mark|Total .{0,4}\d{1,3}|Question\s*\d+\s*\(', re.I)
MARK_RE = re.compile(r'\[\s*\d{1,2}\s*\]')

def clean_text(s: str) -> str:
    if not s:
        return ''
    # 截掉答案下划线(8+连续点)之后的所有内容（含二进制残骸 * 数字 *）
    s = re.split(r'\.{8,}', s, maxsplit=1)[0]
    s = re.sub(r'\*\s*\d{4,}\s*\*', ' ', s)   # 孤立的 * 0000800000006 * 残骸
    lines = s.split('\n')
    out = []
    for ln in lines:
        t = ln.replace('\r', '').strip()
        # 去掉点阵/下划线填空行
        if ANSWER_LINE.match(t):
            continue
        # 去掉噪声行
        if NOISE.search(t):
            continue
        out.append(t)
    # 合并为一段，修复 PDF 列宽导致的不必要换行
    txt = ' '.join(out)
    txt = MARK_RE.sub('', txt)          # 去掉行尾 [n] 分值
    txt = re.sub(r'\s+', ' ', txt).strip()
    # 去掉残留首尾标点/括号
    txt = txt.strip(' .-_')
    return txt

# ---------------- 实验映射 (req3) ----------------
def norm(s: str) -> str:
    s = s.lower()
    s = s.replace('ö', 'oe').replace('ä', 'ae').replace('ü', 'ue').replace('ß', 'ss')
    return s

# (1) 研究者姓氏（含变音归一后的键）
SURNAMES = {
    'dement': 'study.dement_kleitman', 'kleitman': 'study.dement_kleitman',
    'hassett': 'study.hassett',
    'holzel': 'study.holzel', 'hoelzel': 'study.holzel',
    'andrade': 'study.andrade',
    'baron': 'study.baron_cohen', 'cohen': 'study.baron_cohen',
    'pozzulo': 'study.pozzulo',
    'bandura': 'study.bandura',
    'fagen': 'study.fagen',
    'saavedra': 'study.saavedra_silverman', 'silverman': 'study.saavedra_silverman',
    'milgram': 'study.milgram',
    'perry': 'study.perry',
    'piliavin': 'study.piliavin',
}
# (2) 研究内容关键词（高精确，避免误命中）
CONTENT = {
    'study.dement_kleitman': ['rem sleep', 'rem was', 'rem ', 'dream', 'eeg', 'eye movement'],
    'study.holzel': ['mindfulness', 'meditat', 'ffmq', 'five facet', 'body scan', 'mbsr',
                     'mindful', 'cannot relax', 'feel stressed', 'relax more', 'workers relax',
                     'help its workers', 'stress reduction'],
    'study.hassett': ['toy preference', 'vervet', 'monkey', 'sex difference', 'gender difference'],
    'study.andrade': ['doodl', 'daydream'],
    'study.baron_cohen': ['eyes test', 'reading the mind', 'autism', ' asd', 'hfa',
                          'sally-anne', 'sally anne', 'mind-blind', 'mindblind'],
    'study.pozzulo': ['line-up', 'lineup', 'eyewitness', 'identified from a line', 'line-up'],
    'study.bandura': ['bobo', 'aggression', 'imitation'],
    'study.fagen': ['elephant'],
    'study.saavedra_silverman': ['button', 'phobia', 'fear of'],
    'study.milgram': ['obedience', 'shock', 'authority'],
    'study.perry': ['personal space'],
    'study.piliavin': ['subway', 'bystander', 'emergency', 'new york'],
}
# 每个视角下的实验集合（视角级题目回溯用）
APPROACH_STUDIES = {
    'biological': ['study.dement_kleitman', 'study.hassett', 'study.holzel'],
    'cognitive': ['study.andrade', 'study.baron_cohen', 'study.pozzulo'],
    'learning': ['study.bandura', 'study.fagen', 'study.saavedra_silverman'],
    'social': ['study.milgram', 'study.perry', 'study.piliavin'],
}
APPROACH_KW = {
    'biological': ['biological approach', 'biological'],
    'cognitive': ['cognitive approach', 'cognitive'],
    'learning': ['learning approach', 'learning'],
    'social': ['social approach', 'social'],
}
ALL_STUDIES = [s for v in APPROACH_STUDIES.values() for s in v]

def detect_studies(text: str, stem: str):
    """返回 (named_studies:set, approach_studies:set, flags:list)
    named = 通过姓氏/内容关键词命中的实验；approach = 视角级题目回溯到的该视角全部实验。"""
    blob = norm(text + ' ' + stem)
    named = set()
    flags = []
    # (1) 姓氏
    for tok, tid in SURNAMES.items():
        if re.search(r'\b' + re.escape(tok), blob):
            named.add(tid)
    # (2) 内容关键词
    for tid, kws in CONTENT.items():
        if any(k in blob for k in kws):
            named.add(tid)
    # —— 视角级题目回溯 ——
    approach_hit = None
    for ap, kws in APPROACH_KW.items():
        if any(k in blob for k in kws):
            approach_hit = ap
            break
    approach_studies = set()
    if not named and approach_hit:
        # 纯视角题（如 "Outline one assumption of the X approach"）→ 回溯到该视角下全部实验
        approach_studies = set(APPROACH_STUDIES[approach_hit])
        flags.append(f'approach_general:{approach_hit}')
    # —— 对比题：两个具名实验 → 多选 ——
    if len(named) >= 2:
        flags.append('multi_study')
    return named, approach_studies, flags

def is_garbage(text: str) -> bool:
    """丢弃 PDF 抽取残骸：无字母、或大量非 ASCII 乱码。"""
    if not re.search(r'[A-Za-z]', text):
        return True
    if len(text) > 12:
        non_ascii = sum(1 for ch in text if ord(ch) > 127)
        if non_ascii / len(text) > 0.3:
            return True
    return False

def main():
    dry = '--dry' in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, 'data', 'questions', '*.jsonl')))
    pending = []
    stats = {'total_in': 0, 'total_out': 0, 'dropped_empty': 0,
             'study_dist': {}, 'multi': 0, 'approach_general': 0, 'unmapped': 0}
    new_files_rows = []
    for f in files:
        rows = []
        with open(f, encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                stats['total_in'] += 1
                # 清洗文本 (req6)
                r['stem_text'] = clean_text(r.get('stem_text', ''))
                r['text'] = clean_text(r.get('text', ''))
                # 丢弃纯噪声/空叶子 / 二进制乱码（PDF 抽取残骸）。
                # 仅以题干正文(text)判定：stem 可能只是题号(如 "5")，不含字母属正常。
                if is_garbage(r['text']):
                    stats['dropped_empty'] += 1
                    continue
                if r['paper']['no'] == 1:
                    named, approach_studies, flags = detect_studies(r['text'], r['stem_text'])
                    studies = named if named else approach_studies
                    if not studies:
                        # 极端兜底：仍无实验 → 标记待复核并留空
                        stats['unmapped'] += 1
                        flags.append('UNMAPPED')
                    r['topics'] = sorted(studies)
                    # 置信度标注
                    if 'UNMAPPED' in flags:
                        r.setdefault('confidence', {})['topic'] = 0.0
                    elif 'approach_general' in flags:
                        r.setdefault('confidence', {})['topic'] = 0.4
                    elif named and all(t in named for t in studies):
                        r.setdefault('confidence', {})['topic'] = 0.9 if any(
                            re.search(r'\b' + re.escape(tok), norm(r['text'] + ' ' + r['stem_text']))
                            for tok in SURNAMES) else 0.8
                    else:
                        r.setdefault('confidence', {})['topic'] = 0.8
                    if 'multi_study' in flags:
                        stats['multi'] += 1
                    if 'approach_general' in flags:
                        stats['approach_general'] += 1
                    for s in r['topics']:
                        stats['study_dist'][s] = stats['study_dist'].get(s, 0) + 1
                    if flags:
                        pending.append({
                            'id': r['id'], 'paper': f"P{r['paper']['no']}",
                            'q': f"q{r['q_no']}{r['part'] or ''}{('_'+r['subpart']) if r['subpart'] else ''}",
                            'topics': ';'.join(r['topics']), 'flags': ';'.join(flags),
                            'text_preview': r['text'][:70].replace('\n', ' '),
                        })
                rows.append(r)
                stats['total_out'] += 1
        new_files_rows.append((f, rows))

    if dry:
        print("=== DRY RUN ===")
        print("in:", stats['total_in'], "out:", stats['total_out'], "dropped_empty:", stats['dropped_empty'])
        print("multi_study:", stats['multi'], "approach_general:", stats['approach_general'], "unmapped:", stats['unmapped'])
        print("study distribution (P1, multi counted per study):")
        for s, c in sorted(stats['study_dist'].items(), key=lambda x: -x[1]):
            print(f"  {s}: {c}")
        print("\n--- unmapped / approach_general samples ---")
        for p in pending:
            if 'UNMAPPED' in p['flags'] or 'approach_general' in p['flags']:
                print(f"  [{p['id']}] {p['flags']} -> {p['topics']}")
                print(f"     {p['text_preview']}")
        return

    # 写回
    for f, rows in new_files_rows:
        with open(f, 'w', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.makedirs(os.path.join(ROOT, 'data', 'review'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'review', 'remap_pending.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['id', 'paper', 'q', 'topics', 'flags', 'text_preview'])
        w.writeheader()
        for p in pending:
            w.writerow(p)
    print("written. in:", stats['total_in'], "out:", stats['total_out'], "dropped_empty:", stats['dropped_empty'])
    print("multi:", stats['multi'], "approach_general:", stats['approach_general'], "unmapped:", stats['unmapped'])

if __name__ == '__main__':
    main()
