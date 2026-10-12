from pathlib import Path
from urllib.parse import unquote, urlparse
import re

root = Path(__file__).resolve().parent
errors = []
excluded = {'research.md', 'EVIDENCE-CHECKS.md', 'RETRY.md'}
briefs = [p for p in (root / 'oreilly').glob('*.md') if p.name not in excluded]
records = list((root / 'oreilly/nodes').glob('N*.md'))
assert len(briefs) == len(records) == 11
for path in briefs:
    text = path.read_text()
    assert text.startswith('# '), path
    assert 'Research date: 2026-10-11. All claims below carry a source URL.' in text, path
    assert all(re.search(r'^## ' + str(n) + r'\. ', text, re.M) for n in range(1, 6)), path
    assert re.findall(r'^## (.+)$', text, re.M)[-1] == 'Gaps', path
    for label in re.findall(r'\[([^\]]+)\]', text):
        if label.lower().startswith(('observ', 'calculat', 'inferenc')):
            assert label in {'observed', 'calculated', 'inference'}, (path, label)
for path in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if link.startswith(('http:', 'https:', 'mailto:', '#')):
            continue
        target = Path(unquote(urlparse(link).path)) if link.startswith('file:') else path.parent / link.split('#', 1)[0]
        if not target.exists():
            errors.append(f'{path}: missing {link}')
for slug in ['linux-networking-2e', 'cloud-native-fabrics', 'linux-networking-video', 'modern-troubleshooting']:
    path = root / 'oreilly' / (slug + '.md')
    declarations = [line for line in path.read_text().splitlines() if 'not publicly retrievable as of 2026-10-11' in line]
    assert declarations and all('http' in line for line in declarations), path
    print(f'{slug}: {len(declarations)} final declaration lines with source URLs')
text = (root / 'oreilly/research.md').read_text()
states = {state: len(re.findall(r'\| ' + state + r' \|', text)) for state in ['done', 'gap', 'running', 'planned']}
assert states == {'done': 7, 'gap': 4, 'running': 0, 'planned': 0}, states
assert 'in progress' not in (root / 'oreilly/RETRY.md').read_text()
print('Map states:', states)
own = ['research.md', 'oreilly.md', 'oreilly/research.md', 'oreilly/RETRY.md', 'oreilly/EVIDENCE-CHECKS.md', 'README.md', 'ORCHESTRATOR-REPORT.md', 'docs/network-bench-research.md']
own += [str(path.relative_to(root)) for directory in ['nodes', 'oreilly/nodes'] for path in (root / directory).glob('N*.md')]
long = []
for name in own:
    in_code = False
    for number, line in enumerate((root / name).read_text().splitlines(), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code or line.startswith(('|', '#')) or not line.strip():
            continue
        line = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line)
        line = re.sub(r'\[(observed|calculated|inference)\]', '', line)
        for sentence in re.split(r'(?<=[.!?])\s+', line):
            count = len(re.findall(r'\S+', sentence))
            if count >= 20:
                long.append(f'{name}:{number}: {count} words: {sentence}')
print(f'Source briefs: {len(briefs)}; source records: {len(records)}; local-link errors: {len(errors)}')
print(f'Own-prose sentences with 20+ words: {len(long)}')
for item in errors + long:
    print(item)
assert not errors and not long
