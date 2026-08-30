# -*- coding: utf-8 -*-
"""
retag_approach.py — 一次性变换（idempotent）

需求 3：只问「assumption of approach」这类视角层面、不点名任何实验的题目，
不再关联到具体实验，而是关联到对应「视角(approach)」标签。

判定：某题 topics 恰好等于某视角下全部 3 篇实验（即 remap_clean 里 flag=approach_general 的产物）
-> 改写为单一 approach.<视角> 标签。

输入：data/questions/*.jsonl（git-as-db）
输出：原地覆盖；写 data/review/retag_approach.csv 记录被改动的题目。
"""
import os, re, json, glob, csv, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPROACH_STUDIES = {
    'biological': ['study.dement_kleitman', 'study.hassett', 'study.holzel'],
    'cognitive': ['study.andrade', 'study.baron_cohen', 'study.pozzulo'],
    'learning': ['study.bandura', 'study.fagen', 'study.saavedra_silverman'],
    'social': ['study.milgram', 'study.perry', 'study.piliavin'],
}
# 反向：3 实验集合 -> 视角
APPROACH_BY_SET = {frozenset(v): k for k, v in APPROACH_STUDIES.items()}


def main():
    dry = '--dry' in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, 'data', 'questions', '*.jsonl')))
    changed = []
    stats = {'in': 0, 'out': 0, 'retagged': 0}
    new_files_rows = []
    for f in files:
        rows = []
        with open(f, encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                stats['in'] += 1
                if r.get('paper', {}).get('no') == 1 and isinstance(r.get('topics'), list):
                    tops = frozenset(r['topics'])
                    # 已是 approach 标签则跳过（幂等）
                    if tops and all(t.startswith('approach.') for t in tops):
                        pass
                    elif tops in APPROACH_BY_SET:
                        ap = APPROACH_BY_SET[tops]
                        r['topics'] = [f'approach.{ap}']
                        stats['retagged'] += 1
                        changed.append({
                            'id': r['id'], 'approach': ap,
                            'text_preview': (r.get('text') or '')[:70].replace('\n', ' '),
                        })
                rows.append(r)
                stats['out'] += 1
        new_files_rows.append((f, rows))

    if dry:
        print('=== DRY RUN ===')
        print('in:', stats['in'], 'out:', stats['out'], 'retagged:', stats['retagged'])
        for c in changed:
            print(f"  [{c['id']}] -> approach.{c['approach']}  | {c['text_preview']}")
        return

    for f, rows in new_files_rows:
        with open(f, 'w', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.makedirs(os.path.join(ROOT, 'data', 'review'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'review', 'retag_approach.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['id', 'approach', 'text_preview'])
        w.writeheader()
        for c in changed:
            w.writerow(c)
    print('written. in:', stats['in'], 'out:', stats['out'], 'retagged:', stats['retagged'])


if __name__ == '__main__':
    main()
