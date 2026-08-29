# cie-al-psychology-9990

> CIE A-Level 心理学 9990 题库
> A free, open question bank for CIE A-Level Psychology (9990).

## 仓库结构 / Structure

```
9990-qb/
├── pipeline/                 # 抽取与标注流水线（Python + pypdf）
│   ├── taxonomy.yaml         # 分类标准（知识点 + 题型 facet）—— 唯一真相源
│   └── parse.py              # L0–L3 解析、标注、校验
├── data/
│   ├── questions/*.jsonl     # 每套试卷一题一行 —— 题库数据库（git as database）
│   └── review/pending.csv    # 待人工复核条目（~500 题低置信度）
├── reports/
│   └── validation_2024_2026.json  # 校验报告（每套试卷分值合计 = 60）
├── README.md
└── .gitignore
```

## 两条筛选维度 / Two Filter Dimensions

1. **知识点 Syllabus Topic** —— `topics` 字段
   - P1: 4 个 approach、12 个 core study
   - P2: 6 个 research method、11 个 methodological concept
2. **题型 Question Type** —— `type_facet` 字段
   - P1: 实验流程阶段（aim / hypothesis / sample / procedure / findings / conclusion / application_everyday / ethical_issues / evaluation / other）
   - P2: 暂留空（待定）
