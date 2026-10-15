import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from cst2025_bridge import generate_job, analyze_s1p, run_unitcell, health

class BridgeTests(unittest.TestCase):
    def test_generation(self):
        import ast
        x=generate_job('test_1',2.45)
        ast.parse(x['source'])
        self.assertEqual(x['status'],'generated_not_executed')
    def test_bad_frequency(self):
        for f in [0,-1,float('nan'),float('inf'),1000]:
            with self.assertRaises(ValueError):generate_job('test',f)
    def test_bad_name(self):
        with self.assertRaises(ValueError):generate_job('../unsafe',2.45)
    def test_s1p(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.s1p'
            p.write_text('# GHZ S RI R 50\n1 0.5 0\n2 0.1 0\n')
            x=analyze_s1p(str(p))
            self.assertEqual(x['points'],2)
            self.assertEqual(x['status'],'parsed_not_simulated')
    def test_bad_s1p(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.s1p';p.write_text('bad')
            with self.assertRaises(ValueError):analyze_s1p(str(p))
    def test_no_approval(self):
        os.environ.pop('CST_APPROVAL_TOKEN',None)
        with self.assertRaises(PermissionError):run_unitcell('fake')
    def test_health(self):
        self.assertIn('execution_configured',health())

if __name__=='__main__':unittest.main()
