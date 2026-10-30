"""Build the teaching archive from verified PDF files and one catalog."""
from pathlib import Path
import json,html,hashlib,re
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
kits=json.loads((ROOT/'aulas.json').read_text(encoding='utf-8'))
assert kits and len({k['id'] for k in kits})==len(kits)
(ROOT/'assets').mkdir(exist_ok=True)
cards=[];inventory=[];seen=set();E=html.escape
for k in kits:
 assert re.fullmatch(r'[a-z0-9-]+',k['id'])
 primary=next(m for m in k['materials'] if m.get('primary'))
 for m in k['materials']:
  path=ROOT/m['file'];assert path.is_file(),path
  pdf=pymupdf.open(path);text='\n'.join(p.get_text() for p in pdf)
  assert len(pdf)>0 and any(p.get_text().strip() for p in pdf)
  assert not re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}|GRR\d+|[CD]:[\\/]',text),'Inspect private information in '+str(path)
  m['pages']=len(pdf)
  if m is primary:
   thumb='assets/'+k['id']+'.png'
   pdf[0].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(str(ROOT/thumb));k['preview']=thumb
  if m['file'] not in seen:
   inventory.append({'file':m['file'],'pages':len(pdf),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});seen.add(m['file'])
  pdf.close()
 search=' '.join([k['title'],k['label'],k['area'],k['summary'],*k['topics']])
 action_label='Abrir apresentação' if k.get('kind')=='apresentacao' else 'Abrir material completo'
 cards.append(f'''<article class="kit" id="kit-{k['id']}" data-search="{E(search,quote=True)}" data-area="{E(k['area'],quote=True)}" data-level="{E(k['level'],quote=True)}"><a class="preview" href="{E(primary['file'],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Abrir PDF: {E(k['title'],quote=True)}"><img src="{k['preview']}" alt="Prévia do início do material {E(k['label'],quote=True)}" width="834" height="1179" loading="lazy"></a><div class="kit-content"><p class="label">{E(k['area'])} · {E(k['audience'])}</p><h3>{E(k['title'])}</h3><p class="summary">{E(k['summary'])}</p><ul class="tags"><li>{E(k['level'])}</li><li>{primary['pages']} páginas no material principal</li><li>{len(k['materials'])} PDFs no conjunto</li></ul><div class="actions"><a class="button primary-pdf" href="{primary['file']}" target="_blank" rel="noopener noreferrer">{action_label} ↗</a><button class="button secondary" type="button" data-kit="{k['id']}">Explorar conjunto</button></div></div></article>''')
template=(ROOT/'index.template.html').read_text(encoding='utf-8')
filters='<button class="filter" data-area-filter="all" aria-pressed="true" type="button">Todos</button>'+''.join('<button class="filter" data-area-filter="'+E(area,quote=True)+'" aria-pressed="false" type="button">'+E(area)+'</button>' for area in sorted({k['area'] for k in kits}))
label=str(len(kits))+' '+('conjunto' if len(kits)==1 else 'conjuntos')+' · '+str(len(inventory))+' PDFs'
index=template.replace('__CARDS__','\n'.join(cards)).replace('__CATALOG__',json.dumps(kits,ensure_ascii=False).replace('<','\\u003c')).replace('__COUNT_LABEL__',label)
assert '__CARDS__' not in index and '__CATALOG__' not in index
level_filters='<button class="filter" data-level-filter="all" aria-pressed="true" type="button">Todos os níveis</button>'+''.join('<button class="filter" data-level-filter="'+E(level,quote=True)+'" aria-pressed="false" type="button">'+E(level)+'</button>' for level in ['Matemática olímpica','Ensino médio / básico','Universitário'])
index=index.replace('__FILTERS__',filters).replace('__LEVEL_FILTERS__',level_filters)
(ROOT/'index.html').write_text(index,encoding='utf-8')
(ROOT/'.nojekyll').write_text('',encoding='utf-8')
(ROOT/'manifesto.json').write_text(json.dumps({'kits':len(kits),'pdfs':inventory},ensure_ascii=False,indent=2),encoding='utf-8')
print('CONJUNTOS',len(kits),'PDFS',len(inventory))
