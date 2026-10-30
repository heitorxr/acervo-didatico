# Acervo didático — Heitor Cardoso Fernandes

Aulas, apostilas, exercícios comentados e apresentações de apoio, organizados em 20 conjuntos e 37 PDFs.

Site: https://heitorxr.github.io/acervo-didatico/

## Leitura

O acervo permite buscar por tema, filtrar por área, consultar os conteúdos e abrir os PDFs sem navegar por código. Cada conjunto reúne o documento principal e seus complementos. Os filtros de nível e de área podem ser combinados com a busca.

O catálogo inclui Cálculo 1, funções de várias variáveis, integração, Geometria Analítica, nivelamento algébrico, preparação olímpica, Matemática para concursos e materiais de Física.

## Curadoria e autoria

- As cópias e revisões do mesmo material não foram contadas como conjuntos diferentes.
- A autoria dos documentos sem assinatura foi confirmada pelo autor; as cópias públicas receberam um crédito de autoria em espaço livre, sem alterar a explicação ou os exercícios.
- Os nomes dos alunos foram retirados das cópias e dos nomes dos arquivos públicos. Os originais foram preservados.
- As referências e os créditos existentes nos materiais foram mantidos, incluindo a inspiração no material da professora Evelin no segundo aulão de Cálculo 1 e as listas de CMI012 na aula de vetores.
- Livros, listas de professores e outros arquivos de terceiros usados como fonte de preparação não foram redistribuídos como materiais do autor.
- A curadoria e a organização do site tiveram apoio de IA. Não foi realizada uma nova revisão matemática integral de todos os materiais históricos.

A publicação do acervo não atribui uma nova licença aos materiais e referências de terceiros.

## Arquivos e reprodução

- `aulas.json`: catálogo canônico.
- `pdfs/`: cópias públicas dos documentos.
- `assets/`: prévias reais do início dos PDFs.
- `manifesto.json`: contagem, páginas e SHA-256 dos documentos publicados.
- `index.template.html` e `tools/build.py`: geração do site sem dependências remotas para exibição.
- `tools/verify.py`: testes em Chrome para todos os conjuntos, busca, filtros, documentos, fechamento e links diretos em desktop e celular.
- `tools/prepare.py`: preparação de cópias a partir de um plano privado fornecido explicitamente. O plano de origem, seus caminhos pessoais e os relatórios de inspeção não são publicados.

Para reconstruir o site a partir dos PDFs já disponíveis:

```text
python tools/build.py
python tools/verify.py
```

O primeiro comando requer PyMuPDF. O segundo requer Playwright e um Chrome disponível; o executável e a pasta de inspeção podem ser ajustados ao ambiente. Não é necessário compilar os documentos novamente para consultar ou reconstruir o índice.

O primeiro aulão foi compilado a partir do LaTeX fornecido pelo autor. Os materiais preparados foram conferidos quanto a abertura, preservação do conteúdo fora das referências pessoais removidas e autoria das cópias públicas. Os PDFs e a navegação publicados são verificados antes da entrega.

## Classificação por leitura do conteúdo

Cada conjunto apresenta seu nível e a justificativa na ficha. A preparação olímpica reúne a sequência de aulas e os simulados POTI; o ensino médio/básico reúne álgebra elementar, concursos, trigonometria, mecânica e circuitos resistivos; o universitário reúne cálculo, vetores no espaço, estática 3D e LC/RLC por equações diferenciais. Nivelamento algébrico permanece no básico mesmo quando destinado a graduandos. Questões chamadas de desafios não tornam automaticamente uma aula de ensino médio uma aula olímpica.

## Materiais recebidos do Overleaf

A sequência POTI inclui as aulas 1 a 4 e a aula de recorrências. A lista de quadráticas/polinômios é complemento da aula 2; os dois documentos de simulado estão agrupados, sem tratá-los como uma única prova ou como gabarito um do outro. A Aula 1 não foi duplicada. Créditos nominais foram acrescentados, com autorização do autor, aos três materiais que não os continham, preservando fontes de questões de terceiros. Os simulados estão claramente marcados como versões de trabalho, com pontos de revisão descritos nas fichas e aviso nos PDFs. Datas automáticas de recompilação não comprovam quando as aulas ocorreram.

`tools/import_poti.py CAMINHO_DO_PROJETO_PRIVADO` prepara as cópias autorizadas e o catálogo, sem publicar os ZIPs/fontes privados.

## Correção de curadoria

Por esclarecimento do autor, Introdução ao jamovi não é de sua autoria e foi retirada. Materiais magnéticos é um trabalho acadêmico, e Rotações e simetria integra um projeto de iniciação científica: ambos foram retirados do acervo de aulas. Circuitos LC/RLC foi preservado separadamente. As cópias originais foram preservadas fora desta publicação; os commits anteriores não foram reescritos.
