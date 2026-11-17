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

    def test_readme_uses_the_portfolio_owners_voice(self):
        self.assertNotRegex((ROOT / 'README.md').read_text(encoding='utf-8'), EDITORIAL_HANDOFF)

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
        self.assertIn('VERSÕES DE TRABALHO', BY_ID['poti-simulados-algebra']['credit'])


if __name__ == '__main__':
    unittest.main()
