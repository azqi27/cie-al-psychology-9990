// P1 标签镜像（taxonomy.yaml 为单一事实来源，此处为构建期使用的静态映射）。
// 仅覆盖 P1 范围（用户 2026-08-30 指定：仅做 P1）。

export const TOPIC_LABELS: Record<string, string> = {
  // 视角
  'approach.biological': '生物视角',
  'approach.cognitive': '认知视角',
  'approach.learning': '学习视角',
  'approach.social': '社会视角',
  // 12 核心研究
  'study.dement_kleitman': 'Dement & Kleitman（睡眠与梦）',
  'study.hassett': 'Hassett 等（猴子玩具偏好）',
  'study.holzel': 'Hölzel 等（正念与脑扫描）',
  'study.andrade': 'Andrade（涂鸦）',
  'study.baron_cohen': 'Baron-Cohen 等（eyes test）',
  'study.pozzulo': 'Pozzulo 等（列队辨认）',
  'study.bandura': 'Bandura 等（攻击行为）',
  'study.fagen': 'Fagen 等（大象学习）',
  'study.saavedra_silverman': 'Saavedra & Silverman（纽扣恐惧症）',
  'study.milgram': 'Milgram（服从）',
  'study.perry': 'Perry 等（个人空间）',
  'study.piliavin': 'Piliavin 等（地铁助人）',
  // 议题与辩论
  'debate.application_everyday': '应用于日常生活',
  'debate.individual_situational': '个人 vs 情境',
  'debate.nature_nurture': '先天 vs 后天',
  'debate.use_of_children': '使用儿童',
  'debate.use_of_animals': '使用动物',
  'debate.cultural_differences': '文化差异',
  'debate.reductionism_holism': '还原论 vs 整体论',
  'debate.determinism_freewill': '决定论 vs 自由意志',
  'debate.idiographic_nomothetic': 'idiographic vs nomothetic',
};

export const TYPE_LABELS: Record<string, string> = {
  background: '研究背景',
  psychology_investigated: '研究的心理学领域',
  aim: '研究目的',
  hypothesis: '假设',
  research_method_design: '研究方法与设计',
  sample: '被试/样本（技术+特征）',
  procedure: '程序/步骤',
  result: '结果/发现',
  conclusion: '结论',
  strengths_weaknesses: '优势与不足',
  application_everyday: '应用于日常生活',
  issues_debates: '议题与辩论',
  approach: '视角/取向',
  other: '其他/未分类',
};

export const CMD_LABELS: Record<string, string> = {
  define: '下定义',
  outline: '概述',
  describe: '描述',
  explain: '解释',
  suggest: '建议/应用',
  compare: '比较',
  analyse: '分析',
  evaluate: '评价',
  plan: '计划设计',
};

// 知识点下拉分组（顺序即展示顺序）
export const TOPIC_GROUPS: { label: string; ids: string[] }[] = [
  { label: '视角 Approaches', ids: ['approach.biological', 'approach.cognitive', 'approach.learning', 'approach.social'] },
  { label: '核心研究 Core Studies', ids: [
    'study.dement_kleitman', 'study.hassett', 'study.holzel', 'study.andrade',
    'study.baron_cohen', 'study.pozzulo', 'study.bandura', 'study.fagen',
    'study.saavedra_silverman', 'study.milgram', 'study.perry', 'study.piliavin',
  ] },
  { label: '议题与辩论 Debates', ids: [
    'debate.application_everyday', 'debate.individual_situational', 'debate.nature_nurture',
    'debate.use_of_children', 'debate.use_of_animals', 'debate.cultural_differences',
    'debate.reductionism_holism', 'debate.determinism_freewill', 'debate.idiographic_nomothetic',
  ] },
];

export const SESSION_LABELS: Record<string, string> = {
  m: '2–3 月',
  s: '5–6 月',
  w: '10–11 月',
};
