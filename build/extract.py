"""Extract Snowmoon chapters into a structured block list (blocks.json)
plus per-chapter plain-text source files for translation."""
import json, os, re, sys
from html.parser import HTMLParser
from html import unescape, escape

SRC = os.path.join(os.path.dirname(__file__), '..', 'snowmoon_src')
OUT = os.path.dirname(__file__)

VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'path', 'circle',
        'rect', 'polygon', 'line', 'polyline', 'ellipse', 'use', 'stop'}


class Node:
    __slots__ = ('tag', 'attrs', 'children', 'text')

    def __init__(self, tag=None, attrs=None, text=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.text = text

    def cls(self):
        return self.attrs.get('class', '').split()

    def find_all(self, tag=None, cls=None):
        out = []
        for c in self.children:
            if isinstance(c, Node):
                if (tag is None or c.tag == tag) and (cls is None or cls in c.cls()):
                    out.append(c)
                out.extend(c.find_all(tag, cls))
        return out

    def __repr__(self):
        return f'<{self.tag} {self.attrs}>'


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs))
        self.stack[-1].children.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(Node(None, None, data))


def parse(html):
    p = TreeBuilder()
    p.feed(html)
    return p.root


# ---------- raw html reconstruction (for svg / dz-card blocks) ----------
def raw_html(n):
    """Serialize node back to HTML string (only used for svg/dz-card)."""
    if not isinstance(n, Node):
        return ''
    if n.tag is None:
        return escape(n.text or '')
    if n.tag == 'svg':
        # re-serialize manually
        parts = []
        for c in n.children:
            parts.append(raw_html(c))
        return '<svg ' + ' '.join(f'{k}="{v}"' for k, v in n.attrs.items()) + '>' + \
            ''.join(parts) + '</svg>'
    attrs = ' '.join(f'{k}="{v}"' for k, v in n.attrs.items())
    inner = ''.join(raw_html(c) for c in n.children)
    if n.tag in VOID and not inner:
        return f'<{n.tag} {attrs}>' if attrs else f'<{n.tag}>'
    return (f'<{n.tag} {attrs}>' if attrs else f'<{n.tag}>') + inner + f'</{n.tag}>'


# ---------- inline serialization ----------
OKLCH = re.compile(r'oklch\(\s*[\d.]+\s+[\d.]+\s+([-\d.]+)')


def inline_out(n, skip_svg=True):
    """Serialize inline content to token text."""
    if not isinstance(n, Node):
        return ''
    if n.tag is None:
        return re.sub(r'\s+', ' ', n.text or '')
    tag = n.tag
    inner = ''.join(inline_out(c, skip_svg) for c in n.children)
    style = n.attrs.get('style', '')
    if tag == 'span' and 'color' in style:
        m = OKLCH.search(style)
        if m:
            return '{{%s|%s}}' % (m.group(1), inner)
        if '#' in style:
            cm = re.search(r'color\s*:\s*(#[0-9a-fA-F]{3,8})', style)
            if cm:
                return '{{%s|%s}}' % (cm.group(1), inner)
        return inner
    if tag == 'em' or tag == 'i':
        return '*%s*' % inner
    if tag == 'strong' or tag == 'b':
        return '**%s**' % inner
    if tag == 'code':
        return '`%s`' % inner
    if tag == 'svg':
        return '' if skip_svg else raw_html(n)
    if tag == 'br':
        return ' // '
    if tag == 'input':
        t = n.attrs.get('type', '')
        if t == 'range':
            return '[slider]'
        return '[input:%s]' % n.attrs.get('value', '')
    if tag == 'button':
        return '[button: %s]' % inner.strip()
    if tag in ('div', 'span', 'a', 'p', 'center', 'small', 'sup', 'sub', 'font'):
        return inner
    return inner


def inline_in(text):
    """Convert token text back to HTML (for translated content)."""
    if text is None:
        return ''
    s = escape(text, quote=False)
    # color spans
    def rep(m):
        return '<span style="color:oklch(0.7 0.15 %s)">%s</span>' % (m.group(1), m.group(2))
    s = re.sub(r'\{\{([-#0-9a-zA-Z.]+)\|([^}]*)\}\}', rep, s)
    s = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\[button:\s*([^\]]*)\]',
               r'<button style="background-color:#1a3a6a;border:1px solid #3d70c3;'
               r'padding:6px 16px;color:#cef;border-radius:3px;font-family:inherit">\1</button>', s)
    s = s.replace('[slider]', '<span style="font-family:monospace">[slider]</span>')
    return s


# ---------- block extraction ----------
def text_of(n):
    return ''.join(inline_out(c) for c in n.children).strip()


def get_body(path):
    html = open(path, encoding='utf-8').read()
    root = parse(html)
    body = root.find_all('body')[0]
    page = body.find_all('div', 'document-page')[0]
    return page


def cell_out(td):
    has_svg = any(c.tag == 'svg' for c in td.find_all() if isinstance(c, Node))
    txt = ''.join(inline_out(c) for c in td.children).strip()
    txt = re.sub(r'\s*//\s*', ' / ', txt).strip()
    return txt, int(td.attrs.get('colspan', '1')), int(td.attrs.get('rowspan', '1')), has_svg


def table_out(tbl):
    rows = []
    for tr in tbl.find_all('tr'):
        cells = []
        for c in tr.children:
            if isinstance(c, Node) and c.tag in ('td', 'th'):
                cells.append(cell_out(c))
        if cells:
            rows.append(cells)
    return rows


def lambda_cells(tr):
    return 'td'


def device_subblocks(dv):
    """Return list of ('svg', rawhtml) / ('table', rows) / ('text', s) / ('h3', s)"""
    out = []
    for c in dv.children:
        if not isinstance(c, Node):
            continue
        if c.tag == 'svg':
            out.append(('svg', raw_html(c)))
        elif c.tag == 'table':
            out.append(('table', table_out(c)))
        elif c.tag in ('h3', 'p', 'div'):
            if c.find_all('svg'):
                for s in c.find_all('svg'):
                    out.append(('svg', raw_html(s)))
                t = text_of(c)
                if t:
                    out.append(('text', t))
            else:
                t = text_of(c)
                if t:
                    out.append(('h3' if c.tag == 'h3' else 'text', t))
        elif c.tag in ('ul', 'ol'):
            items = []
            for li in c.find_all('li'):
                items.append(text_of(li))
            out.append(('list', items))
    return out


def extract_chapter(idx):
    path = os.path.join(SRC, f'chapter-{idx}.html')
    page = get_body(path)
    blocks = []
    for c in page.children:
        if not isinstance(c, Node):
            continue
        cls = c.cls()
        if 'chapter-nav' in cls or 'dark-toggle' in cls:
            continue
        if c.tag == 'h1':
            blocks.append({'t': 'h1', 'text': text_of(c)})
        elif c.tag == 'div' and 'dateline' in cls:
            kind = 'open' if 'chapter-open' in cls else 'scene'
            place = date = ''
            for s in c.find_all('span'):
                if 'place' in s.cls():
                    place = text_of(s)
                elif 'date' in s.cls():
                    date = text_of(s)
            blocks.append({'t': 'dateline', 'kind': kind, 'place': place, 'date': date})
        elif c.tag == 'hr':
            blocks.append({'t': 'hr'})
        elif c.tag == 'p':
            t = text_of(c)
            if t:
                blocks.append({'t': 'p', 'text': t})
        elif c.tag == 'blockquote':
            parts = []
            for p in c.find_all('p'):
                parts.append(text_of(p))
            if not parts:
                parts.append(text_of(c))
            blocks.append({'t': 'quote', 'text': '\n'.join(parts)})
        elif c.tag in ('ul', 'ol'):
            items = [text_of(li) for li in c.find_all('li')]
            blocks.append({'t': 'list', 'ordered': c.tag == 'ol', 'items': items})
        elif c.tag == 'div' and 'device-view' in cls:
            wide = 'wide-device-view' in cls
            left = 'device-view-left' in cls
            blocks.append({'t': 'device', 'wide': wide, 'left': left,
                           'items': device_subblocks(c)})
        elif c.tag == 'center' or (c.tag == 'div' and 'dz-card' in cls):
            inner = c.find_all('div', 'dz-card')
            if inner:
                blocks.append({'t': 'raw', 'html': raw_html(inner[0])})
            elif c.find_all('svg'):
                blocks.append({'t': 'raw', 'html': ''.join(raw_html(s) for s in c.find_all('svg'))})
        elif c.tag == 'svg':
            blocks.append({'t': 'raw', 'html': raw_html(c)})
        elif c.tag == 'br':
            continue
        elif c.tag in ('h2', 'h3', 'h4'):
            blocks.append({'t': 'h2', 'text': text_of(c)})
        else:
            t = text_of(c)
            if t:
                blocks.append({'t': 'p', 'text': t})
    # merge consecutive raw svg blocks that belong together? keep as is
    return blocks


def main():
    data = {}
    os.makedirs(os.path.join(OUT, 'src'), exist_ok=True)
    total_words = 0
    for i in range(1, 33):
        blocks = extract_chapter(i)
        data[i] = blocks
        lines = []
        for j, b in enumerate(blocks):
            bid = f'{i}.{j}'
            t = b['t']
            if t == 'p':
                lines.append(f'@@{bid}|p\n{b["text"]}\n')
                total_words += len(b['text'].split())
            elif t == 'h1':
                lines.append(f'@@{bid}|h1\n{b["text"]}\n')
            elif t == 'h2':
                lines.append(f'@@{bid}|h2\n{b["text"]}\n')
                total_words += len(b['text'].split())
            elif t == 'dateline':
                lines.append(f'@@{bid}|{b["kind"]}|place={b["place"]}|date={b["date"]}\n')
            elif t == 'quote':
                lines.append(f'@@{bid}|q\n{b["text"]}\n')
                total_words += len(b['text'].split())
            elif t == 'list':
                lines.append(f'@@{bid}|list|{"ol" if b["ordered"] else "ul"}')
                for it in b['items']:
                    lines.append('- ' + it)
                    total_words += len(it.split())
                lines.append('')
            elif t == 'device':
                lines.append(f'@@{bid}|device|{"wide" if b["wide"] else "narrow"}{"|left" if b["left"] else ""}')
                for k, (kind, val) in enumerate(b['items']):
                    if kind == 'svg':
                        lines.append(f'@@{bid}.{k}|raw-svg')
                    elif kind in ('text', 'h3'):
                        lines.append(f'@@{bid}.{k}|dvtext\n{val}\n')
                        total_words += len(val.split())
                    elif kind == 'list':
                        lines.append(f'@@{bid}.{k}|dvlist')
                        for it in val:
                            lines.append('- ' + it)
                            total_words += len(it.split())
                        lines.append('')
                    else:  # table
                        lines.append(f'@@{bid}.{k}|table')
                        for row in val:
                            cells = []
                            for txt, cs, rs, hasvg in row:
                                pre = ''
                                if cs > 1:
                                    pre += f'<c{cs}>'
                                if rs > 1:
                                    pre += f'<r{rs}>'
                                cells.append(pre + txt)
                            lines.append('| ' + ' ‖ '.join(cells))
                        lines.append('')
            elif t == 'raw':
                lines.append(f'@@{bid}|raw')
            elif t == 'hr':
                lines.append(f'@@{bid}|hr')
        open(os.path.join(OUT, 'src', f'ch{i:02d}.md'), 'w', encoding='utf-8').write('\n'.join(lines))
        print(f'ch{i:02d}: {len(blocks)} blocks')
    json.dump(data, open(os.path.join(OUT, 'blocks.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('TOTAL WORDS (approx):', total_words)


if __name__ == '__main__':
    main()
