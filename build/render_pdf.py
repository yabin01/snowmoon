import subprocess, os, sys, urllib.request, pathlib

BASE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(BASE, '..'))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME):
    CHROME = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

jobs = [
    ('book_en.html', 'Snowmoon (English).pdf'),
    ('book_zh.html', 'Snowmoon (中文版).pdf'),
]

for src, out in jobs:
    sp = os.path.join(ROOT, src)
    op = os.path.join(ROOT, out)
    if os.path.exists(op):
        os.remove(op)
    url = pathlib.Path(sp).as_uri()
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
           '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw',
           '--virtual-time-budget=15000', f'--print-to-pdf={op}', url]
    print('running:', out)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print('rc', r.returncode)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
    print('exists', os.path.exists(op), os.path.getsize(op) if os.path.exists(op) else 0)
