"""Assemble book_en.html and book_zh.html from blocks.json + zh/*.md"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from extract import inline_in

BASE = os.path.dirname(__file__)
ROOT = os.path.join(BASE, '..')

blocks = json.load(open(os.path.join(BASE, 'blocks.json'), encoding='utf-8'))


# ---------- parse zh md ----------
def parse_md(path):
    """return dict id -> (kind, params, content_lines)"""
    out = {}
    cur = None
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('@@'):
            parts = line.strip()[2:].split('|')
            bid = parts[0]
            kind = parts[1] if len(parts) > 1 else ''
            params = parts[2:]
            cur = bid
            out[bid] = [kind, params, []]
        elif cur is not None:
            out[cur][2].append(line)
    return out


def cell_html(raw, tag):
    if isinstance(raw, (list, tuple)):
        txt = raw[0]
        cs = str(raw[1]) if len(raw) > 1 else None
        rs = str(raw[2]) if len(raw) > 2 else None
        if cs == '1':
            cs = None
        if rs == '1':
            rs = None
    else:
        m = re.match(r'^(?:<c(\d+)>)?(?:<r(\d+)>)?(.*)$', raw, re.S)
        cs, rs, txt = m.group(1), m.group(2), m.group(3)
    attrs = ''
    if cs:
        attrs += f' colspan="{cs}"'
    if rs:
        attrs += f' rowspan="{rs}"'
    return f'<{tag}{attrs}>{inline_in(txt.strip())}</{tag}>'


def render_table(rows, first_header=True):
    h = ['<table>']
    for i, row in enumerate(rows):
        h.append('<tr>')
        for cell in row:
            h.append(cell_html(cell, 'th' if (i == 0 and first_header) else 'td'))
        h.append('</tr>')
    h.append('</table>')
    return ''.join(h)


def render_block_en(b, bid):
    t = b['t']
    if t == 'h1':
        return f'<h1 class="chapter-title">{inline_in(b["text"])}</h1>'
    if t == 'h2':
        return f'<h2>{inline_in(b["text"])}</h2>'
    if t == 'dateline':
        kind = b['kind']
        place, date = b['place'], b['date']
        inner = (f'<span class="place">{inline_in(place)}</span>'
                 f'<span class="sep">·</span>'
                 f'<span class="date">{inline_in(date)}</span>')
        cls = 'dateline chapter-open' if kind == 'open' else 'dateline scene-break'
        return f'<div class="{cls}"><hr class="rule"><span class="txt">{inner}</span></div>'
    if t == 'p':
        return f'<p>{inline_in(b["text"])}</p>'
    if t == 'hr':
        return '<hr>'
    if t == 'quote':
        ps = ''.join(f'<p>{inline_in(x)}</p>' for x in b['text'].split('\n') if x.strip())
        return f'<blockquote>{ps}</blockquote>'
    if t == 'list':
        tag = 'ol' if b['ordered'] else 'ul'
        lis = ''.join(f'<li>{inline_in(x)}</li>' for x in b['items'])
        return f'<{tag}>{lis}</{tag}>'
    if t == 'raw':
        return b['html']
    if t == 'device':
        return render_device_en(b)
    return ''


def render_device_en(b):
    cls = 'device-view ' + ('wide-device-view' if b['wide'] else 'narrow-device-view')
    if b['left']:
        cls += ' device-view-left'
    parts = [f'<div class="{cls}">']
    for kind, val in b['items']:
        if kind == 'svg':
            parts.append(val)
        elif kind == 'table':
            parts.append(render_table(val))
        elif kind in ('text', 'h3'):
            if kind == 'h3':
                parts.append(f'<h3>{inline_in(val)}</h3>')
            else:
                parts.append(f'<p>{inline_in(val)}</p>')
        elif kind == 'list':
            parts.append('<ul>' + ''.join(f'<li>{inline_in(x)}</li>' for x in val) + '</ul>')
    parts.append('</div>')
    return ''.join(parts)


def render_block_zh(b, bid, zh):
    t = b['t']
    e = zh.get(bid)
    if t in ('hr',):
        return '<hr>'
    if t == 'raw':
        return b['html']
    if e is None:
        return render_block_en(b, bid)  # fallback
    kind, params, lines = e
    text = '\n'.join(lines).strip('\n')
    if t == 'h1':
        return f'<h1 class="chapter-title">{inline_in(text)}</h1>'
    if t == 'h2':
        return f'<h2>{inline_in(text)}</h2>'
    if t == 'dateline':
        place = date = ''
        for p in params:
            if p.startswith('place='):
                place = p[6:]
            elif p.startswith('date='):
                date = p[5:]
        inner = (f'<span class="place">{inline_in(place)}</span>'
                 f'<span class="sep">·</span>'
                 f'<span class="date">{inline_in(date)}</span>')
        cls = 'dateline chapter-open' if b['kind'] == 'open' else 'dateline scene-break'
        return f'<div class="{cls}"><hr class="rule"><span class="txt">{inner}</span></div>'
    if t == 'p':
        return f'<p>{inline_in(text)}</p>'
    if t == 'quote':
        ps = ''.join(f'<p>{inline_in(x)}</p>' for x in text.split('\n') if x.strip())
        return f'<blockquote>{ps}</blockquote>'
    if t == 'list':
        tag = 'ol' if b['ordered'] else 'ul'
        lis = ''.join(f'<li>{inline_in(x[2:] if x.startswith("- ") else x)}</li>'
                      for x in text.split('\n') if x.strip())
        return f'<{tag}>{lis}</{tag}>'
    if t == 'device':
        cls = 'device-view ' + ('wide-device-view' if b['wide'] else 'narrow-device-view')
        if b['left']:
            cls += ' device-view-left'
        parts = [f'<div class="{cls}">']
        k = 0
        for kind2, val in b['items']:
            sub = f'{bid}.{k}'
            ze = zh.get(sub)
            if kind2 == 'svg':
                parts.append(val)
            elif kind2 == 'table':
                if ze is not None and ze[0] == 'table':
                    rows = []
                    for line in ze[2]:
                        line = line.strip()
                        if not line:
                            continue
                        body = line[1:].strip() if line.startswith('|') else line
                        rows.append([c for c in body.split(' ‖ ')])
                    parts.append(render_table(rows))
                else:
                    parts.append(render_table(val))
            elif kind2 in ('text', 'h3'):
                zt = '\n'.join(ze[2]).strip('\n') if ze else val
                if kind2 == 'h3':
                    parts.append(f'<h3>{inline_in(zt)}</h3>')
                else:
                    parts.append(f'<p>{inline_in(zt)}</p>')
            elif kind2 == 'list':
                if ze is not None:
                    items = [x[2:] for x in ze[2] if x.strip().startswith('- ')]
                else:
                    items = val
                parts.append('<ul>' + ''.join(f'<li>{inline_in(x)}</li>' for x in items) + '</ul>')
            k += 1
        parts.append('</div>')
        return ''.join(parts)
    return ''


CSS = """
@page { size: 148mm 210mm; margin: 16mm 15mm 18mm; }
@page :first { margin: 20mm 15mm; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", "STSong",
               "SimSun", Georgia, "Times New Roman", serif;
  font-size: 10.4pt; line-height: 1.75; color: #1a1a1a; background: #fff;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
p { margin: 0 0 0.72em; text-align: justify; text-justify: inter-ideograph; }
h1, h2, h3 { font-family: "Source Han Sans SC", "PingFang SC", "Microsoft YaHei",
             "Helvetica Neue", Arial, sans-serif; }
.chapter-title {
  font-size: 20pt; font-weight: 600; letter-spacing: 0.02em;
  margin: 0 0 2px; padding-bottom: 0; border: none; color: #222;
}
h2 { font-size: 13pt; margin: 1.6em 0 0.6em; color: #333; }
h3 { font-size: 11pt; margin: 1.2em 0 0.5em; color: #333; }
hr { border: none; height: 1px; background: #c9c4d8; margin: 1.1em 0; }
blockquote {
  border-left: 3px solid #667eea; background: #f6f7fb; color: #444;
  padding: 0.6em 1em; margin: 1em 0; border-radius: 3px; font-size: 9.8pt;
}
blockquote p { margin: 0 0 0.4em; }
blockquote p:last-child { margin-bottom: 0; }
ul, ol { margin: 0 0 0.8em; padding-left: 1.5em; }
li { margin-bottom: 0.3em; }
em { font-style: italic; }
code { font-family: "Consolas", monospace; background: #f2f2f5; padding: 0 3px;
       border-radius: 3px; font-size: 0.92em; }
/* datelines */
.dateline .rule { margin: 0 0 8px; height: 1px; background: #c9c4d8; border: none; }
.dateline.chapter-open { margin: 2px 0 20px 0; }
.dateline.chapter-open .txt { font-size: 8.6pt; letter-spacing: 0.05em; color: #5a5480; }
.dateline.chapter-open .place { font-weight: 600; }
.dateline.chapter-open .sep { margin: 0 0.5em; color: #c3bed6; }
.dateline.chapter-open .date { letter-spacing: 0.14em; color: #8a83a8; }
.dateline.scene-break { margin: 18px 0; }
.dateline.scene-break .rule { margin-bottom: 6px; }
.dateline.scene-break .txt { font-size: 7.8pt; letter-spacing: 0.12em; color: #a49dc4; }
.dateline.scene-break .place { font-weight: 600; color: #8a83a8; }
.dateline.scene-break .sep { margin: 0 0.5em; }
/* device views */
.device-view {
  background-color: #0a0e27; color: #7fbcff; border-radius: 10px;
  padding: 14px; margin: 14px auto; text-align: center;
  font-family: "Consolas", "Courier New", monospace; font-size: 8.6pt;
  line-height: 1.5; page-break-inside: avoid;
}
.device-view table { width: 100%; border-collapse: collapse; margin: 0 auto;
                     text-align: left; font-size: 8.4pt; }
.device-view th { padding: 7px 8px; border: 1px solid #3d70c3; color: #cef;
                  background: #1a2a4a; font-weight: bold; }
.device-view td { padding: 6px 8px; border: 1px solid #2a4a7a; color: #b8d8ff; }
.device-view tbody tr:nth-child(odd) { background-color: #0f1a3a; }
.device-view tbody tr:nth-child(even) { background-color: #12204a; }
.device-view p { color: #7fbcff; margin: 6px 0; font-size: 8.8pt; text-align: left; }
.device-view h3 { color: #7fbcff; border-bottom: 2px solid #3d70c3; padding-bottom: 6px;
                  margin: 0 0 10px; font-size: 10pt; font-family: inherit; }
.device-view ul { text-align: left; padding-left: 18px; margin: 4px 0; color: #9cc2ff;
                  font-family: inherit; font-size: inherit; }
.device-view li { margin-bottom: 2px; color: #9cc2ff; font-family: inherit; font-size: inherit; }
.device-view svg { display: block; margin: 4px auto !important; max-width: 100%; height: auto; }
.device-view-left { text-align: left; }
.device-view-left table { margin-left: 0; }
.device-view-left svg { margin-left: 0 !important; }
.wide-device-view { max-width: 100%; }
.narrow-device-view { max-width: 62%; }
button {
  background-color: #1a3a6a; border: 1px solid #3d70c3; padding: 4px 12px;
  color: #cef; border-radius: 3px; font-family: inherit; font-size: 8.4pt;
}
/* dz cards */
.dz-card { background: #1b2b36; color: #e6f4ff; border-radius: 8px;
           padding: 14px 18px; margin: 12px auto; max-width: 78%; }
.dz-line { white-space: nowrap; }
center { display: block; margin: 12px 0; }
/* structure */
.chapter { page-break-before: always; }
.chapter:first-of-type { page-break-before: avoid; }
svg { max-width: 100%; height: auto; }
/* cover */
.cover { text-align: center; page-break-after: always; padding-top: 26mm; }
.cover h1 { font-size: 34pt; font-weight: 600; letter-spacing: 0.08em;
            margin: 0 0 6pt; border: none; padding: 0; color: #058; }
.cover .sub { font-size: 10pt; color: #7a74a0; letter-spacing: 0.24em;
              text-transform: uppercase; margin-bottom: 30mm; }
.cover .meta { font-size: 9pt; color: #666; line-height: 1.9; }
.decl { margin: 0 auto; max-width: 118mm; text-align: left; font-size: 8.8pt;
        line-height: 1.7; color: #444; page-break-after: always; }
.decl h2 { font-size: 11pt; margin: 0 0 10px; color: #058; border: none; }
.decl .lab { font-weight: 600; color: #5a5480; margin-top: 12px; display: block; }
.decl p { margin: 0 0 8px; }
.decl a { color: #058; text-decoration: none; }
.toc { page-break-after: always; }
.toc h2 { font-size: 13pt; color: #058; border: none; margin: 0 0 14px; }
.toc table { width: 100%; border-collapse: collapse; font-size: 9.2pt; }
.toc td { padding: 3px 0; border-bottom: 1px dotted #ddd; color: #333;
          vertical-align: baseline; }
.toc td.num { width: 12mm; color: #8a83a8; }
.toc td.loc { text-align: right; color: #8a83a8; font-size: 8.2pt; white-space: nowrap; }
.running { position: running(running-head); font-size: 8pt; color: #999; }
@page { @top-center { content: string(chap, first); font-size: 8pt; color: #999;
                      font-family: "Microsoft YaHei", sans-serif; } }
h1.chapter-title { string-set: chap content(); }
"""

COVER_EN = """
<div class="cover">
  <h1>Snowmoon</h1>
  <div class="sub">A novel</div>
  <div class="meta">Vitalik Buterin<br>vitalik.eth.limo/snowmoon/</div>
</div>
<div class="decl">
  <h2>License</h2>
  <p>Snowmoon is released under the <a href="https://www.gnu.org/licenses/gpl-3.0.html">GPL v3</a></p>
  <p>Yes, I said GPL v3, not CC-BY-SA. My legal theory, which Kimi K3 says is plausible, is that you are free to go turn it into a movie or a vibe-coded anime or whatever, but if you do that, you are required to open-source the pipeline (AI prompts, scripts, task-specific harness, etc) and other non-commodity materials that you used to make it so that other people can build on top of your work.</p>
  <span class="lab">AI usage declaration:</span>
  <p>All words were written directly by me.</p>
  <p>Spelling, grammar and style checking, verifying consistency of the rules of Minpentai and Dzegoban, the HTML and CSS format and style, and the SVGs were done with assistance from Kimi K3 and Qwen 3.8 Flash Next.</p>
  <span class="lab">&#29233; usage declaration:</span>
  <p>Snowmoon was written with love.</p>
</div>
"""

COVER_ZH = """
<div class="cover">
  <h1>&#38634;&#26376;</h1>
  <div class="sub">Snowmoon &middot; Vitalik Buterin</div>
  <div class="meta">&#32500;&#37324;&#36842;&#20122; &middot; &#27901;&#25096; &middot; &#26126;&#30406;&#27888;<br>vitalik.eth.limo/snowmoon/</div>
</div>
<div class="decl">
  <h2>&#35768;&#21487;&#35777;</h2>
  <p>&#12298;&#38634;&#26376;&#12299;&#20197; <a href="https://www.gnu.org/licenses/gpl-3.0.html">GPL v3</a> &#21327;&#35758;&#21457;&#24067;&#12290;</p>
  <p>&#27880;&#24847;&#65292;&#25105;&#35828;&#30340;&#26159; GPL v3&#65292;&#32780;&#19981;&#26159; CC-BY-SA&#12290;&#25105;&#30340;&#27861;&#24459;&#29702;&#35299;&#8212;&#8212;Kimi K3 &#35748;&#20026;&#23427;&#26159;&#25104;&#31435;&#30340;&#8212;&#8212;&#26159;&#65306;&#20320;&#21487;&#20197;&#25226;&#23427;&#25913;&#32534;&#25104;&#30005;&#24433;&#12289;&#29992; vibe coding &#20570;&#20986;&#21160;&#30011;&#25110;&#20854;&#20182;&#20219;&#20309;&#24418;&#24335;&#65292;&#20294;&#19968;&#26086;&#20320;&#36825;&#26679;&#20570;&#20102;&#65292;&#23601;&#24517;&#39035;&#23558;&#20320;&#21046;&#20316;&#23427;&#25152;&#29992;&#30340;&#27969;&#27700;&#32447;&#65288;AI &#25552;&#31034;&#35789;&#12289;&#33050;&#26412;&#12289;&#38754;&#21521;&#29305;&#23450;&#20219;&#21153;&#30340;&#24037;&#20855;&#31561;&#65289;&#20197;&#21450;&#20854;&#20182;&#38750;&#21830;&#21697;&#21270;&#26448;&#26009;&#24320;&#28304;&#20986;&#26469;&#65292;&#35753;&#20854;&#20182;&#20154;&#33021;&#22312;&#20320;&#30340;&#22522;&#30784;&#19978;&#32487;&#32493;&#26500;&#24314;&#12290;</p>
  <span class="lab">AI &#20351;&#29992;&#22768;&#26126;&#65306;</span>
  <p>&#25152;&#26377;&#25991;&#23383;&#22343;&#30001;&#25105;&#20146;&#31508;&#20889;&#23601;&#12290;</p>
  <p>&#25340;&#20889;&#12289;&#35821;&#27861;&#19982;&#39118;&#26684;&#26657;&#23545;&#12289;&#26126;&#30406;&#27888;&#19982;&#27901;&#25096;&#35821;&#35268;&#21017;&#19968;&#33268;&#24615;&#30340;&#26680;&#26597;&#12289;HTML &#19982; CSS &#26684;&#24335;&#39118;&#26684;&#20197;&#21450; SVG &#22270;&#24418;&#65292;&#26159;&#22312; Kimi K3 &#21644; Qwen 3.8 Flash Next &#30340;&#21327;&#21161;&#19979;&#23436;&#25104;&#30340;&#12290;</p>
  <span class="lab">&#29233; &#20351;&#29992;&#22768;&#26126;&#65306;</span>
  <p>&#12298;&#38634;&#26376;&#12299;&#26159;&#24102;&#30528;&#29233;&#20889;&#25104;&#30340;&#12290;</p>
</div>
"""


def toc(lang):
    rows = []
    for i in range(1, 33):
        bl = blocks[str(i)]
        title = ''
        place = ''
        date = ''
        for b in bl:
            if b['t'] == 'h1':
                title = b['text']
            if b['t'] == 'dateline' and b['kind'] == 'open':
                place, date = b['place'], b['date']
                break
        if lang == 'zh':
            z = parse_md(os.path.join(BASE, 'zh', f'ch{i:02d}.md'))
            for bid in z:
                if z[bid][0] == 'open':
                    for p in z[bid][1]:
                        if p.startswith('place='):
                            place = p[6:]
                        elif p.startswith('date='):
                            date = p[5:]
                    break
        rows.append((i, title, place, date))
    out = ['<div class="toc"><h2>%s</h2><table>' % ('目录' if lang == 'zh' else 'Contents')]
    for i, title, place, date in rows:
        if lang == 'zh':
            t = f'第 {i} 章'
            loc = place
        else:
            t = title
            loc = place
        out.append(f'<tr><td class="num">{i}</td><td>{t}</td>'
                   f'<td class="loc">{loc}</td></tr>')
    out.append('</table></div>')
    return ''.join(out)


def build(lang):
    parts = ['<!DOCTYPE html><html lang="%s"><head><meta charset="utf-8"><title>%s</title>' %
             ('zh-CN' if lang == 'zh' else 'en', '雪月' if lang == 'zh' else 'Snowmoon'),
             '<style>', CSS, '</style></head><body>']
    parts.append(COVER_ZH if lang == 'zh' else COVER_EN)
    parts.append(toc(lang))
    for i in range(1, 33):
        bl = blocks[str(i)]
        zh = parse_md(os.path.join(BASE, 'zh', f'ch{i:02d}.md')) if lang == 'zh' else None
        parts.append('<section class="chapter">')
        for j, b in enumerate(bl):
            bid = f'{i}.{j}'
            if lang == 'zh':
                parts.append(render_block_zh(b, bid, zh))
            else:
                parts.append(render_block_en(b, bid))
        parts.append('</section>')
    parts.append('</body></html>')
    html = ''.join(parts)
    out = os.path.join(ROOT, 'book_zh.html' if lang == 'zh' else 'book_en.html')
    open(out, 'w', encoding='utf-8').write(html)
    print(out, len(html))


if __name__ == '__main__':
    build('en')
    build('zh')
