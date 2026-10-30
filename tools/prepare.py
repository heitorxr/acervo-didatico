"""Prepare public copies from a private curation plan; originals stay intact."""
from pathlib import Path
import json,re,sys,hashlib
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
plan_path=Path(sys.argv[1]);plan=json.loads(plan_path.read_text(encoding='utf-8'))
assert plan['authorship_confirmed'] is True
(ROOT/'pdfs').mkdir(exist_ok=True)
catalog=[];report=[]
for kit in plan['kits']:
 public={k:v for k,v in kit.items() if k!='materials'};public['materials']=[]
 for material in kit['materials']:
  source=Path(material['source']);target=ROOT/material['file']
  assert source.is_file() and source.resolve()!=target.resolve()
  before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
  original=pymupdf.open(source);original_text='\n'.join(p.get_text() for p in original)
  assert not re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}|GRR\d+',original_text),'Inspect personal data in source'
  hidden=material.get('hide_names',[]);removed=0
  for page in original:
   for name in hidden:
    if ' ' in name:
     areas=page.search_for(name)
    else:
     areas=[pymupdf.Rect(w[:4]) for w in page.get_text('words') if w[4].strip(' ,.;:!?()[]—–').casefold()==name.casefold()]
    for rect in areas:
     page.add_redact_annot(rect,fill=(1,1,1));removed+=1
   if hidden:page.apply_redactions(images=2,graphics=0,text=0)
   for link in list(page.get_links()):
    uri=link.get('uri','')
    if uri.startswith('file:') or re.match(r'[A-Za-z]:',uri):page.delete_link(link)
  added_author=not bool(re.search(r'Heitor',original_text,re.I))
  if added_author:
   page=original[0];w,h=page.rect.width,page.rect.height
   choices=[pymupdf.Rect(28,h-25,w-28,h-5),pymupdf.Rect(28,5,w-28,25)]
   words=page.get_text('words');area=next((r for r in choices if not any(r.intersects(pymupdf.Rect(word[:4])) for word in words)),None)
   assert area is not None,'No safe author-credit space in '+str(source)
   result=page.insert_textbox(area,'Material didático de Heitor Cardoso Fernandes',fontname='helv',fontsize=8,color=(.25,.32,.30),align=1)
   assert result>=0
  result=pymupdf.open();result.insert_pdf(original)
  result.set_metadata({'title':kit['title']+' — '+material['label'],'author':'Heitor Cardoso Fernandes','subject':'Material didático para ensino e estudo de exatas.'})
  result.save(target,garbage=4,deflate=True,clean=True)
  result.close();original.close()
  check=pymupdf.open(target);new_text='\n'.join(p.get_text() for p in check)
  assert not any(re.search(r'\b'+re.escape(name)+r'\b',new_text,re.I) for name in hidden)
  assert 'Heitor' in new_text or 'Heitor' in str(check.metadata)
  # Preserve every original extracted word outside the student-name redactions.
  allowed=set(word for name in hidden for word in name.split())
  new_words=set(new_text.split())
  missing=[word for word in original_text.split() if word.strip(' ,.;:!?()[]—–') not in allowed and word not in new_words]
  assert not missing,'Unexpected content loss (review privately): '+str(source)
  assert before_hash==hashlib.sha256(source.read_bytes()).hexdigest(),'Original was changed'
  report.append({'source':str(source),'public_file':material['file'],'source_sha256':before_hash,'public_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'pages':len(check),'student_name_redactions':removed,'author_credit_added':added_author})
  public['materials'].append({k:material[k] for k in ['file','label','primary'] if k in material})
 catalog.append(public)
assert len({k['id'] for k in catalog})==len(catalog)
(ROOT/'aulas.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
(plan_path.parent/'preparation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('CONJUNTOS_PREPARADOS',len(catalog),'PDFS_PREPARADOS',len(report),'CREDITOS_ADICIONADOS',sum(r['author_credit_added'] for r in report),'NOMES_RETIRADOS',sum(r['student_name_redactions'] for r in report))
