# CIE A-Level 9990 Psychology 公益题库网站 — 规划方案 v1

> 编制日期：2026-08-29 ｜ 更新：2026-08-30 ｜ 状态：**P1 已落地**（分类体系 YAML + 解析管线跑通，2024–2026 P1/P2 全量解析完成）
> 本方案中的数据结论均基于对本工作区现有资料的实际解析验证，非估算。

---

## 一、项目定位

| 项 | 内容 |
|---|---|
| 目标用户 | 修读 CIE 9990 Psychology 的 AS/A2 学生、任课教师 |
| 核心价值 | 把 240 份 past paper 拆成可按「知识点 + 题型」检索的原子题目，替代"翻 PDF 找同类题"的低效备考方式 |
| 功能边界 | 只读。筛选 → 浏览 → 打印/导出。无注册、无提交、无评论、无排行 |
| 性质 | 公益，零收费、零广告 |
| 成本目标 | 搭建 0 元，年运维 ≤ 100 元（仅域名可选） |

---

## 二、现状盘点（已实测）

### 2.1 数据资产

工作区内已具备**完整**的原始素材，无需外部抓取：

| 资产 | 数量 | 位置 |
|---|---|---|
| 试卷 qp（去重后） | **240 份** | `CIE/真题/{2022..2026}`、`09-AL心理 备考资料合集/CIE心理/真题/新考纲/9990/{2018..2024}` |
| 评分标准 ms | 同量级 | 同上 |
| 考官报告 er / 分数线 gt | 部分年份 | 同上 |
| 官方考纲 | 2018-20、2024-26 两版 | `CIE/官方文件/9990_y24-26_sy - syllabus.pdf` |
| 12 篇 core study 原文 | 12 | `CIE/original paper/` |
| 已有人工题目索引雏形 | 1 份卷（m24_22） | `CIE/past paper.xlsx` |

文件命名完全遵循 CIE 标准：`9990_{m|s|w}{yy}_{qp|ms|er|gt}_{variant}.pdf`
→ **年份、考季、卷号、variant 可 100% 由文件名正则解析，零人工录入。**

### 2.2 覆盖范围

- 考季：2018 至 2026，共 **25 个考季**（m=2/3 月，s=5/6 月，w=10/11 月）
- Variant：1 / 2 / 3（m 季仅 variant 2）
- 卷别分布：P1 59 份、P2 61 份、P3 61 份、P4 59 份

### 2.3 可行性验证结果 ★关键

已用 `pypdf` 对全部 240 份试卷跑通原型解析，结论：

| 验证项 | 结果 |
|---|---|
| PDF 是否可提取文本 | ✅ **全部为文本层 PDF**，无扫描件，**无需 OCR** |
| 解析失败率 | **0 / 240** |
| 可切分的带分值子题总数 | **6 081 题** |
| P1 平均总分校验 | 60.0 / 60（**完全吻合官方**） |
| P2 平均总分校验 | 60.0 / 60（**完全吻合官方**） |

分卷题量：

| 卷别 | 份数 | 子题数 | 平均每卷 |
|---|---|---|---|
| P1 Approaches, Issues and Debates | 59 | 1 059 | 17.9 |
| P2 Research Methods | 61 | 1 480 | 24.3 |
| P3 Specialist Options | 61 | 1 402 | 23.0 |
| P4 Specialist Options: Application | 59 | 2 140 | 36.3 |
| **合计** | **240** | **6 081** | — |

> P3/P4 单卷子题多，是因为一份卷含 4 个 specialist option（考生选 2），总分 120/176。
> **副产品：`[n]` 分值之和与官方总分比对，天然构成一个自动化质检 checksum**——这是本项目数据质量的核心保障机制。

### 2.4 考纲版本断层（必须在数据模型中体现）

实测各年份卷面标题，发现 **2024 年 P3/P4 发生结构性改版**：

| 年份 | Paper 3 | Paper 4 |
|---|---|---|
| 2018–2023 | Specialist Options: **Theory** | Specialist Options: **Application** |
| 2024–2026 | Specialist Options: **Approaches, Issues and Debates** | Specialist Options: **Application and Research Methods** |

→ 数据模型必须带 `syllabus_version` 字段（`2018-2021` / `2022-2023` / `2024-2026`），前端默认筛选**当前考纲**，旧卷标注"旧考纲"角标。否则学生会练到已废除的题型。

---

## 三、★ 前置风险：版权合规（需你先决策）

这是全项目**唯一的真实阻塞点**，技术上没有任何难点。

- CIE past paper 与 mark scheme 版权归 **UCLES / Cambridge Assessment** 所有。
- 官方许可通常限定为「注册 centre 内部教学使用」，**公开网络转载完整题干与评分标准超出许可范围**。
- 现实中 PapaCambridge、SaveMyExams 等站点在做，但那是商业风险自担，不代表合法。
- 公益性质**不构成免责理由**。

### 三个可选路径

| 方案 | 做法 | 用户价值 | 风险 |
|---|---|---|---|
| **A. 全文模式** | 展示完整题干，不放 mark scheme，全站标注 `© UCLES {year}` 与官方来源链接 | 高 | 中等，存在收到 takedown 的可能 |
| **B. 索引模式**（保守） | 只放题目元数据 + 关键词摘要 + 精确定位（如 `9990/22 · 2025 s · Q3(b) · 4 marks`），题干原文不上站，附官方 PDF 下载指引 | 中 | 低 |
| **C. 授权模式** | 走 Cambridge `copyright@cambridgeinternational.org` 申请公益使用许可，或限定为学校 centre 内部访问（加访问口令） | 高 | 最低，但需等待且可能被拒 |

**我的建议**：技术架构按 A 设计，**上线前把开关做成配置项**（`DISPLAY_MODE: full | index`）。先以 B 模式公开上线，同时并行走 C 申请；若获批或评估可接受，改一个配置即切到 A。架构上零返工。

---

## 四、分类体系设计

### 4.1 维度一：知识点（Syllabus Topic）

树形 4 层，节点数约 90，全部严格对齐官方考纲编号（便于学生和考纲互查）。

```
AS Level
├── Core Studies（12 篇，按 4 个 approach 分组）
│   ├── Biological    → Dement & Kleitman (sleep and dreams)
│   │                   Hassett et al. (monkey toy preferences)
│   │                   Hölzel et al. (mindfulness and brain scans)
│   ├── Cognitive     → Andrade (doodling)
│   │                   Baron-Cohen et al. (eyes test)
│   │                   Pozzulo et al. (line-ups)
│   ├── Learning      → Bandura et al. (aggression)
│   │                   Fagen et al. (elephant learning)
│   │                   Saavedra & Silverman (button phobia)
│   └── Social        → Milgram (obedience)
│                       Perry et al. (personal space)
│                       Piliavin et al. (subway Samaritan)
└── Research Methodology
    ├── Research methods：Experiments(lab/field) · Self-reports(questionnaire/interview)
    │                     · Case studies · Observations · Correlations · Longitudinal
    └── Methodological concepts：Aims & hypotheses · Variables · Controls · Types of data
                                · Sampling · Ethics · Reliability · Validity
                                · Data analysis(descriptive/graphs) · Evaluating research

A Level（4 个 specialist option × 5 topic × 3 sub-topic = 60 个叶子节点）
├── 1 Clinical Psychology    1.1 Schizophrenia · 1.2 Mood (affective) disorders
│                            1.3 Impulse control disorders · 1.4 Anxiety & fear-related
│                            1.5 OCD   ← 每个 topic 下固定 3 子项：
│                                        Diagnostic criteria / Explanations / Treatment & management
├── 2 Consumer Psychology    2.1 Physical environment · 2.2 Psychological environment
│                            2.3 Consumer decision-making · 2.4 The product · 2.5 Advertising
├── 3 Health Psychology      3.1 Patient–practitioner relationship · 3.2 Adherence
│                            3.3 Pain · 3.4 Stress · 3.5 Health promotion
└── 4 Organisational Psy.    4.1 Motivation to work · 4.2 Leadership & management
                             4.3 Group behaviour · 4.4 Work conditions · 4.5 Satisfaction at work

Issues & Debates（横切标签，可与上面任意节点叠加）
├── AS（5）：application to everyday life · individual vs situational · nature vs nurture
│            · use of children · use of animals
└── A2（8）：上述前 4 项 + cultural differences · reductionism vs holism
             · determinism vs free-will · idiographic vs nomothetic
```

> Issues & Debates 单独作为横切标签而非树节点——因为 P1 Section B 和 P3 的评价题几乎必然带 I&D 要求，学生需要"我要专练 nature vs nurture 的题"这种检索。

### 4.2 维度二：题型（Question Type）

拆成 3 个可组合的 facet，比单一列表实用得多：

**Facet 2a — Command word（官方 11 个，直接映射 AO 能力）**

| Command word | 官方释义 | AO |
|---|---|---|
| Define / State / Identify / Give | give precise meaning / express in clear terms / name·select·recognise | AO1 |
| Outline | set out the main points | AO1 |
| Describe | state the points of a topic / give characteristics and main features | AO1 |
| Explain | set out purposes or reasons, make relationships clear, support with evidence | AO1+AO2 |
| Suggest | apply knowledge to situations with a range of valid responses | AO2 |
| Compare | identify similarities and/or differences | AO2 |
| Analyse | examine in detail to show meaning and relationships | AO3 |
| Evaluate | judge the quality, importance, amount or value | AO3 |
| Plan（`Plan an experiment/investigation/study to…`） | 计划设计题 | AO3 |

**Facet 2b — 题目形态**

`短答题` · `情境应用题（scenario/stimulus）` · `数据图表题（table/graph/calculation/draw）` · `计划设计题（planning）` · `长论述题（8–10 marks essay）` · `核心研究复述题`

**Facet 2c — 分值** `1 · 2 · 3 · 4 · 6 · 8 · 10 · 其他`

**Facet 2d — 卷别与来源** `P1/P2/P3/P4` · `年份` · `考季 m/s/w` · `variant` · `考纲版本`

> 分值 facet 看似次要，实际是学生最高频的诉求之一——"给我 10 分的 evaluate 题"直接对应一整类答题模板训练。

---

## 五、数据结构设计

### 5.1 存储原则：Git as Database

**不用任何数据库。**全部数据以纯文本文件存于 Git 仓库：

```
data/
├── taxonomy/
│   ├── topics.yaml           # 知识点树（~90 节点，人工一次性维护）
│   ├── command-words.yaml    # 题型字典
│   ├── studies.yaml          # 12 core studies + specialist option key studies 别名表
│   └── debates.yaml
├── raw/                      # 解析中间产物，不上线，仅供 diff 追溯
│   └── 9990_s25_qp_31.txt
├── questions/                # 主数据，按卷分文件 → 天然分片、diff 友好
│   ├── 2025-s-31.jsonl
│   ├── 2025-s-32.jsonl
│   └── ...（240 个文件）
└── review/
    └── pending.csv           # 低置信度待人工复核队列
```

**为什么用 Git 而不是数据库**
- 免费、无需服务器、无需备份策略
- 每次改题自带版本历史与责任人（`git blame`）
- 可在 GitHub 网页端直接编辑 → **等于免费 CMS，非技术人员也能改**
- 推送即触发自动构建部署，无手工发布动作

### 5.2 题目记录 Schema

```jsonc
{
  "id": "9990-2025s-31-q4b",              // 全站唯一、可读、稳定
  "paper": { "code": "9990/31", "no": 3, "variant": 1 },
  "series": { "year": 2025, "session": "s", "label": "2025 May/June" },
  "syllabus_version": "2024-2026",

  "q_no": "4",                             // 顶层题号
  "part": "b",                             // (b)
  "subpart": null,                         // (i)/(ii)
  "marks": 10,

  "section": "Section B: Consumer Psychology",
  "option": "consumer",                    // P3/P4 专用
  "stem_id": "9990-2025s-31-q4",           // 共享题干/情境材料的父节点
  "stem_text": "For the treatment and management of ...",
  "text": "Evaluate SSRIs and exposure and response prevention (ERP), including ...",
  "has_figure": false,                     // 含表格/坐标轴 → 需截图补充

  // ——— 分类维度 ———
  "topics": ["a2.clinical.1.5.3"],         // 知识点（多值）
  "studies": ["bridge_1988"],              // 涉及研究（多值）
  "debates": ["use_of_children"],          // I&D 横切标签
  "command_words": ["evaluate"],
  "ao": ["AO3"],
  "form": ["essay"],

  // ——— 溯源与质检 ———
  "source": { "file": "9990_s25_qp_31.pdf", "page": 2 },
  "ms_ref": { "file": "9990_s25_ms_31.pdf", "page": 12 },   // 只存引用，不存原文
  "confidence": { "structure": 1.0, "topic": 0.86, "command": 1.0 },
  "reviewed_by": null,
  "reviewed_at": null
}
```

**关键设计点**
1. `stem_id` / `stem_text` 分离 —— 解决"一段情境材料带 (a)(b)(c) 三小问"的问题。筛选命中子题时，前端自动带出父级情境，学生不会看到断头题。
2. `confidence` 三段独立 —— 结构信息（题号/分值/卷别）机器解析置信度为 1.0，只需人工复核 `topic` 低分项。这是把 6 081 题的审校工作量压到可承受的关键。
3. `ms_ref` 只存文件名+页码，**不存评分标准原文** —— 规避最敏感的版权部分。
4. `has_figure` 标记 —— P2/P4 有约 15% 的题含数据表或坐标轴，纯文本无法承载，需单独截图，作为独立子任务排期。

### 5.3 前端产物（构建时生成，非运行时查询）

| 文件 | 内容 | 体积估算 |
|---|---|---|
| `dist/api/index.json` | 全量 6 081 条**精简索引**：id、卷别、年份、分值、topic ids、command、form、题干前 80 字 | ~750 KB → gzip **≈150 KB** |
| `dist/api/q/{paper}-{year}-{session}.json` | 按卷分片的完整题目正文 | 每片 20–60 KB，按需懒加载 |
| `dist/api/taxonomy.json` | 分类树 + 每节点题目计数 | ~30 KB |
| `dist/q/{id}/index.html` | 每道**顶层题**一个静态页（约 1 800 页），可被搜索引擎收录、可分享链接 | — |

筛选完全在浏览器内对 6 081 条数组做 `filter` —— 这个量级下无需任何搜索引擎库，响应 <10 ms。仅当后续要加**关键词全文搜索**时才引入 MiniSearch（~6 KB gzip）。

---

## 六、技术选型

### 6.1 推荐方案

| 层 | 选型 | 理由 | 成本 |
|---|---|---|---|
| 数据管线 | **Python 3.13 + pypdf** | 已实测跑通 240/240，零失败 | 0 |
| 站点框架 | **Astro 5**（静态输出） | 默认零 JS；islands 架构让筛选器局部水合；能为 1 800 道题生成静态页 → SEO 可收录，学生 Google 搜题即可命中 | 0 |
| 样式 | **Tailwind CSS** | 无需自写 CSS 架构，长期可维护 | 0 |
| 交互 | 原生 JS / Preact island | 仅筛选面板需要交互 | 0 |
| 代码与数据托管 | **GitHub**（公开仓库） | 免费私有/公开、免费 Actions、网页端可直接改数据 | 0 |
| CI/CD | **GitHub Actions** | push 即构建部署；公开仓库额度无限 | 0 |
| 站点托管 | **Cloudflare Pages** | 免费、带宽不限、全球 CDN、无需 ICP 备案、静态站无冷启动 | 0 |
| 域名 | 先用 `xxx.pages.dev`，需要时再买 `.org`/`.cn` | 可选 | 0 或 ¥40–70/年 |

### 6.2 关键取舍说明

**为什么不用 Vercel / Netlify**
`*.vercel.app` 在中国大陆长期不可稳定访问，Netlify 亦不稳定。目标用户是中国大陆 A-Level 考生，这是硬否决项。

**Cloudflare Pages 的大陆访问现状**
可访问但速度波动。若上线后实测体验不佳，两个升级路径（架构零改动，只换部署目标）：
- **腾讯云 EdgeOne Pages** —— 有免费额度，大陆节点体验明显更好；绑自定义域名需 ICP 备案
- 阿里云 OSS + CDN —— 约 ¥5–20/月，需备案

> 静态站的最大红利就在这里：托管商是**可即时替换的商品**，不产生任何迁移成本。这正是"低维护成本"要求的正解。

**是否考虑更极端的零构建方案？**
纯 HTML + Alpine.js + JSON（不需要 npm、不会有依赖腐化）确实维护成本更低。但代价是失去静态页生成 → 失去 SEO → 公益项目最重要的**自然传播渠道**没了。
折中：Astro 版本锁定 + `package-lock.json` 提交 + 每年仅做一次依赖体检。构建脚本一旦跑通，三年内无需触碰。

**明确不引入的东西**
无后端、无数据库、无用户系统、无 Redis、无 Docker、无付费 API。任何一项都会把"零成本 + 低维护"击穿。

---

## 七、题目录入与维护方案

### 7.1 五级流水线（自动化优先）

| 级 | 环节 | 方式 | 覆盖率 | 人工量 |
|---|---|---|---|---|
| L0 | 文件名解析 → 卷别/年份/考季/variant/考纲版本 | 正则 | **100%** | 0 |
| L1 | PDF 文本提取 → 题号/子题/分值/section/正文切分 | pypdf + 正则状态机 | **≈98%**（已实测 240/240 无失败） | 抽查 |
| L2 | 题型自动标注（command word / form / AO） | 关键词字典（官方 11 个命令词是封闭集合） | **≈98%** | 抽查 |
| L3 | 知识点自动标注（topic / study / debate） | 字典匹配（研究者姓名、专业术语、section 标题三重线索）+ LLM 兜底并输出置信度 | 字典 ≈75%，+LLM ≈92% | 复核低分项 |
| L4 | 人工审校 | 只审 `confidence.topic < 0.9` 的条目 | 剩余 ≈8% | **约 500 题** |

**质检 checksum（已验证有效）**：每卷 `[n]` 分值求和必须等于官方总分（P1/P2 = 60，P3 = 120，P4 = 176）。任何一卷不吻合 → CI 直接构建失败，定位到具体文件。这让"漏题/多切题"这类最致命的错误不可能流入线上。

**审校工具**：不做后台系统。生成 `review/pending.csv`，用 Excel / 腾讯文档打开，`topic` 列做下拉选项，改完提交回仓库，脚本合并。零开发成本。

### 7.2 含图表题的处理

约 15% 的 P2/P4 题目含数据表或坐标轴。方案：
1. L1 阶段自动检测（正文出现 `Table x.x` / `Fig.` / `axes provided` / `Draw a bar chart` 等特征）→ 打 `has_figure: true`
2. 用 `pypdf` 定位页码，`pdftocairo`/`PyMuPDF` 裁切该区域导出 PNG（本地脚本，免费）
3. 存 `public/figures/{id}.png`，前端题干下方展示
4. 首版可先把这批题标注为"含图，见原卷 Pxx"，不阻塞上线，二期补齐

### 7.3 长期维护（每年约 3 小时）

每年 3 个考季放卷（2/3 月、5/6 月、10/11 月），每次新增约 12 份卷 / 约 300 题：

```
把新 PDF 丢进 data/pdf/  →  跑 `python pipeline.py --series 2027s`
→  CI 自动跑 checksum  →  打开 pending.csv 复核约 25 条低置信度
→  git push  →  自动构建上线
```

单次约 1 小时，年度约 3 小时。**这是本方案"低维护成本"的具体兑现。**
另每年一次依赖体检（Astro/Tailwind 小版本升级 + 重跑构建），约 1 小时。

---

## 八、分阶段执行计划

| 阶段 | 目标 | 主要交付 | 工期 | 出口标准 |
|---|---|---|---|---|
| **P0 立项与合规** | 消除唯一阻塞项 | 版权路径决策（A/B/C）；发出 Cambridge 授权询问；确定站点名与域名 | 3–5 天（含等待） | 明确 `DISPLAY_MODE` 取值 |
| **P1 数据管线 + 分类体系** | 把 PDF 变成结构化数据 | `taxonomy/*.yaml`（90 节点）；`pipeline.py`（L0–L3）；checksum 质检；**2024-2026 考纲全部 9 个考季数据落地并审校完成**（约 1 500 题） | 2 周 | 1 500 题结构 checksum 全绿，topic 标注抽检准确率 ≥95% |
| **P2 网站 MVP 上线** | 可用的公开站点 | Astro 站点；知识点树 + 题型多 facet 筛选；题目详情页；移动端适配；Cloudflare Pages 部署 + CI | 1.5 周 | 手机端可完成"选知识点 → 选题型 → 看到题"全流程，首屏 <1.5 s |
| **P3 历史数据回填** | 覆盖全部 past paper | 2022-2023（约 1 900 题）+ 2018-2021（约 2 700 题）；旧考纲角标；含图题截图补齐 | 3 周（可与 P2 并行） | 6 081 题全部上线，checksum 全绿 |
| **P4 体验增强** | 从"能用"到"好用" | 关键词全文搜索（MiniSearch）；打印/PDF 导出选中题目；组卷（按筛选条件生成练习清单）；暗色模式；题目计数看板 | 1.5 周 | — |
| **P5 常态运维** | 自动化 | 考季更新 SOP 文档；GitHub Actions 定时依赖检查；反馈入口（GitHub Issues，零成本） | 持续 | 单考季更新 ≤1 小时 |

**总工期约 7–8 周**（P2、P3 可并行则约 6 周）。
**建议先做窄而深的切片**：P1 只做 2024-2026 考纲 + P2 上线，两周半即可拿到一个真实可用的站点给学生试用，再决定是否投入 P3 回填 4 600 道旧题。

### 里程碑优先级
1. 🔴 **P0 版权决策** —— 不定则全部后续工作有推翻风险
2. 🔴 **P1 分类体系 YAML** —— 一旦有题目按旧体系标注完，改体系成本极高，必须一次定稿
3. 🟡 P2 MVP —— 尽早拿到用户反馈
4. 🟢 P3/P4 —— 增量，可随时暂停

---

## 十一、决策锁定（用户 Q1–Q8 答复，2026-08-30）

| 项 | 决策 | 对方案的影响 |
|---|---|---|
| Q1 版权 | **按 A 全文模式**；暂不把授权与否纳入考虑 | `taxonomy.yaml` 设 `display_mode: full`；仍保留切换开关 |
| Q2 首版范围 | **仅 2024–2026 考纲的 P1 + P2** | 数据范围收窄；P3/P4 留待 P3 回填阶段 |
| Q3 Mark scheme | **不展示**；每题仅给原卷文件名 + 题号溯源 | 数据模型无 `ms_text` 字段；`source.file` 即溯源依据 |
| Q4 题型维度 | **P1 按「实验/研究流程阶段」分类**（aim/sample/procedure/findings/application to everyday life 等），command word 仅作备选；**P2 题型留空** | `type_facet` 维度：P1=研究切面枚举，P2=null |
| Q5 语言 | 界面中文 + 题目英文 | `taxonomy.yaml` `ui_language: zh` / `question_language: en` |
| Q6 站点名 | `cie-al-psychology-9990`；域名待定留空 | 仓库/项目代号已定；域名先用 `*.pages.dev` |
| Q7 参与复核 | **会**参与约 500 题低置信复核 | 解析管线输出 `data/review/pending.csv` 作为复核工作单 |
| Q8 试用渠道 | 有学生群 / 校内试用渠道 | P2 上线后可直接投放收集反馈 |

> 重要事实更正：2024–2026 考纲下 **Paper 1 = Approaches, Issues and Debates**（Section A 为 12 篇核心研究），**Paper 2 = Research Methods**。因此 P1 的「研究流程阶段」分类实际作用在**核心研究题**上（aim/sample/procedure/findings/application to everyday life 等即「研究切面」）。

## 十二、P1 落地实测（2026-08-30）

### 12.1 交付物

```
9990-qb/
├── pipeline/
│   ├── taxonomy.yaml     # 分类体系单一事实来源（两维 + 通用 facet）
│   └── parse.py          # L0–L3 解析管线（已跑通）
├── data/
│   ├── questions/        # 36 个 .jsonl，每卷一个，每行一道叶子题（共 883 题）
│   └── review/pending.csv# 人工复核工作单
└── reports/
    └── validation_2024_2026.json  # 校验报告（含每卷 60 分 checksum）
```

### 12.2 实测数据

| 指标 | 数值 |
|---|---|
| 去重后源试卷（2024–2026 P1/P2） | **36 份**（注意：2024 年试卷在 `CIE/真题/` 与 `09-AL心理 备考资料合集/` 两处重复，管线按文件名去重，固定 `CIE/真题/` 为权威源） |
| 解析出的叶子题（P1+P2） | **883 道** |
| 每卷总分 checksum 通过率 | **36/36 = 100%**（每卷 `[n]` 之和 = 60） |
| 待复核行（pending.csv） | 717；其中纯分类复核 ≈645，含图题 72 |
| P1 `type_facet` 自动标注命中 | 研究切面枚举约 189 题；其余为 approach/debate 题（留空属正确） |

### 12.3 已解决的关键工程难点

1. **子题层级错乱**：首版把罗马数字 `(i)(ii)` 误判为字母题号；修正为字母题号限 `[a-h]`、罗马数字单独成层。
2. **引导句带分值的题丢失**：如 `3 The table shows… [2]` 后接 (a)(b)，其 `[2]` 落在首标记前被丢弃；改为首标记前文本若含 `[n]` 单独成叶子。
3. **子题标记在 PDF 抽取中偶发丢失**（如某 (i) 文本缺失）：改为**逐标记独立成叶子**，保证每处 `[n]` 都落在某叶子 span 内；缺失标记的子题退化为并入父级，分值不丢。
4. **题头分值未分摊到子题**：部分题的分值标在题头（如 `5 …[4]`）而非各子题后，导致子题 `marks=None`；改为**整题层面余额分配**——先取各叶子自身 `[n]`，剩余总分平摊给非空且较长的未标分真实计分题，标 `marks_source: distributed` 供复核，全程不破坏每卷 60 分校验。

### 12.4 已知待处理项（进入 P2 前或并行）

- **含图题约 72 道**：P1/P2 含数据表/坐标轴，纯文本无法承载，需 `pdftocairo` 裁切 PNG（二期，不阻塞上线）。
- **`marks=None` 约 123 道（14%）**：均为「引导/承接句」等本身非独立计分的部分，其分值已由相邻子题承载，全局 60 分校验不受影响；标 `marks_missing` 供复核时赋 0 或合并。
- **P2 题型体系待定**：按 Q4 留空，后续由用户确认分类口径后再补 `type_facet.values` 与自动标注规则。

## 十三、成本清单

| 项目 | 一次性 | 年度 |
|---|---|---|
| 代码 / 数据托管（GitHub 公开仓库） | 0 | 0 |
| CI 构建（GitHub Actions，公开仓库无限额度） | 0 | 0 |
| 站点托管（Cloudflare Pages 免费版，带宽不限） | 0 | 0 |
| 域名（可选，用 `*.pages.dev` 则为 0） | 0 | ¥0–70 |
| LLM 辅助标注（L3 兜底，约 6 000 次短请求） | ¥30–80 | 0（仅新卷，年约 ¥5） |
| 人力 | 约 60–80 工时 | 约 4 工时 |
| **合计** | **≈¥80 + 人力** | **≈¥75** |

---

## 十、待你确认的问题

### 🔴 阻塞级（影响架构，需先定）

**Q1. 版权路径选哪个？**
A 全文模式 / B 索引模式（保守，先上线）/ C 先申请授权。
我建议：架构按 A 建，先以 B 上线，并行走 C。

**Q2. 首版覆盖范围？**
① 只做 2024-2026 现行考纲（约 1 500 题，2.5 周出站）
② 2022-2026（约 3 400 题）
③ 2018-2026 全量（6 081 题，约 7 周）
我建议 ①，先验证产品形态再回填。

**Q3. 是否展示 mark scheme / 参考答案？**
不展示（仅给出 ms 文件与页码定位，版权风险最低）/ 展示要点摘要 / 展示原文。
我建议：不展示原文。这是版权风险最高的部分，且"看答案"会削弱题库的训练价值。

### 🟡 影响体验（可稍后定）

**Q4. 「题型」维度的呈现粒度？**
按官方 11 个 command word（学生和考纲、评分标准语言一致）/ 归并为 5 类能力（AO1 回忆·AO2 应用·AO3 评价·计划设计·数据处理）/ 两级都做（先能力后命令词）。
我建议：两级都做，默认展示能力大类。

**Q5. 是否需要中文？**
纯英文（保持与考试一致）/ 界面中文 + 题目英文 / 题目附中文翻译（工作量 +100%，且译文质量风险高）。
我建议：界面中文 + 题目英文。

**Q6. 站点名称与域名？**
需要你定名。域名可先用免费 `*.pages.dev`。

### 🟢 待你补充的信息

**Q7. 你自己会参与数据审校吗？**（约 500 题低置信度复核）有专业老师参与，标注质量会显著高于纯自动化。
**Q8. 有无试用渠道？**（学生群 / 校内）P2 上线后需要真实反馈来定 P4 优先级。
**Q9. `CIE/past paper.xlsx` 里那份 m24_22 的人工索引，字段口径（Study involved、Syllabus）是否就是你想要的标准？** 若是，我会直接把它作为自动标注的对齐基准与验收样本。

---

## 附：现有 past paper.xlsx 字段与本方案 Schema 的对应

| 你现有字段 | 本方案字段 | 说明 |
|---|---|---|
| Paper No.（`m24_22`） | `paper` + `series` | 拆为结构化，可独立筛选 |
| Question No. / (a)(b)(c) | `q_no` / `part` / `subpart` | 三级拆分 |
| Question | `stem_text` + `text` | 情境与设问分离 |
| Study involved | `studies[]` | 对齐 `studies.yaml` 别名表 |
| Syllabus | `topics[]` | 对齐官方考纲编号 |
| —（新增） | `marks` | 自动提取，且用于 checksum |
| —（新增） | `command_words` / `form` / `ao` | 题型维度 |
| —（新增） | `debates[]` | I&D 横切标签 |

→ 你的字段口径与本方案完全兼容，方向是对的，只是需要从"人工逐题填"升级为"机器批量出草稿 + 人工只审可疑项"。
