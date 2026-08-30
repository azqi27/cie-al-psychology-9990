// P1 标签镜像（taxonomy.yaml 为单一事实来源，此处为构建期使用的静态映射）。
// 仅覆盖 P1 范围（用户 2026-08-30 指定：仅做 P1）。
//
// 语言约定（用户 2026-08-30 调整）：
//   - 知识点（12 篇实验）与所有下拉选项 → 英语
//   - 网站 UI（按钮、筛选区标题等）→ 中文

// 12 篇核心实验（知识点维度唯一来源）：英文显示
export const TOPIC_LABELS: Record<string, string> = {
  'study.dement_kleitman': 'Dement & Kleitman (sleep and dreams)',
  'study.hassett': 'Hassett et al. (monkey toy preferences)',
  'study.holzel': 'Hölzel et al. (mindfulness and brain scans)',
  'study.andrade': 'Andrade (doodling)',
  'study.baron_cohen': 'Baron-Cohen et al. (eyes test)',
  'study.pozzulo': 'Pozzulo et al. (line-ups)',
  'study.bandura': 'Bandura et al. (aggression)',
  'study.fagen': 'Fagen et al. (elephant learning)',
  'study.saavedra_silverman': 'Saavedra & Silverman (button phobia)',
  'study.milgram': 'Milgram (obedience)',
  'study.perry': 'Perry et al. (personal space)',
  'study.piliavin': 'Piliavin et al. (subway Samaritan)',
  // —— 四个视角（approach）：仅问视角层面（如 assumption of approach）的题目关联到此处，不绑定具体实验 ——
  'approach.biological': 'Biological approach',
  'approach.cognitive': 'Cognitive approach',
  'approach.learning': 'Learning approach',
  'approach.social': 'Social approach',
  // —— P2 方法/概念（供宏观 Paper 筛选未来扩展；当前无数据）——
  'method.experiment': 'Experiments',
  'method.self_report': 'Self-reports',
  'method.case_study': 'Case studies',
  'method.observation': 'Observations',
  'method.correlation': 'Correlations',
  'method.longitudinal': 'Longitudinal',
  'concept.aims_hypotheses': 'Aims & hypotheses',
  'concept.variables': 'Variables',
  'concept.controls': 'Controls',
  'concept.types_of_data': 'Types of data',
  'concept.sampling': 'Sampling',
  'concept.ethics': 'Ethics',
  'concept.reliability': 'Reliability',
  'concept.validity': 'Validity',
  'concept.data_analysis': 'Data analysis',
  'concept.evaluating': 'Evaluating research',
};

// 各视角下的实验（仅 12 篇）
export const STUDIES_BY_APPROACH: Record<string, string[]> = {
  biological: ['study.dement_kleitman', 'study.hassett', 'study.holzel'],
  cognitive: ['study.andrade', 'study.baron_cohen', 'study.pozzulo'],
  learning: ['study.bandura', 'study.fagen', 'study.saavedra_silverman'],
  social: ['study.milgram', 'study.perry', 'study.piliavin'],
};

// 四个视角标签（仅问视角层面的题目使用，不绑定具体实验）
export const APPROACH_TAGS: string[] = [
  'approach.biological',
  'approach.cognitive',
  'approach.learning',
  'approach.social',
];

// 研究切面（题型）英文
export const TYPE_LABELS: Record<string, string> = {
  background: 'Background',
  psychology_investigated: 'Psychology Investigated',
  aim: 'Aim',
  hypothesis: 'Hypothesis',
  research_method_design: 'Method + Design',
  sample: 'Sample',
  procedure: 'Procedure',
  result: 'Result',
  conclusion: 'Conclusion',
  strengths_weaknesses: 'Strengths & Weaknesses',
  application_everyday: 'Application',
  issues_debates: 'Issues & Debates',
  approach: 'Approach',
  other: 'Other',
};

// 命令词英文
export const CMD_LABELS: Record<string, string> = {
  define: 'Define / State',
  outline: 'Outline',
  describe: 'Describe',
  explain: 'Explain',
  suggest: 'Suggest',
  compare: 'Compare',
  analyse: 'Analyse',
  evaluate: 'Evaluate',
  plan: 'Plan',
};

// 考季英文（用户指定：march / summer / winter）
export const SESSION_LABELS: Record<string, string> = {
  m: 'march',
  s: 'summer',
  w: 'winter',
};

// 试卷（宏观筛选）
export const PAPER_LABELS: Record<number, string> = {
  1: 'Paper 1',
  2: 'Paper 2',
  3: 'Paper 3',
  4: 'Paper 4',
};

// 知识点下拉分组（顺序即展示顺序）；12 实验按视角分组 + 4 个视角(approach)选项
export const TOPIC_GROUPS: { label: string; ids: string[] }[] = [
  { label: 'Biological', ids: STUDIES_BY_APPROACH.biological },
  { label: 'Cognitive', ids: STUDIES_BY_APPROACH.cognitive },
  { label: 'Learning', ids: STUDIES_BY_APPROACH.learning },
  { label: 'Social', ids: STUDIES_BY_APPROACH.social },
  { label: 'Approaches (视角)', ids: APPROACH_TAGS },
];

// P2 方法 / 概念分组（未来扩展）
const P2_GROUPS: { label: string; ids: string[] }[] = [
  {
    label: 'Methods',
    ids: [
      'method.experiment', 'method.self_report', 'method.case_study',
      'method.observation', 'method.correlation', 'method.longitudinal',
    ],
  },
  {
    label: 'Concepts',
    ids: [
      'concept.aims_hypotheses', 'concept.variables', 'concept.controls',
      'concept.types_of_data', 'concept.sampling', 'concept.ethics',
      'concept.reliability', 'concept.validity', 'concept.data_analysis', 'concept.evaluating',
    ],
  },
];

// 宏观 Paper 筛选决定知识点下拉内容（需求 4：不同 paper 展示不同筛选项）
export const TOPICS_BY_PAPER: Record<number, { label: string; ids: string[] }[]> = {
  1: TOPIC_GROUPS,
  2: P2_GROUPS,
  3: [],
  4: [],
};
