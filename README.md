# cie-al-psychology-9990

> CIE A-Level 心理学 9990 题库 · 慈善 / 非营利 · 免费开放
> A free, non-profit, open question bank for CIE A-Level Psychology (9990).

## 项目说明 / About

- **考纲 Syllabus:** 2024–2026
- **试卷范围 Papers:** P1（Approaches / Issues & Debates，含 12 个核心研究）、P2（Research Methods）
- **数据来源 Source:** 历年真题 PDF（已抽取为结构化 JSONL，原始 PDF 不入库）
- **界面语言 UI:** 中文 ｜ **题目原文 Questions:** 英文
- **不展示 mark scheme** —— 仅标注原卷名与题号，便于老师 / 学生溯源
- **慈善定位:** 用户仅筛选 / 浏览，无注册、无提交、无交互；维护成本低

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
   - P1: 4 个 approach、12 个 core study、9 个 debate
   - P2: 6 个 method、11 个 concept
2. **题型 Question Type** —— `type_facet` 字段
   - P1: 研究切面（background / psychology_investigated / aim / hypothesis / research_method_design / sample / procedure / result / conclusion / strengths_weaknesses / application_everyday / issues_debates / approach / other）
   - P2: 暂留空（待定）

通用 facet：`marks` / `command_words` / `paper` / `syllabus_version` / `year` / `session`

## 本地运行 / Local Usage

```bash
pip install pypdf
python pipeline/parse.py
```

输出：`data/questions/*.jsonl`、`data/review/pending.csv`、`reports/validation_*.json`

## 部署 / Deploy (publish from GitHub)

前端（Astro 5 + Tailwind v4）已建设，题库筛选站点部署到 **GitHub Pages** 项目站点：
**https://azqi27.github.io/cie-al-psychology-9990/**

- **构建 Build:** `cd site && npm install && npm run build` → 产物在 `site/dist/`
- **发布 Publish:** 将 `site/dist/` 推送到 `gh-pages` 分支（仓库根目录），并在
  Settings → Pages → Source 选择 **Deploy from a branch → gh-pages → /(root)**。
- 该方式仅需仓库 `repo` 权限，**无需** `workflow` 权限，因此未使用 GitHub Actions。
- 数据即代码：题库以 JSONL 文本形式入库，GitHub Web 界面即免费 CMS。

## 许可 / License

慈善 / 教育用途，免费开放。
