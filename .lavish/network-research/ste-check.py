import json
import re
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
baseline = root / 'STE-BASELINE.json'
fences = r'^```[^\n]*\n.*?^```[ \t]*$'
quotes = r'“[^”\n]+”|"[^"\n]+"'

def protected(text):
    prose = re.sub(fences, '', text, flags=re.M | re.S)
    return {
        'urls': Counter(re.findall(r'(?:https?://|file:///)[^\s)>]+', text)),
        'headings': re.findall(r'^#{1,6} .*$', text, re.M),
        'code': re.findall(fences, text, re.M | re.S),
        'labels': Counter(re.findall(r'\[(?:observed|calculated|inference)\]', text)),
        'numbers': Counter(re.findall(r'\d+(?:[.,]\d+)*', text)),
        'quotes': Counter(re.findall(quotes, prose)),
        'gap_declarations': text.count('not publicly retrievable as of 2026-10-11'),
        'inline_code': Counter(re.findall(r'`([^`\n]+)`', prose)),
        'table_shape': [len(re.findall(r'(?<!\\)\|', line)) for line in prose.splitlines() if line.startswith('|')],
        'link_targets': Counter(re.findall(r'\]\(([^)]+)\)', text)),
        'quote_delimiters': Counter(char for char in prose if char in '\"“”‘'),
        'list_shape': re.findall(r'^(\s*(?:[-*]|\d+\.) )', prose, re.M),
    }

def prose_blocks(text):
    text = re.sub(fences, '', text, flags=re.M | re.S)
    text = re.sub(r'`[^`\n]+`', 'CODE', text)
    text = re.sub(r'\[[^\]]+\]\([^)]+\)', 'CITATION', text)
    text = re.sub(r'(?:https?://|file:///)[^\s)>]+', 'URL', text)
    text = re.sub(quotes, 'QUOTE', text)
    text = re.sub(r'\[(?:observed|calculated|inference)\]', '', text)
    text = re.sub(r'\b([A-Z])\.(?=\s)', r'\1<DOT>', text)
    text = re.sub(r'\b(?:Ch|ch|chs|p|pp|vs)\.(?=\s)', lambda m: m[0][:-1] + '<DOT>', text)
    text = re.sub(r'(The title:\s*)\*[^*]+\*', r'\1TITLE', text)
    blocks = []
    current = []
    def flush():
        if current:
            blocks.append(' '.join(current))
            current.clear()
    for line in text.splitlines():
        if not line.strip() or line.startswith(('#', '>')):
            flush()
        elif line.startswith('|'):
            flush()
            if not re.fullmatch(r'[|\s:-]+', line):
                blocks.extend(cell.strip() for cell in line.strip('|').split('|') if cell.strip())
        else:
            if re.match(r'^\s*(?:[-*]|\d+\.)\s+', line):
                flush()
                line = re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', line)
            current.append(line.strip())
    flush()
    return blocks

if sys.argv[1:] == ['snapshot']:
    assert not baseline.exists(), 'Do not replace the original baseline.'
    files = {str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob('*.md'))}
    baseline.write_text(json.dumps(files, indent=2))
    print(f'Original Markdown files: {len(files)}')
    for name, text in files.items():
        print(f'{len(text.splitlines()):4} {name}')
    raise SystemExit

originals = json.loads(baseline.read_text())
if sys.argv[1:]:
    originals = {name: originals[name] for name in sys.argv[1:]}
errors = []
long = []
paragraphs = []
for name, original in originals.items():
    path = root / name
    if not path.exists():
        errors.append(f'{name}: missing file')
        continue
    current = path.read_text()
    comparison = current
    if name == 'docs/network-bench-research.md':
        diagram = '```mermaid\n' + (root / 'bench-run-architecture.mmd').read_text() + '```'
        if diagram in comparison:
            assert comparison.count(diagram) == 1
            comparison = comparison.replace(diagram, '', 1)
    before, after = protected(original), protected(comparison)
    for field in before:
        if before[field] != after[field]:
            errors.append(f'{name}: changed {field}')
    file_long = []
    file_paragraphs = []
    for block in prose_blocks(current):
        sentences = [x for x in re.split(r'(?<=[.!?])\s+', block) if x.strip()]
        sentences = [x for x in sentences if not re.fullmatch(r'(?:CITATION|URL|[\s.,;·])+', x)]
        if len(sentences) > 6:
            file_paragraphs.append(block)
        for sentence in sentences:
            words = re.findall(r'\S+', sentence)
            if len(words) >= 20:
                file_long.append(f'{len(words)} words: {sentence}')
    print(f'{name}: changed={current != original}, long={len(file_long)}, paragraphs={len(file_paragraphs)}')
    long.extend(f'{name}: {x}' for x in file_long)
    paragraphs.extend(f'{name}: {x}' for x in file_paragraphs)
print(f'Checked {len(originals)} original Markdown files; preservation errors: {len(errors)}')
for error in errors:
    print(error)
for item in long + paragraphs:
    print('REVIEW', item)
assert not errors
