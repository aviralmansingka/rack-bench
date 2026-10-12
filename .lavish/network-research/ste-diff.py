import difflib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
originals = json.loads((root / 'STE-BASELINE.json').read_text())
for name in sys.argv[1:]:
    original = originals[name].splitlines(keepends=True)
    current = (root / name).read_text().splitlines(keepends=True)
    print(''.join(difflib.unified_diff(original, current, fromfile='original/' + name, tofile='converted/' + name)))
