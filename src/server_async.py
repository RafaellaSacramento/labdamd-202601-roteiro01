"""Wrapper para executar o servidor assíncrono da raiz do repositório.

O roteiro pede que o arquivo principal seja criado na raiz: `../server_async.py`.
Se você rodar este arquivo dentro de `src/`, ele delega para o arquivo correto.
"""

from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "server_async.py"
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
