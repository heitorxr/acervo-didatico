"""Import the authorized POTI PDFs, preserving originals and avoiding duplicates."""
from pathlib import Path
from collections import Counter
import argparse,json,hashlib,re
import pymupdf
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source_project',type=Path)
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1];SRC=args.source_project.resolve()
assert (SRC/'compilacao.json').is_file()
compiled=json.loads((SRC/'compilacao.json').read_text(encoding='utf-8'))
assert len(compiled)==8 and all(r['compiler_exit']==0 for r in compiled)
CAT=ROOT/'aulas.json';catalog=json.loads(CAT.read_text(encoding='utf-8'))
existing={k['id']:k for k in catalog}
base_credit='Material didático de Heitor Cardoso Fernandes, recebido em fonte LaTeX do Overleaf. Créditos e referências originais preservados. Onde a fonte usa data automática, a data do PDF é de compilação e não comprova a data da aula.'
def material(key,label,primary=False,warning=False):
 source=SRC/'pdfs'/(key+'.pdf');dest=ROOT/'pdfs'/(key+'.pdf')
 before=hashlib.sha256(source.read_bytes()).hexdigest()
 doc=pymupdf.open(source);original_text='\n'.join(p.get_text() for p in doc)
 result=pymupdf.open();result.insert_pdf(doc)
 for page in result:
  for link in list(page.get_links()):
   if link.get('uri','').startswith('file:'):page.delete_link(link)
 if warning:
  area=pymupdf.Rect(25,12,result[0].rect.width-25,42)
  assert not any(area.intersects(pymupdf.Rect(w[:4])) for w in result[0].get_text('words'))
  assert result[0].insert_textbox(area,'VERSÃO DE TRABALHO: revisão matemática pendente. Consulte a nota no acervo.',fontsize=8.5,fontname='helv',color=(.6,.18,.08))>=0
 result.set_metadata({'title':label,'author':'Heitor Cardoso Fernandes','subject':'POTI — preparação para olimpíadas de Matemática.'})
 result.save(dest,garbage=4,deflate=True,clean=True);result.close();doc.close()
 with pymupdf.open(dest) as check:
  new_text='\n'.join(p.get_text() for p in check)
  assert Counter(original_text.split())<=Counter(new_text.split()),'Unexpected academic-content loss'
  assert 'Heitor Cardoso Fernandes' in new_text
  assert not re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}|GRR\d+|[CD]:[/\\]',new_text)
 assert hashlib.sha256(source.read_bytes()).hexdigest()==before
 return {'file':'pdfs/'+dest.name,'label':label,'primary':primary}
def kit(key,title,label,summary,topics,prerequisites,materials,credit=None):
 return {'id':key,'title':title,'label':label,'area':'Matemática','audience':'Preparação para olimpíadas de Matemática — POTI','summary':summary,'topics':topics,'prerequisites':prerequisites,'credit':credit or base_credit,'materials':materials,'level':'Matemática olímpica','level_reason':'Material da sequência POTI, identificado nos arquivos enviados pelo autor e pelo desenvolvimento de problemas e argumentos de preparação olímpica.'}
new=[]
new.append(kit('poti-aula-2-quadraticas','Funções quadráticas e revisão de funções','Aula 2 POTI e lista complementar','Revisão de paridade, composição e inversão de funções, seguida de equações quadráticas, dedução de Bhaskara, discriminante, soma e produto. A lista complementar também traz exercícios de polinômios.', ['Funções pares e ímpares','Composição, identidade e inversa','Dedução de Bhaskara e discriminante','Soma e produto das raízes','Lista complementar: quadráticas e polinômios'],'Álgebra elementar e conceitos de função.',[material('poti-aula-2-quadraticas','Aula 2 — Revisão e funções quadráticas',True),material('poti-lista-quadraticas-polinomios','Lista complementar — Quadráticas e polinômios')],base_credit+' Na lista, o crédito de organização foi acrescentado por autorização do autor; foram preservadas as indicações SBM, OBMEP, ITA e UECE.'))
new.append(kit('poti-aula-3-girard','Relações de Girard e raízes de polinômios','Aula 3 POTI','Dedução das relações entre raízes e coeficientes em graus 2 e 3, generalização, revisão de somatórios e exemplos de aplicação. A aula encerra com uma introdução aos números complexos.',['Raízes e coeficientes','Relações de Girard em graus 2 e 3','Generalização e somatórios','Exemplos e preparação para números complexos'],'Equações quadráticas, soma e produto e operações com polinômios.',[material('poti-aula-3-girard','Aula 3 — Relações de Girard',True)]))
new.append(kit('poti-aula-4-complexos','Números complexos e aplicações olímpicas','Aula 4 POTI','Aula sobre forma algébrica, operações, conjugado, plano complexo, módulo e argumento. Desenvolve as formas trigonométrica e exponencial, De Moivre, raízes da unidade e aplicações geométricas.',['Forma algébrica e operações','Conjugado, módulo e argumento','Formas trigonométrica e exponencial','De Moivre e raízes n-ésimas','Rotações e raízes da unidade'],'Álgebra, produtos notáveis, trigonometria elementar e coordenadas cartesianas.',[material('poti-aula-4-complexos','Aula 4 — Números complexos',True)]))
new.append(kit('poti-recorrencias','Relações de recorrência, telescopagem e indução','POTI — Nível 3','A partir de um problema da Olimpíada Brasileira de Matemática, a aula constrói recorrências, desenrola produtos e somas telescópicas e relaciona o método à indução. O ZIP de origem tinha o nome regressão, mas o conteúdo é de recorrências.',['Condições iniciais e recorrências','Produtos e somas telescópicos','Indução matemática','Transformação por ponto fixo','Recorrências com mais de um termo'],'Álgebra, sequências e operações com somatórios e produtos.',[material('poti-recorrencias','Aula — Relações de recorrência',True)],base_credit+' Crédito nominal acrescentado por autorização do autor; preservada a referência à XX Olimpíada Brasileira de Matemática, Problema 5.'))
review_note='VERSÕES DE TRABALHO — revisão matemática pendente. No simulado de cinco questões, a questão 4 pressupõe três raízes reais incompatíveis com as demais condições. Nas resoluções do outro simulado, a questão 15 determina os valores nos inteiros positivos, mas não uma função única em todos os reais. Os documentos são de simulados distintos: as resoluções não são o gabarito das cinco questões.'
new.append(kit('poti-simulados-algebra','Simulados de álgebra e resoluções — versões de trabalho','POTI · materiais de avaliação em revisão','Dois documentos distintos: um simulado com cinco questões e resoluções das questões 11 e 15 de outro simulado. Versões históricas de trabalho, com pontos que exigem revisão antes do uso como avaliação ou gabarito final.',['Polinômios e divisibilidade','Funções periódicas','Raízes, coeficientes e relações algébricas','Somas parciais e recorrências','Revisão pendente de hipóteses e enunciados'],'Funções, polinômios, equações quadráticas e sequências.',[material('poti-simulado-algebra','Simulado — Cinco questões de álgebra (em revisão)',True,True),material('poti-simulado-resolucoes','Outro simulado — Resoluções das questões 11 e 15 (em revisão)',False,True)],base_credit+' '+review_note))
# Retain the previously published first lesson and its historical date.
existing['funcoes-olimpiadas']['label']='Aula 1 POTI e desafios de composição'
ids={k['id'] for k in new}
catalog=[k for k in catalog if k['id'] not in ids]
position=next(i for i,k in enumerate(catalog) if k['id']=='funcoes-olimpiadas')+1
catalog[position:position]=new
assert len({k['id'] for k in catalog})==len(catalog)
CAT.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'kits':len(catalog),'pdfs':len({m['file'] for k in catalog for m in k['materials']}),'poti_kits':sum(k['level']=='Matemática olímpica' for k in catalog),'new_kits':[k['id'] for k in new],'new_pdfs':[m['file'] for k in new for m in k['materials']],'review_note':review_note,'first_lesson_existing_pdf_preserved':True}
(SRC/'importacao-publica.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
