import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = path.resolve('.lavish/internet-research');
const baselinePath = path.join(root, 'ste-baseline.json');
function files(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? files(p) : e.name.endsWith('.md') ? [p] : [];
  }).sort();
}
const sorted = values => [...values].sort();
function record(text) {
  const lines = text.split('\n');
  const blocks = [];
  let fence = null;
  let protectedBlock = false;
  let block = [];
  const prose = [];
  for (const line of lines) {
    const marker = line.match(/^\s*(`{3,}|~{3,})(.*)$/);
    if (fence) {
      block.push(line);
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length && !marker[2].trim()) {
        if (protectedBlock) blocks.push(block.join('\n'));
        fence = null;
      }
      if (!protectedBlock) prose.push(line);
    } else if (marker) {
      fence = marker[1];
      protectedBlock = marker[2].trim() !== 'markdown';
      block = [line];
      if (!protectedBlock) prose.push(line);
    } else prose.push(line);
  }
  const urls = [...text.matchAll(/https?:\/\/[^\s<>"'`]+/g)].map(m => m[0].replace(/[),.;]+$/, ''));
  const quotes = [...text.matchAll(/"[^"\n]*"|“[^”]*”|(?<![A-Za-z0-9])'[^'\n]+'(?![A-Za-z0-9])|‘[^’]*’/g)].map(m => m[0]);
  const inline = [...text.matchAll(/(?<!`)`[^`\n]+`(?!`)/g)].map(m => m[0]);
  const numbers = [...text.matchAll(/\d+(?:[.,]\d+)*/g)].map(m => m[0]);
  const headings = prose.filter(x => /^#{1,6}\s/.test(x)).map(x => x.match(/^#+/)[0]);
  const tables = prose.filter(x => /^\s*\|/.test(x)).map(x => (x.match(/(?<!\\)\|/g) || []).length);
  const listMarkers = prose.flatMap(x => {
    const m = x.match(/^(\s*)([-+*]|\d+[.)])\s/);
    return m ? [`${m[1]}${m[2]}`] : [];
  });
  const links = [...text.matchAll(/\]\(([^)]+)\)/g)].map(m => m[1]);
  return {
    hash: crypto.createHash('sha256').update(text).digest('hex'),
    lines: lines.length - (lines.at(-1) === '' ? 1 : 0),
    urls: sorted(urls), quotes: sorted(quotes), inline: sorted(inline), numbers: sorted(numbers),
    headings, tables, listMarkers, links: sorted(links), protectedBlocks: blocks,
    prose: prose.join('\n')
  };
}
function proseWarnings(text) {
  const safe = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/https?:\/\/[^\s<>]+/g, 'URL')
    .replace(/`[^`\n]*`/g, 'CODE')
    .replace(/"[^"]*"|“[^”]*”|‘[^’]*’/g, 'QUOTE');
  const banned = [...safe.matchAll(/\b(?:utiliz(?:e|es|ed|ing)|facilitat(?:e|es|ed|ing)|implement(?:s|ed|ing)?|leverag(?:e|es|ed|ing)|endeavo(?:r|rs|red|ring|ur|urs|ured|uring))\b/gi)].map(m => m[0]);
  const normalized = safe.replace(/\d+(?:[.,]\d+)+/g, 'NUMBER')
    .replace(/\b(?:e\.g\.|i\.e\.|et al\.)/g, 'TERM')
    .replace(/[*_~]/g, '');
  const longSentences = [];
  for (const paragraph of normalized.split(/\n\s*\n/)) {
    if (/^\s*#{1,6}\s/.test(paragraph)) continue;
    const chunks = paragraph.split(/\n(?=\s*(?:[-+*]|\d+[.)])\s)|\|/);
    for (const chunk of chunks) {
      for (const sentence of chunk.split(/(?<=[.!?])\s+/)) {
        const clean = sentence.replace(/[*_~#<>]/g, '').trim();
        const count = clean.split(/\s+/).filter(Boolean).length;
        if (count >= 20 && /[.!?]$/.test(clean)) longSentences.push({ words: count, text: clean });
      }
    }
  }
  const tenseWarnings = [...safe.matchAll(/\b(?:have|has|had) (?:not )?(?:verified|checked|confirmed|completed|published|measured|rewritten|converted)|\b(?:was|were|will|would|had)\b/gi)].map(m => m[0]);
  return { banned, longSentences, tenseWarnings };
}
if (process.argv[2] === 'init') {
  if (fs.existsSync(baselinePath)) throw new Error('Baseline already exists. Keep the original baseline.');
  const data = Object.fromEntries(files(root).map(p => [path.relative(root, p), record(fs.readFileSync(p, 'utf8'))]));
  fs.writeFileSync(baselinePath, JSON.stringify(data, null, 2) + '\n');
  console.log(`Saved baseline for ${Object.keys(data).length} Markdown files.`);
} else {
  const baseline = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
  const selected = process.argv.slice(2);
  const names = selected.length ? selected : Object.keys(baseline);
  const results = [];
  for (const name of names) {
    if (!baseline[name]) throw new Error(`Unknown file: ${name}`);
    const now = record(fs.readFileSync(path.join(root, name), 'utf8'));
    const before = baseline[name];
    const differences = ['urls', 'quotes', 'inline', 'numbers', 'headings', 'tables', 'listMarkers', 'links', 'protectedBlocks']
      .filter(key => JSON.stringify(before[key]) !== JSON.stringify(now[key]));
    const allQuotes = prose => sorted([...prose.matchAll(/"[^"]*"|“[^”]*”|‘[^’]*’/g)].map(m => m[0]));
    if (JSON.stringify(allQuotes(before.prose)) !== JSON.stringify(allQuotes(now.prose))) differences.push('allQuotedText');
    const warnings = proseWarnings(now.prose);
    results.push({ file: name, changed: before.hash !== now.hash, lines: now.lines, differences, ...warnings });
  }
  console.log(JSON.stringify(results, null, 2));
  if (results.some(x => x.differences.length || x.banned.length)) process.exitCode = 1;
}
