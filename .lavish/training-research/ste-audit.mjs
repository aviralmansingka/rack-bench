import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// ponytail: local preservation checks and prose warnings; no grammar-certification claim.
const root = path.dirname(fileURLToPath(import.meta.url));
const baselinePath = path.join(root, '.ste-baseline.json');
function files(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const p = path.join(dir, entry.name);
    return entry.isDirectory() ? files(p) : p.endsWith('.md') ? [p] : [];
  });
}
const relative = p => path.relative(root, p);
function fences(text) {
  return [...text.matchAll(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[^\n]*$/gm)].map(m => m[0]);
}
function bag(items) {
  const result = new Map();
  for (const item of items) result.set(item, (result.get(item) || 0) + 1);
  return result;
}
function lost(before, after) {
  const a = bag(after);
  return [...bag(before)].filter(([item, count]) => (a.get(item) || 0) < count);
}
function quoteSections(text) {
  return text.split(/(?=^#{1,6} )/m).map(section => ({
    heading: section.match(/^#{1,6} .+$/m)?.[0] || '',
    quotes: section.match(/“[^”]*”|"(?:\\.|[^"\\])*"|‘[^’]*’/g) || [],
    delimiters: [...section].filter(c => ['“', '”', '"', '‘'].includes(c)).join(''),
  }));
}
function tokens(text) {
  const noLinks = text.replace(/https?:\/\/[^\s)\]>]+/g, '');
  return {
    urls: [...text.matchAll(/https?:\/\/[^\s)\]>]+/g)].map(m => m[0]),
    links: [...text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)].map(m => m[1]),
    numbers: [...noLinks.matchAll(/\b\d+(?:\.\d+)*(?:%|[a-zA-Z]+)?\b/g)].map(m => m[0]),
    inlineCode: [...text.matchAll(/`([^`\n]+)`/g)].map(m => m[1]),
    headings: text.match(/^#{1,6} .+$/gm) || [],
    tableShape: text.split('\n').filter(l => /^\s*\|/.test(l)).map(l => (l.match(/\|/g) || []).length),
    evidence: [...text.matchAll(/\[(?:observed|calculated|inference)(?:\/proposal)?\]/gi)].map(m => m[0]),
    fences: fences(text),
    quoteSections: quoteSections(text),
  };
}
function prose(text) {
  let fenced = false;
  const blocks = []; let block = [];
  const flush = () => { if (block.length) blocks.push(block.join(' ')); block = []; };
  for (const raw of text.split('\n')) {
    if (/^\s*(```|~~~)/.test(raw)) { flush(); fenced = !fenced; continue; }
    if (fenced || /^\s*(?:#|>)/.test(raw)) { flush(); continue; }
    if (!raw.trim()) { flush(); continue; }
    let line = raw.replace(/\[([^\]]*)\]\([^)]+\)/g, '$1')
      .replace(/https?:\/\/\S+/g, 'URL')
      .replace(/`[^`]+`/g, 'IDENTIFIER')
      .replace(/[“”]([^“”]*)[“”]/g, (_match, body) => 'QUOTE' + (/[.!?]$/.test(body) ? body.at(-1) : ''))
      .replace(/"([^"\n]+)"/g, (_match, body) => 'QUOTE' + (/[.!?]$/.test(body) ? body.at(-1) : ''))
      .replace(/\[(?:observed|calculated|inference)(?:\/proposal)?\]/gi, '')
      .replace(/[*_]/g, '').replace(/^\s*(?:\d+[.)]|[-+])\s+/, '').trim();
    if (/^\s*\|/.test(raw)) { flush(); blocks.push(...line.split('|').map(x => x.trim()).filter(x => x && !/^[-: ]+$/.test(x))); }
    else block.push(line);
  }
  flush();
  return blocks;
}
if (process.argv[2] === 'baseline') {
  if (fs.existsSync(baselinePath)) throw new Error('Baseline already exists.');
  fs.writeFileSync(baselinePath, JSON.stringify(Object.fromEntries(files(root).map(p => [relative(p), fs.readFileSync(p, 'utf8')])), null, 2));
  console.log('Baseline:', files(root).length, 'Markdown files.');
} else {
  const original = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
  const selected = process.argv.slice(2);
  const names = selected.length ? selected : Object.keys(original);
  let errors = 0;
  for (const name of names) {
    if (!(name in original)) throw new Error('File absent from baseline: ' + name);
    const p = path.join(root, name), text = fs.readFileSync(p, 'utf8');
    const architecture = name === 'docs/training-bench-research.md'
      ? fences(text).find(block => /^```mermaid\nflowchart TB/m.test(block)) : undefined;
    const preservationText = architecture && !fences(original[name]).includes(architecture)
      ? text.replace(architecture, '') : text;
    const before = tokens(original[name]), after = tokens(preservationText);
    const issues = [];
    for (const kind of ['urls', 'links', 'numbers', 'inlineCode', 'evidence']) {
      const missing = lost(before[kind], after[kind]);
      if (missing.length) issues.push({ kind: 'lost-' + kind, items: missing });
    }
    if (before.urls.length !== after.urls.length) issues.push({ kind: 'changed-url-count' });
    if (before.links.length !== after.links.length) issues.push({ kind: 'changed-link-count' });
    for (const kind of ['headings', 'fences', 'tableShape', 'quoteSections']) {
      if (JSON.stringify(before[kind]) !== JSON.stringify(after[kind])) issues.push({ kind: 'changed-' + kind });
    }
    for (const target of after.links) {
      if (/^[a-z]+:|^#/i.test(target)) continue;
      if (!fs.existsSync(path.resolve(path.dirname(p), target.split('#')[0]))) issues.push({ kind: 'missing-target', target });
    }
    for (const block of prose(text)) {
      const sentences = block.split(/(?<=[.!?])\s+(?=[A-Z\[])/).filter(s => s.trim());
      const complete = sentences.filter(s => /[.!?]$/.test(s.trim()));
      if (complete.length > 6) issues.push({ kind: 'paragraph-sentences', count: complete.length, text: block });
      for (const sentence of sentences) {
        const count = sentence.trim().split(/\s+/).filter(Boolean).length;
        if (count >= 20 && /[.!?]/.test(sentence)) issues.push({ kind: 'sentence-words', count, text: sentence });
        if (/\b(?:utili[zs](?:e|es|ed|ing)|facilitat(?:e|es|ed|ing)|implement(?:s|ed|ing)?|leverag(?:e|es|ed|ing)|endeavou?r(?:s|ed|ing)?)\b/i.test(sentence)) issues.push({ kind: 'forbidden-verb', text: sentence });
      }
    }
    if (issues.length) { errors++; console.log(JSON.stringify({ file: name, issues })); }
    else console.log('PASS preservation and prose warnings:', name);
  }
  console.log('Checked:', names.length, 'Files with issues:', errors);
  process.exitCode = errors ? 1 : 0;
}
