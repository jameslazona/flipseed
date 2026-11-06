"""Build the public FLIPSEED student website from a saved copy of the FLIPSEED artifact.
Usage: python3 tools/build_site.py <artifact.html> <output index.html>

The page itself holds NO activities, so nobody can browse lessons from it.
Each published activity is written to activities/<code>.json and the page only
loads the one named in the link (…/flipseed/#a=<code>). Files for activities that
are no longer published are removed."""
import json, os, re, sys
SITE = 'https://jameslazona.github.io/flipseed/'
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
m = re.search(r'(<script id="fs-data" type="application/json">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
published = [a for a in data.get('activities', []) if a.get('status') == 'published']

act_dir = os.path.join(os.path.dirname(os.path.abspath(out)), 'activities')
os.makedirs(act_dir, exist_ok=True)
keep = set()
for a in published:
    code = str(a.get('code', '')).lower()
    if not re.fullmatch(r'[a-z0-9]{3,8}', code):
        continue
    keep.add(code + '.json')
    path = os.path.join(act_dir, code + '.json')
    body = json.dumps(a, ensure_ascii=False, separators=(',', ':'))
    if not os.path.exists(path) or open(path, encoding='utf-8').read() != body:
        open(path, 'w', encoding='utf-8').write(body)

# the mission map: the missions the teacher opened, in order (FLIPSEED writes this list each time it saves)
pub_codes = {str(a.get('code','')).lower() for a in published}
missions = [m for m in (data.get('settings') or {}).get('jmeta') or [] if str(m.get('code','')).lower() in pub_codes]
body = json.dumps({'missions': missions}, ensure_ascii=False, separators=(',', ':'))
jpath = os.path.join(act_dir, 'journey.json')
if not os.path.exists(jpath) or open(jpath, encoding='utf-8').read() != body:
    open(jpath, 'w', encoding='utf-8').write(body)
keep.add('journey.json')

for f in os.listdir(act_dir):
    if f.endswith('.json') and f not in keep:
        os.remove(os.path.join(act_dir, f))

data['activities'] = []
old = data.get('settings') or {}
data['settings'] = dict(old, link=SITE)  # keep the teacher's choices (sounds, classes, tracking address)
data['site'] = True
js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
html = html[:m.start(2)] + js + html[m.end(2):]
if '<meta charset' not in html[:600].lower():
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n') + html + '\n</body></html>'
open(out, 'w', encoding='utf-8').write(html)
print('activities:', sorted(keep), '| page bytes:', len(html.encode()))
