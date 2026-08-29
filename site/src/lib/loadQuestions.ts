import fs from 'node:fs';
import path from 'node:path';

export interface Question {
  id: string;
  paper: { code: string; no: number; variant: number };
  series: { year: number; session: string; label: string };
  syllabus_version: string;
  q_no: string;
  part: string | null;
  subpart: string | null;
  marks: number | null;
  section: string;
  stem_text: string;
  text: string;
  has_figure: boolean;
  topics: string[];
  type_facet: string | null;
  command_words: string[];
  marks_source: string;
  confidence: { structure: number; topic: number; type: number };
  source: { file: string; page: null };
  reviewed_by: string | null;
  reviewed_at: string | null;
}

// 数据即代码：直接读取仓库内 data/questions/*.jsonl（git as database）。
// 站点在 site/ 下构建，数据在上级 data/questions/。
const DATA_DIR = path.resolve(process.cwd(), '../data/questions');

// 轻量清洗：去掉点阵填空行、页码、UCLES 页脚等噪声，保留原题正文。
function cleanText(s: string): string {
  return s
    .split('\n')
    .map((l) => l.replace(/\s+/g, ' ').trim())
    .filter((l) => l !== '')
    .filter((l) => !/^[.\-·‐\s]+$/.test(l))
    .filter((l) => !/^\d+$/.test(l))
    .filter((l) => !/UCLES|Turn over|©/i.test(l))
    .join('\n')
    .trim();
}

function loadAll(): Question[] {
  if (!fs.existsSync(DATA_DIR)) return [];
  const files = fs.readdirSync(DATA_DIR).filter((f) => f.endsWith('.jsonl'));
  const out: Question[] = [];
  for (const f of files) {
    const content = fs.readFileSync(path.join(DATA_DIR, f), 'utf-8');
    for (const line of content.split('\n')) {
      const t = line.trim();
      if (!t) continue;
      try {
        const q = JSON.parse(t) as Question;
        q.text = cleanText(q.text || '');
        out.push(q);
      } catch {
        /* skip malformed line */
      }
    }
  }
  // 用户范围：仅 P1（2024–2026 考纲 Paper 1）
  return out.filter((q) => q.paper.no === 1);
}

export const questions: Question[] = loadAll();

// 题目展示用“有效研究切面”：未命中分类的统一记作 other
export function effectiveType(q: Question): string {
  return q.type_facet || 'other';
}
