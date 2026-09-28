"""Validate zh/*.md structure against src/*.md and normalize terminology."""
import os, re, sys, collections

BASE = os.path.dirname(__file__)


def markers(path):
    out = []
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('@@'):
            out.append(line.strip())
    return out


def mkey(m):
    # id + type + flags (exclude translated place/date)
    parts = m.split('|')
    keep = [p for p in parts if not (p.startswith('place=') or p.startswith('date='))]
    return '|'.join(keep)


def main():
    problems = []
    stats = {}
    for i in range(1, 33):
        s = os.path.join(BASE, 'src', f'ch{i:02d}.md')
        z = os.path.join(BASE, 'zh', f'ch{i:02d}.md')
        if not os.path.exists(z):
            problems.append(f'ch{i:02d}: MISSING zh file')
            continue
        ms, mz = markers(s), markers(z)
        if len(ms) != len(mz):
            problems.append(f'ch{i:02d}: marker count {len(ms)} vs {len(mz)}')
        ks = [mkey(x) for x in ms]
        kz = [mkey(x) for x in mz]
        if ks != kz:
            for a, b in zip(ks, kz):
                if a != b:
                    problems.append(f'ch{i:02d}: marker mismatch {a} != {b}')
                    break
            if len(ks) == len(kz):
                diff = [(a, b) for a, b in zip(ks, kz) if a != b]
                problems.append(f'ch{i:02d}: {len(diff)} mismatched markers e.g. {diff[:3]}')
        # untranslated check
        txt = open(z, encoding='utf-8').read()
        lines = [l for l in txt.split('\n') if l.strip() and not l.startswith('@@')]
        cjk = sum(len(re.findall(r'[\u4e00-\u9fff]', l)) for l in lines)
        stats[i] = cjk
        for l in lines:
            words = re.findall(r'\b[A-Za-z]{3,}\b', l)
            han = len(re.findall(r'[\u4e00-\u9fff]', l))
            if len(words) >= 6 and han < len(words):
                problems.append(f'ch{i:02d}: possibly untranslated: {l[:90]}')
        # marker integrity inside content
        if txt.count('{{') != open(s, encoding='utf-8').read().count('{{'):
            problems.append(f'ch{i:02d}: color-token count differs')
    print('CJK chars per chapter:', sum(stats.values()))
    for i in range(1, 33):
        print(f'  ch{i:02d}: {stats.get(i,0)}')
    print('\nPROBLEMS:', len(problems))
    for p in problems[:60]:
        print(' -', p)


if __name__ == '__main__':
    main()
