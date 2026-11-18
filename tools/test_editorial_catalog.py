"""Regression checks for the teaching archive's editorial metadata."""
from pathlib import Path
import ast
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / 'aulas.json').read_text(encoding='utf-8'))
BY_ID = {kit['id']: kit for kit in CATALOG}
EDITORIAL_HANDOFF = re.compile(
    r'enviados? pelo autor|fornecid[oa]s? pelo autor|confirmad[oa]s? pelo autor|'
    r'recebid[oa]s? em fonte|autoriza[çc][ãa]o do autor|esclarecimento do autor|'
    r'materiais recebidos do Overleaf|ZIP de origem',
    re.IGNORECASE,
)


class EditorialCatalogTests(unittest.TestCase):
    def test_multivariable_title_centers_calculus(self):
        self.assertEqual(BY_ID['calculo-multivariado']['title'], 'Cálculo multivariado')

    def test_algebra_leveling_is_for_incoming_undergraduates(self):
        kit = BY_ID['nivelamento-algebra']
        self.assertIn('calouros universitários', kit['audience'].lower())
        self.assertIn('pré-cálculo', kit['summary'].lower())
        self.assertIn('conceitos básicos', kit['summary'].lower())
        self.assertNotRegex(json.dumps(kit, ensure_ascii=False), r'(?i)v[ií]deo')
        self.assertEqual(kit['level'], 'Ensino médio / básico')

    def test_catalog_does_not_describe_an_editor_receiving_my_work(self):
        for kit in CATALOG:
            with self.subTest(kit=kit['id']):
                self.assertNotRegex(json.dumps(kit, ensure_ascii=False), EDITORIAL_HANDOFF)

    def test_removed_editorial_disclaimers_do_not_regenerate(self):
        patterns = [
            r'versões\W+anteriores\W+e\W+cópias\W+de\W+trabalho',
            r'(?:livros|arquivos|listas)[^.\n]*terceiros[^.\n]*fonte\W+de\W+preparação',
            r'cópias\W+e\W+revisões\W+do\W+mesmo\W+material',
        ]
        for name in ['index.template.html', 'index.html', 'README.md']:
            text = (ROOT / name).read_text(encoding='utf-8')
            for pattern in patterns:
                with self.subTest(file=name, pattern=pattern):
                    self.assertNotRegex(text, re.compile(pattern, re.IGNORECASE))

    def test_readme_uses_the_portfolio_owners_voice(self):
        self.assertNotRegex((ROOT / 'README.md').read_text(encoding='utf-8'), EDITORIAL_HANDOFF)

    def test_single_pdf_cards_use_the_singular(self):
        index = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertNotRegex(index, r'\b1 PDFs no conjunto\b')
        self.assertIn('1 PDF no conjunto', index)
        self.assertIn('2 PDFs no conjunto', index)

    def test_compilation_date_note_is_central(self):
        note = 'A data de compilação dos PDFs nem sempre corresponde à data em que a aula foi dada.'
        template = (ROOT / 'index.template.html').read_text(encoding='utf-8')
        self.assertEqual(template.count(note), 1)
        for kit in CATALOG:
            with self.subTest(kit=kit['id']):
                self.assertNotIn('data do PDF é de compilação', kit['credit'])
                self.assertNotIn('não comprova a data da aula', kit['credit'])
        self.assertNotIn('não comprova a data da aula', (ROOT / 'tools/import_poti.py').read_text(encoding='utf-8'))

    def test_poti_importer_keeps_the_same_editorial_voice(self):
        # Execute only the pure metadata helpers, never PDF import or filesystem writes.
        tree = ast.parse((ROOT / 'tools/import_poti.py').read_text(encoding='utf-8'))
        nodes = [node for node in tree.body if
                 (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'base_credit' for t in node.targets))
                 or (isinstance(node, ast.FunctionDef) and node.name == 'kit')]
        namespace = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<POTI metadata>', 'exec'), namespace)
        kit = namespace['kit']('sample', 'Sample', 'Sample', 'Sample', [], 'Sample', [])
        self.assertNotRegex(json.dumps(kit, ensure_ascii=False), EDITORIAL_HANDOFF)
        self.assertNotRegex((ROOT / 'tools/import_poti.py').read_text(encoding='utf-8'), EDITORIAL_HANDOFF)

    def test_third_party_references_remain_identified(self):
        self.assertIn('Evelin', BY_ID['calculo-1-derivadas']['credit'])
        self.assertIn('CMI012', BY_ID['geometria-analitica']['credit'])
        for source in ['SBM', 'OBMEP', 'ITA', 'UECE']:
            self.assertIn(source, BY_ID['poti-aula-2-quadraticas']['credit'])
        self.assertIn('XX Olimpíada Brasileira de Matemática', BY_ID['poti-recorrencias']['credit'])
        self.assertNotIn('versões de trabalho', BY_ID['poti-simulados-algebra']['credit'].lower())

    def test_simulado_credits_do_not_publish_a_correction_log(self):
        credit = BY_ID['poti-simulados-algebra']['credit']
        self.assertIn('simulados distintos', credit)
        for phrase in ['A questão 4 considera', 'A questão 15 determina', 'A questão 11 justifica']:
            self.assertNotIn(phrase, credit)
            self.assertNotIn(phrase, (ROOT / 'tools/import_poti.py').read_text(encoding='utf-8'))

    def test_simulados_are_published_without_work_in_progress_labels(self):
        kit = BY_ID['poti-simulados-algebra']
        self.assertEqual(kit['title'], 'Simulados de álgebra e resoluções')
        self.assertNotRegex(json.dumps(kit, ensure_ascii=False), r'(?i)versões de trabalho|em revisão|revisão pendente|revisão matemática pendente')
        importer = (ROOT / 'tools/import_poti.py').read_text(encoding='utf-8')
        self.assertNotIn('VERSÕES DE TRABALHO', importer)
        self.assertIn("'revisoes'", importer)


class ArchiveSelectionTests(unittest.TestCase):
    def test_ohm_kirchhoff_identifies_vcnp(self):
        kit = BY_ID['eletricidade-ohm-kirchhoff']
        self.assertIn('VCNP', kit['audience'])
        self.assertIn('pré-vestibular', kit['summary'])

    def test_unconfirmed_lc_rlc_lesson_is_not_published(self):
        self.assertNotIn('magnetismo-circuitos', BY_ID)
        self.assertFalse((ROOT / 'pdfs/circuitos-lc-rlc.pdf').exists())
        self.assertFalse((ROOT / 'assets/magnetismo-circuitos.png').exists())


if __name__ == '__main__':
    unittest.main()
