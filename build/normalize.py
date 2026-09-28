"""Unify terminology across all zh chapters."""
import re, os, glob

BASE = os.path.dirname(__file__)
REPL = [
    ('英格洛尔', '英格尔沃'),
    ('埃菲利翁', '埃费利翁'),
    ('孔高佩', '昆高佩'),
    ('德文维尔', '德万维尔'),
    ('雷敏', '雷明'),
    ('算力盒', '计算盒'),
    ('共同治理', '共治'),
    ('公民议事会', '公民大会'),
    ('反传输箔', '防传输箔'),
    ('晶圆厂', '芯片厂'),
    ('最高委员会', '高等理事会'),
    ('金字塔山', '山体金字塔'),
    ('沙箱', '沙盒'),
    ('隔热斗篷', '热隐斗篷'),
    ('阿克诸城', '塔克诸邦'),
    ('滴答', '瞬'),
    ('每息', '每瞬'),
]
RX = [
    (re.compile(r'([0-9零一二两三四五六七八九十百千万几])息(?!间)'), r'\1瞬'),
]

total = 0
for f in sorted(glob.glob(os.path.join(BASE, 'zh', 'ch*.md'))):
    t = open(f, encoding='utf-8').read()
    orig = t
    for a, b in REPL:
        t = t.replace(a, b)
    for rx, rep in RX:
        t = rx.sub(rep, t)
    if t != orig:
        open(f, 'w', encoding='utf-8').write(t)
        total += 1
print('files modified:', total)

# report
txt = ''.join(open(f, encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(BASE, 'zh', 'ch*.md'))))
for k in ['英格尔沃', '埃费利翁', '昆高佩', '德万维尔', '雷明', '计算盒', '公民大会',
          '防传输箔', '芯片厂', '高等理事会', '山体金字塔', '沙盒', '热隐斗篷', '塔克诸邦',
          '银聊', '翡翠', '明盆泰', '北极邦', '哨兵', '守护者', '光尺', '长时']:
    print(f'{k}: {txt.count(k)}')
