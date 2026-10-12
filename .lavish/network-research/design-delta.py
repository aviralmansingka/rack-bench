import json,re,collections
from pathlib import Path
r=Path(__file__).resolve().parent
base=json.loads((r/'STE-BASELINE.json').read_text())
a=base['docs/network-bench-research.md']; b=(r/'docs/network-bench-research.md').read_text()
for pat in [r'`([^`\n]+)`',r'\d+(?:[.,]\d+)*']:
    A=collections.Counter(re.findall(pat,a)); B=collections.Counter(re.findall(pat,b))
    print('MISSING',A-B); print('ADDED',B-A)
print('Original length',len(a.splitlines()),'current',len(b.splitlines()))
print('ORIGINAL HEADINGS', re.findall(r'^#+ .*$', a, re.M))
def content_numbers(s):
    s=re.sub(r'^#+ .*$', '', s, flags=re.M)
    s=re.sub(r'^\s*\d+\.\s+', '', s, flags=re.M)
    s=re.sub(r'^```mermaid\n.*?^```', '', s, flags=re.M|re.S)
    return collections.Counter(re.findall(r'\d+(?:[.,]\d+)*',s))
print('MISSING CONTENT NUMBERS',content_numbers(a)-content_numbers(b))
for label,text in [('OLD',a),('NEW',b)]:
    for line in text.splitlines():
        if re.search(r'(?<!\d)2(?!\d|[.,]\d)',line):
            print(label,line)
for name in ['academia.md','books.md','troubleshooting-tools.md','oreilly/tcpip-illustrated.md','oreilly/research.md']:
    text=(r/name).read_text()
    for line in text.splitlines():
        if any(word in line for word in ['Keep these items','Kept:','Its preface','Verified facts.','KEEP as a targeted','searches ran']):
            print(name,line)
