import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent

@pytest.mark.skipif(not shutil.which("node"), reason="precisa do node")
def test_javascript_do_frontend():
    saida = subprocess.run(["node", "--test", "tests/frontend.test.mjs"], cwd=RAIZ, capture_output=True, text=True, timeout=60)
    assert saida.returncode == 0, saida.stdout + saida.stderr
