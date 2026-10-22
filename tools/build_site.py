"""Build the public FLIPSEED student website (index.html) from a saved copy of the FLIPSEED artifact.
Usage: python3 tools/build_site.py <artifact.html> <output index.html>
Keeps only published activities and points every student link at the GitHub Pages address."""
import json, re, sys
SITE = 'https://jameslazona.github.io/flipseed/'
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
m = re.search(r'(<script id="fs-data" type="application/json">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
data['activities'] = [a for a in data.get('activities', []) if a.get('status') == 'published']
data['settings'] = {'link': SITE}
data['site'] = True
js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
html = html[:m.start(2)] + js + html[m.end(2):]
open(out, 'w', encoding='utf-8').write(html)
print('activities:', [a['code'] + ' ' + a['title'] for a in data['activities']], '| bytes:', len(html.encode()))
