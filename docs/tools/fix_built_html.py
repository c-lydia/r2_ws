#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'build' / 'html'
REPO_BLOB_OLD = 'https://github.com/c-lydia/r2_ws/blob/maindocs/source/'
REPO_BLOB_NEW = 'https://github.com/c-lydia/r2_ws/blob/main/docs/source/'
REPO_ROOT = 'https://github.com/c-lydia/r2_ws'

def fix_file(p: Path):
    txt = p.read_text(encoding='utf8')
    orig = txt
    # remove any script tag referencing fix_github_link.js
    txt = re.sub(r"<script[^>]*fix_github_link\.js[^>]*>.*?</script>\s*", '', txt, flags=re.S)
    # replace old blob paths
    txt = txt.replace(REPO_BLOB_OLD, REPO_BLOB_NEW)
    txt = txt.replace('/blob/maindocs/source/', '/blob/main/docs/source/')

    # Replace breadcrumb aside anchor to point to repo root and open in new tab
    # Match the whole wy-breadcrumbs-aside li and replace the anchor inside
    def repl_aside(match):
        return '<li class="wy-breadcrumbs-aside">\n              <a href="%s" target="_blank" rel="noopener"> Repository</a>\n            </li>' % REPO_ROOT

    txt = re.sub(r'<li class="wy-breadcrumbs-aside">.*?</li>', repl_aside, txt, flags=re.S)

    if txt != orig:
        p.write_text(txt, encoding='utf8')
        return True
    return False

def main():
    if not ROOT.exists():
        print('Built HTML directory not found:', ROOT)
        return 1

    changed = 0
    for p in ROOT.rglob('*.html'):
        if fix_file(p):
            changed += 1

    # remove any leftover static JS file
    js = ROOT / '_static' / 'fix_github_link.js'
    if js.exists():
        js.unlink()
        print('Removed', js)

    print('Files modified:', changed)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
