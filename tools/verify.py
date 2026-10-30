"""Exercise every teaching kit in Chrome, on desktop and phone widths."""
from pathlib import Path
import json,os,argparse
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
kits=json.loads((ROOT/'aulas.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'manifesto.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('url',nargs='?',default=(ROOT/'index.html').as_uri())
parser.add_argument('--out',type=Path,default=ROOT/'qa')
parser.add_argument('--chrome',type=Path,default=Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Google/Chrome/Application/chrome.exe')
args=parser.parse_args();url=args.url
OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
report={'kits':len(kits),'pdfs':len(manifest['pdfs']),'url_kind':'live' if url.startswith('https:') else 'local','checks':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=str(args.chrome) if args.chrome.exists() else None,headless=True)
 for width,height,label in [(1440,1000,'desktop'),(390,844,'mobile')]:
  page=browser.new_page(viewport={'width':width,'height':height})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url,wait_until='load',timeout=60000)
  assert page.locator('article.kit').count()==len(kits)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),label
  for area in sorted({k['area'] for k in kits}):
   page.get_by_role('button',name=area,exact=True).click()
   expected=sum(k['area']==area for k in kits)
   assert page.locator('article.kit:visible').count()==expected,(label,area)
  page.locator('[data-area-filter="all"]').click()
  for level in sorted({k['level'] for k in kits}):
   page.locator('[data-level-filter]').filter(has_text=level).click()
   assert page.locator('article.kit:visible').count()==sum(k['level']==level for k in kits)
   for area in sorted({k['area'] for k in kits}):
    page.get_by_role('button',name=area,exact=True).click()
    assert page.locator('article.kit:visible').count()==sum(k['level']==level and k['area']==area for k in kits)
   page.locator('[data-area-filter="all"]').click()
  page.locator('[data-level-filter="all"]').click()
  page.locator('#search').fill('termo-inexistente-xyz')
  assert page.locator('article.kit:visible').count()==0 and page.locator('#empty').is_visible()
  page.locator('#search').fill('')
  assert page.locator('article.kit:visible').count()==len(kits)
  for k in kits:
   primary=next(m for m in k['materials'] if m.get('primary'))
   card=page.locator('#kit-'+k['id']);card.scroll_into_view_if_needed()
   page.wait_for_function('(id)=>{const img=document.querySelector("#kit-"+id+" img");return img.complete&&img.naturalWidth>0}',arg=k['id'])
   assert card.locator('.primary-pdf').get_attribute('href')==primary['file']
   card.locator('[data-kit]').click()
   assert page.locator('#kit-dialog').is_visible()
   assert page.locator('#detail-title').inner_text()==k['title']
   assert page.locator('.material').count()==len(k['materials'])
   assert page.locator('.material').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==[m['file'] for m in k['materials']]
   assert page.evaluate('document.querySelector("dialog").scrollWidth<=document.querySelector("dialog").clientWidth+1')
   page.screenshot(path=str(OUT/(label+'-'+k['id']+'-details.png')))
   page.keyboard.press('Escape');assert not page.locator('#kit-dialog').is_visible()
   report['checks'].append(label+': '+k['id'])
  page.evaluate('scrollTo(0,0)');page.wait_for_timeout(150)
  page.screenshot(path=str(OUT/(label+'.png')),full_page=True)
  page.screenshot(path=str(OUT/(label+'-viewport.png')))
  assert not errors,errors
  page.close()
 page=browser.new_page(viewport={'width':390,'height':844})
 page.goto(url.split('#')[0]+'#aula-'+kits[-1]['id'],wait_until='load')
 assert page.locator('#kit-dialog').is_visible()
 assert page.locator('#detail-title').inner_text()==kits[-1]['title']
 page.close();browser.close()
report['checks'].append('direct kit link')
(OUT/(report['url_kind']+'-report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
