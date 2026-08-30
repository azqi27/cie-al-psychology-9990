# -*- coding: utf-8 -*-
"""
9990 公益题库 — 解析管线 (Pipeline L0–L3)
把 2024–2026 考纲的 P1/P2 真题 PDF 解析为结构化题目记录。

输出:
  data/questions/{series}_{paper}{variant}.jsonl   每卷一个文件，每行一道叶子题
  data/review/pending.csv                          待人工复核队列
  reports/validation_2024_2026.json                校验报告(含总分 checksum)

质检: 每卷所有叶子题 [n] 分值之和必须等于官方总分 60；不符则标记校验失败。
"""
import os, re, json, glob, csv, sys
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS   = "E:/Work/学为贵/心理学"
PY   = "C:/Users/27725/.workbuddy/binaries/python/envs/default/Scripts/python.exe" if False else None

# ---------- 文件名解析 ----------
NAME_RE = re.compile(r'9990_([msw])(\d\d)_qp_([12])(\d)\.pdf$', re.I)
SESSION_LABEL = {'m': 'February/March', 's': 'May/June', 'w': 'October/November'}

def parse_name(path):
    b = os.path.basename(path)
    m = NAME_RE.search(b)
    if not m: return None
    sess, yy, paper, variant = m.groups()
    year = 2000 + int(yy)
    if year not in (2024, 2025, 2026): return None
    if paper not in ('1', '2'): return None
    return dict(basename=b, session=sess, year=year, paper=int(paper),
                variant=int(variant),
                series=f"9990-{year}{sess}",
                session_label=SESSION_LABEL[sess])

def discover():
    """递归找全部 9990 qp PDF，按文件名去重（优先 CIE/真题 目录）。"""
    hits = glob.glob(os.path.join(WS, '**', '9990_*_qp_*.pdf'), recursive=True)
    best = {}
    for h in hits:
        meta = parse_name(h)
        if not meta: continue
        b = meta['basename']
        if b in best:
            # 优先 CIE/真题
            if ('CIE/真题' in h or 'CIE\\真题' in h) and ('CIE/真题' not in best[b] and 'CIE\\真题' not in best[b]):
                best[b] = h
        else:
            best[b] = h
    return best

# ---------- 文本与切题 ----------
SEC_RE = re.compile(r'Section\s+([ABC])\b', re.I)
# 字母题号限定 [a-h]；[i,v,x]+ 视为罗马子题（(i)(ii)(iii)），避免层级错乱
MARKER_RE = re.compile(r'(?<![A-Za-z0-9])\((([a-h])|([ivx]+))\)(?![A-Za-z0-9])')
MARK_RE = re.compile(r'\[\s*(\d{1,2})\s*\]')

def extract_text(pdf_path):
    try:
        return '\n'.join((p.extract_text() or '') for p in PdfReader(pdf_path).pages)
    except Exception as e:
        return f"__EXTRACT_ERROR__{e}"

def _is_empty(txt):
    return not re.sub(r'[\s.]+', '', txt)

def split_leaves(block, base=0):
    """逐标记独立成叶子：每个 (a)/(i)/(ii) 都拥有自己的文本段与 span，
    保证每一处 [n] 都落在某叶子的 span 内（总分 checksum 不丢分）。
    子题标记在 PDF 抽取中偶发丢失时，其分值并入最近的父级叶子，不再丢失。"""
    ms = list(MARKER_RE.finditer(block))
    if not ms:
        return [("", "", block, base, base + len(block))]
    leaves = []
    # 首标记之前的引导文本：若本身带分值（如 "3 The table shows... [2]" 后接 (a)(b)），单独成叶子
    pre = block[:ms[0].start()]
    if MARK_RE.search(pre) and not _is_empty(pre):
        leaves.append(("", "", pre, base, base + len(pre)))
    last_part = ""
    for i, m in enumerate(ms):
        start = m.end()
        end = ms[i+1].start() if i+1 < len(ms) else len(block)
        letter, roman = m.group(2), m.group(3)
        seg = block[start:end]
        if letter:                      # [a-h] 字母题号 → 顶层 part
            last_part = letter
            if not _is_empty(seg):
                leaves.append((letter, "", seg, base + start, base + end))
        else:                          # 罗马数字 → 子题，归到最近 part
            if not _is_empty(seg):
                leaves.append((last_part, roman, seg, base + start, base + end))
    return leaves

def parse_paper(text):
    # 章节
    secs = [(m.start(), m.group(1).upper()) for m in SEC_RE.finditer(text)]
    # 顶层题号（数字+空格+字母/左括号）
    qre = re.compile(r'(?m)^[ \t]*(\d{1,2})[ \t]+(?=[A-Za-z(])')
    qs = list(qre.finditer(text))
    # 去掉信息区以前的假题号：从第一个 Section 之后开始
    start_from = secs[0][0] if secs else 0
    qs = [q for q in qs if q.start() >= start_from]
    questions = []
    for i, q in enumerate(qs):
        qno = q.group(1)
        end = qs[i+1].start() if i+1 < len(qs) else len(text)
        block = text[q.start():end]
        # 章节归属
        sec = ''
        for sp, sl in secs:
            if sp <= q.start(): sec = sl
        # stem = 第一个题号标记之前
        pm = MARKER_RE.search(block)
        stem = block[:pm.start()].strip() if pm else block.strip()
        stem = re.sub(r'^\d{1,2}[ \t]+', '', stem).strip()
        leaves = split_leaves(block, q.start())
        block_total = sum(int(x) for x in MARK_RE.findall(block))
        owns, cleaned = [], []
        for part, sub, seg, lstart, lend in leaves:
            seg_clean = seg.strip()
            cleaned.append(seg_clean)
            marks = MARK_RE.findall(seg)
            owns.append(int(marks[-1]) if marks else None)
        # 整题层面余额分配：把题内总分平分给仍为 None 的真实计分题（非空且文本较长），
        # 保住每卷 60 分校验，同时给每题一个可用分值（标 distributed 供复核）。
        sum_own = sum(m for m in owns if m is not None)
        remainder = block_total - sum_own
        none_idx = [i for i, m in enumerate(owns)
                    if m is None and _is_empty(cleaned[i]) is False and len(cleaned[i]) > 10]
        distributed = [False] * len(owns)
        if remainder and none_idx:
            base, rem = divmod(remainder, len(none_idx))
            for k, i in enumerate(none_idx):
                owns[i] = base + (1 if k < rem else 0)
                distributed[i] = True
        for idx, (part, sub, seg, lstart, lend) in enumerate(leaves):
            questions.append(dict(qno=qno, part=part, subpart=sub,
                                  stem=stem, text=cleaned[idx], marks=owns[idx], section=sec,
                                  marks_source=('distributed' if distributed[idx] else 'extracted'),
                                  _start=lstart, _end=lend))
    return questions

# ---------- 自动标注 ----------
# ---------- 文本清洗（需求 6） ----------
ANSWER_LINE = re.compile(r'^[\s.\-_·‐‑‒–—_{}()\[\]]+$')
NOISE = re.compile(r'UCLES|Turn over|©|Cambridge International|For Examiner|Examiner.{0,6}Use|'
                   r'DO NOT WRITE|Blank page|This page is intentionally|www\.Cambridge|'
                   r'Maximum mark|Total .{0,4}\d{1,3}|Question\s*\d+\s*\(', re.I)
MARK_RE2 = re.compile(r'\[\s*\d{1,2}\s*\]')

def clean_question(s):
    if not s:
        return ''
    s = re.split(r'\.{8,}', s, maxsplit=1)[0]      # 截掉答案下划线之后的内容（含二进制残骸）
    s = re.sub(r'\*\s*\d{4,}\s*\*', ' ', s)         # 孤立 * 数字 * 残骸
    out = []
    for ln in s.split('\n'):
        t = ln.replace('\r', '').strip()
        if ANSWER_LINE.match(t):
            continue
        if NOISE.search(t):
            continue
        out.append(t)
    txt = ' '.join(out)
    txt = MARK_RE2.sub('', txt)                     # 去掉行尾 [n] 分值
    txt = re.sub(r'\s+', ' ', txt).strip().strip(' .-_')
    return txt

def norm(s):
    s = s.lower()
    return s.replace('ö', 'oe').replace('ä', 'ae').replace('ü', 'ue').replace('ß', 'ss')

# ---------- 实验映射（需求 3：仅 12 篇核心实验） ----------
STUDY_DICT = {  # 研究者姓氏 → 实验（含变音归一键）
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
# 研究内容关键词（高精确，避免误命中）
CONTENT = {
    'study.dement_kleitman': ['rem sleep', 'rem was', 'rem ', 'dream', 'eeg', 'eye movement'],
    'study.holzel': ['mindfulness', 'meditat', 'ffmq', 'five facet', 'body scan', 'mbsr', 'mindful',
                     'cannot relax', 'feel stressed', 'relax more', 'workers relax', 'help its workers', 'stress reduction'],
    'study.hassett': ['toy preference', 'vervet', 'monkey', 'sex difference', 'gender difference'],
    'study.andrade': ['doodl', 'daydream'],
    'study.baron_cohen': ['eyes test', 'reading the mind', 'autism', ' asd', 'hfa', 'sally-anne', 'sally anne', 'mind-blind', 'mindblind'],
    'study.pozzulo': ['line-up', 'lineup', 'eyewitness', 'identified from a line', 'line-up'],
    'study.bandura': ['bobo', 'aggression', 'imitation'],
    'study.fagen': ['elephant'],
    'study.saavedra_silverman': ['button', 'phobia', 'fear of'],
    'study.milgram': ['obedience', 'shock', 'authority'],
    'study.perry': ['personal space'],
    'study.piliavin': ['subway', 'bystander', 'emergency', 'new york'],
}
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

def is_garbage(text):
    """丢弃 PDF 抽取残骸：无字母、或大量非 ASCII 乱码。"""
    if not re.search(r'[A-Za-z]', text):
        return True
    if len(text) > 12:
        na = sum(1 for ch in text if ord(ch) > 127)
        if na / len(text) > 0.3:
            return True
    return False

def detect_studies(text, stem):
    """返回 (named_studies:set, approach_studies:set, flags:list)。
    named=姓氏/内容命中；approach=视角级题目回溯到的该视角全部实验。"""
    blob = norm(text + ' ' + stem)
    named = set()
    flags = []
    for tok, tid in STUDY_DICT.items():
        if re.search(r'\b' + re.escape(tok), blob):
            named.add(tid)
    for tid, kws in CONTENT.items():
        if any(k in blob for k in kws):
            named.add(tid)
    approach_hit = None
    for ap, kws in APPROACH_KW.items():
        if any(k in blob for k in kws):
            approach_hit = ap
            break
    approach_studies = set()
    if not named and approach_hit:
        approach_studies = set(APPROACH_STUDIES[approach_hit])
        flags.append('approach_general')
    if len(named) >= 2:
        flags.append('multi_study')
    return named, approach_studies, flags
# P1 题型 = 研究切面（用户 2026-08-30 指定 13 类 + other；优先级从高到低，首个命中为准）
TYPE_P1 = [
    ('background',            ['brief background', 'background to the study', 'background of the study',
                               'brief description of one study', 'description of one study',
                               'briefly describe the study', 'briefly outline one study',
                               'give a brief description', 'briefly describe one', 'briefly outline']),
    ('psychology_investigated',['area of psychology', 'branch of psychology', 'field of psychology',
                               'psychology is being investigated', 'psychology does this study investigate',
                               'which area of psychology', 'what area of psychology', 'what branch of psychology',
                               'psychology was investigated', 'psychology being investigated']),
    ('aim',                   ['aim of the study', 'the aim of', 'what was the aim', 'state the aim',
                               'what is the aim', 'purpose of the study', 'the study aimed', 'one aim of',
                               'aims of the study', 'the aim was', 'outline one aim', 'outline the aim',
                               'state one aim', 'one aim', 'what was the purpose', 'the purpose of']),
    ('hypothesis',            ['hypothesis', 'null hypothesis', 'directional hypothesis',
                               'experimental hypothesis', 'alternative hypothesis', 'the hypothesis was',
                               'outline one hypothesis', 'state one hypothesis', 'one hypothesis',
                               'the hypothesis']),
    ('research_method_design',['research method', 'method used in the study', 'experimental design',
                               'design of the study', 'what research method', 'what design was',
                               'which design', 'lab experiment', 'field experiment', 'independent groups',
                               'repeated measures', 'matched pairs', 'correlational design',
                               'observational design', 'the method was', 'what method was', 'research design',
                               'identify the research method', 'research method used',
                               'experimental design used', 'what experimental design', 'the design of',
                               'design used in', 'what design was used']),
    ('sample',                ['sampling technique', 'who took part', 'how many participant',
                               'number of participant', 'volunteer sample', 'opportunity sample',
                               'random sample', 'how many people took part', 'how many children',
                               'how many student', 'age of the participant', 'who were the participant',
                               'how many males', 'how many females', 'how many people were',
                               'describe the sample', 'outline the sample', 'how many participants',
                               'the sample consisted', 'the sample was', 'number of participants',
                               'the participants were', 'how many were', 'who were the participants']),
    ('procedure',             ['procedure', 'how was the study carried out', 'what did the participant do',
                               'how the study was conducted', 'outline the procedure', 'stages of the study',
                               'step of the study', 'describe what the participant', 'how the study was',
                               'what happened in the study', 'the study was carried out', 'steps of the study',
                               'describe the procedure', 'what the participant did', 'outline the stages',
                               'describe the stages', 'the procedure involved', 'steps involved',
                               'describe the steps', 'what happened', 'how the study was carried']),
    ('result',                ['finding', 'what did the study find', 'what were the result',
                               'what the study found', 'evidence from the study', 'what the researchers found',
                               'what does the table show', 'what does the graph show', 'the results show',
                               'the findings show', 'data from the study', 'what does figure', 'the results were',
                               'outline one result', 'state one result', 'one result', 'the result of',
                               'what does the table', 'what does the graph', 'what does the figure',
                               'what does the chart', 'the results indicate', 'the findings indicate',
                               'according to the table', 'according to the graph', 'according to figure',
                               'according to the chart', 'what does chart', 'the results of the study']),
    ('conclusion',            ['conclusion of the study', 'what conclusion', 'the conclusion',
                               'what conclusion can be', 'conclusion that can be', 'draw a conclusion',
                               'explain the conclusion', 'what conclusion can', 'the conclusion is',
                               'conclusion that', 'a conclusion']),
    ('strengths_weaknesses',  ['strength', 'weakness', 'limitation', 'evaluate the study', 'evaluate one study',
                               'criticism', 'validity', 'reliability', 'generalis', 'bias',
                               'criticise', 'strengths of the study', 'weaknesses of the study',
                               'strengths and weaknesses', 'weaknesses and strengths',
                               'one strength', 'a strength', 'one weakness', 'a weakness',
                               'one limitation', 'a limitation', 'strengths of', 'weaknesses of',
                               'evaluate the', 'evaluate one', 'a strength of', 'a weakness of']),
    ('application_everyday',  ['application to everyday life', 'everyday life', 'real-life', 'real life',
                               'real-world', 'real world', 'apply the study to', 'applied to everyday',
                               'application of the study', 'apply your knowledge', 'could be applied',
                               'applied to', 'one application', 'real life situation', 'everyday']),
    ('issues_debates',        ['issues and debates', 'nature and nurture', 'nature/nurture',
                               'individual and situational', 'use of children', 'use of animals',
                               'cultural differences', 'reductionis', 'holism', 'holistic', 'determinis',
                               'free will', 'idiographic', 'nomothetic', 'gender bias', 'ethnocentrism',
                               'one issue', 'the debate', 'a debate', 'issues and', 'one way in which',
                               'ethnocentric', 'androgyny']),
    ('approach',              ['the biological approach', 'the cognitive approach', 'the learning approach',
                               'the social approach', 'two approaches', 'compare the', 'one assumption',
                               'key assumption', 'assumptions of', 'the approach argues',
                               'the approach suggests', 'assumption of the', 'outline one assumption',
                               'compare two approaches', 'the approach', 'one assumption of',
                               'assumptions of the']),
]
METHOD_KW = {
    'method.experiment': ['experiment', 'experimental'],
    'method.self_report': ['questionnaire', 'interview', 'self-report', 'self report'],
    'method.case_study': ['case study', 'case-study'],
    'method.observation': ['observation', 'observational'],
    'method.correlation': ['correlation', 'correlational'],
    'method.longitudinal': ['longitudinal'],
}
CONCEPT_KW = {
    'concept.aims_hypotheses': ['hypothesis', 'aim of the'],
    'concept.variables': ['variable', 'independent variable', 'dependent variable', 'extraneous'],
    'concept.controls': ['control', 'standardis'],
    'concept.types_of_data': ['qualitative', 'quantitative', 'data type', 'type of data', 'primary data', 'secondary data'],
    'concept.sampling': ['sample', 'sampling', 'random sample', 'opportunity sample', 'volunteer sample'],
    'concept.ethics': ['ethic', 'consent', 'deception', 'debrief', 'withdraw', 'confidential'],
    'concept.reliability': ['reliability', 'reliable'],
    'concept.validity': ['validity', 'valid'],
    'concept.data_analysis': ['mean', 'median', 'mode', 'graph', 'bar chart', 'scatter', 'table', 'percentage', 'calculate', 'standard deviation', 'analyse the', 'analyse the data'],
    'concept.evaluating': ['evaluate', 'strength', 'weakness', 'limitation', 'criticism'],
}
FIG_KW = ['table', 'figure', 'fig.', 'draw a', 'bar chart', 'scatter', 'pie chart', 'axis', 'graph', 'histogram']
CMD_MAP = {
    'state': 'define', 'identify': 'define', 'give': 'define', 'define': 'define', 'name': 'define',
    'outline': 'outline', 'describe': 'describe', 'explain': 'explain', 'suggest': 'suggest',
    'compare': 'compare', 'analyse': 'analyse', 'analyze': 'analyse', 'evaluate': 'evaluate', 'plan': 'plan',
}

def tag_topics_p1(text):
    """需求 3：知识点仅 12 篇实验。返回 (studies_set, confidence)。"""
    named, approach_studies, flags = detect_studies(text, '')
    studies = named if named else approach_studies
    if not studies:
        return set(), 0.0
    if 'approach_general' in flags:
        return set(studies), 0.4
    return set(studies), 0.9

def tag_topics_p2(text):
    t = text.lower()
    topics, conf = [], 0.0
    for tid, kws in METHOD_KW.items():
        if any(k in t for k in kws):
            topics.append(tid); conf = max(conf, 0.7); break
    if not topics:
        for tid, kws in CONCEPT_KW.items():
            if any(k in t for k in kws):
                topics.append(tid); conf = max(conf, 0.6); break
    else:
        for tid, kws in CONCEPT_KW.items():
            if any(k in t for k in kws):
                topics.append(tid); conf = max(conf, 0.7)
    return topics, round(conf, 2)

def tag_type_p1(text):
    t = text.lower()
    for tid, kws in TYPE_P1:
        if any(k in t for k in kws):
            return tid, 0.7
    return None, 0.0

def tag_cmd(text):
    w = re.sub(r'^[\(\[][^\)\]]*[\)\]]\s*', '', text).strip().split()
    if not w: return None
    return CMD_MAP.get(w[0].lower().rstrip('.,:;'))

def has_figure(text):
    t = text.lower()
    return any(k in t for k in FIG_KW)

# ---------- 主流程 ----------
def main():
    files = discover()
    print(f"发现去重后源文件: {len(files)} 份")
    all_rows = []
    pending = []
    report = {'papers': [], 'totals': {}}
    tot_q = tot_leaf = 0
    for b in sorted(files):
        path = files[b]
        meta = parse_name(path)
        text = extract_text(path)
        if text.startswith('__EXTRACT_ERROR__'):
            report['papers'].append({**meta, 'error': text, 'ok': False}); continue
        qs = parse_paper(text)
        # 章节统计辅助
        series = meta['series']; paper = meta['paper']; variant = meta['variant']
        prefix = f"{series}-{paper}{variant}"
        leaves = []
        for q in qs:
            part = q['part']; sub = q['subpart']
            leaf_id = f"q{q['qno']}{part}{('_'+sub) if sub else ''}"
            clean_stem = clean_question(q['stem'])
            clean_qtext = clean_question(q['text'])
            full = (clean_stem + ' ' + clean_qtext).strip()
            if meta['paper'] == 1:
                topics, tconf = tag_topics_p1(full)
                ttype, pconf = tag_type_p1(full)
            else:
                topics, tconf = tag_topics_p2(full)
                ttype, pconf = None, 0.0   # Q4: P2 题型留空
            topics = sorted(topics)          # set → 有序列表（仅 12 实验）
            cmd = tag_cmd(q['text'])
            fig = has_figure(full)
            rec = {
                "_start": q['_start'], "_end": q['_end'],   # 临时调试用，写出前 pop
                "id": f"{prefix}-{leaf_id}",
                "paper": {"code": f"9990/{paper}{variant}", "no": paper, "variant": variant},
                "series": {"year": meta['year'], "session": meta['session'], "label": f"{meta['year']} {meta['session_label']}"},
                "syllabus_version": "2024-2026",
                "q_no": q['qno'], "part": part or None, "subpart": sub or None,
                "marks": q['marks'],
                "section": q['section'],
                "stem_text": clean_stem,
                "text": clean_qtext,
                "has_figure": fig,
                "topics": topics,
                "type_facet": ttype,            # P1=研究切面, P2=null
                "command_words": [cmd] if cmd else [],
                "marks_source": q.get('marks_source', 'extracted'),  # extracted | distributed
                "confidence": {"structure": 1.0, "topic": tconf, "type": pconf},
                "source": {"file": b, "page": None},
                "reviewed_by": None, "reviewed_at": None,
            }
            leaves.append(rec); all_rows.append(rec); rec.pop('_start', None); rec.pop('_end', None)
            # 复核判定
            need = []
            if not topics: need.append('topic_empty')
            # P1 题型为空仅当“研究型题目”(topics 含 study.*) 才需补；approach/debate 题留空属正确
            if meta['paper'] == 1 and ttype is None and any(t.startswith('study.') for t in topics):
                need.append('p1_type_empty')
            if q['marks'] is None: need.append('marks_missing')
            if q.get('marks_source') == 'distributed': need.append('marks_distributed')
            if tconf < 0.85 and topics: need.append('topic_lowconf')
            if fig: need.append('figure')
            if need:
                pending.append({
                    'id': rec['id'], 'paper': f"P{paper}", 'q': leaf_id, 'marks': q['marks'] or '',
                    'section': q['section'], 'type_auto': ttype or '', 'topics_auto': ';'.join(topics),
                    'cmd': cmd or '', 'has_figure': 'Y' if fig else '', 'needs': ';'.join(need),
                    'text_preview': q['text'][:60].replace('\n', ' '),
                    'correction': ''
                })
        marks_sum = sum(r['marks'] for r in leaves if r['marks'])
        expected = 60
        ok = (marks_sum == expected)
        report['papers'].append({
            **meta, 'n_questions': len(qs), 'n_leaves': len(leaves),
            'marks_sum': marks_sum, 'expected': expected, 'checksum_ok': ok,
            'n_figure': sum(1 for r in leaves if r['has_figure']),
            'n_review': sum(1 for r in leaves if (not r['topics']) or (meta['paper']==1 and not r['type_facet'] and any(t.startswith('study.') for t in r['topics'])) or r['marks'] is None or r.get('marks_source')=='distributed' or r['confidence']['topic']<0.85 or r['has_figure']),
        })
        tot_q += len(qs); tot_leaf += len(leaves)
        # 写出该卷 jsonl
        out_path = os.path.join(ROOT, 'data', 'questions', f"{prefix}.jsonl")
        with open(out_path, 'w', encoding='utf-8') as f:
            for r in leaves:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    report['totals'] = {'papers': len(report['papers']), 'questions': tot_q, 'leaves': tot_leaf,
                        'checksum_fail': sum(1 for p in report['papers'] if not p.get('checksum_ok'))}
    # 校验报告
    with open(os.path.join(ROOT, 'reports', 'validation_2024_2026.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    # 复核 CSV
    with open(os.path.join(ROOT, 'data', 'review', 'pending.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['id','paper','q','marks','section','type_auto','topics_auto','cmd','has_figure','needs','text_preview','correction'])
        w.writeheader()
        for row in pending: w.writerow(row)
    print(f"题目(顶层): {tot_q}  叶子题: {tot_leaf}  校验失败卷: {report['totals']['checksum_fail']}")
    print(f"待复核行: {len(pending)}  输出目录: data/questions/")

if __name__ == '__main__':
    main()
