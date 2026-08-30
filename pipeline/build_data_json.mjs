// build_data_json.mjs
// 读取 data/questions/*.jsonl（仅 P1），生成 site/dist/data/questions.json。
// 该文件由前端与后台在运行时 fetch，从而实现“在后台保存 → 直接永久更新到线上数据库”。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.resolve(__dirname, '..', 'data', 'questions');
const OUT = path.resolve(__dirname, '..', 'site', 'dist', 'data', 'questions.json');

function uidFromId(id) {
  const parts = id.split('-');
  if (parts.length !== 4) return id;
  const [prefix, ym, variant, q] = parts;
  const year = ym.slice(0, 4);
  const season = ym.slice(4); // m / s / w
  return `${prefix}_${season}${year.slice(2)}_${variant}_${q.toUpperCase()}`;
}

function trim(s) {
  return String(s || '').replace(/\s+/g, ' ').trim();
}

const files = fs.readdirSync(DATA_DIR).filter((f) => f.endsWith('.jsonl'));
const out = [];
for (const f of files) {
  const file = f; // 如 9990-2024m-12.jsonl
  const content = fs.readFileSync(path.join(DATA_DIR, f), 'utf-8');
  for (const line of content.split('\n')) {
    const t = line.trim();
    if (!t) continue;
    let q;
    try {
      q = JSON.parse(t);
    } catch {
      continue;
    }
    if (q.paper?.no !== 1) continue; // 仅 P1（与站点范围一致）
    out.push({
      id: q.id,
      uid: uidFromId(q.id),
      file,
      paper: q.paper,
      series: q.series,
      syllabus_version: q.syllabus_version,
      q_no: q.q_no,
      part: q.part || null,
      subpart: q.subpart || null,
      marks: q.marks ?? null,
      section: q.section,
      stem_text: trim(q.stem_text),
      text: trim(q.text),
      has_figure: !!q.has_figure,
      topics: q.topics || [],
      type_facet: q.type_facet || null,
      command_words: q.command_words || [],
    });
  }
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(out));
console.log(`[build_data_json] wrote ${out.length} questions -> ${path.relative(__dirname, OUT)}`);
