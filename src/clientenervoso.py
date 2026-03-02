import socket
import threading
import time
from pathlib import Path

HOST = '127.0.0.1'
PORT = 65432

NUM_CLIENTES = 200
TIMEOUT_SEC = 2

_lock = threading.Lock()
_resultados = {
    "sucesso": 0,
    "timeout": 0,
    "recusado": 0,
    "erro": 0,
}
_linhas = []


def _log(linha: str):
    with _lock:
        _linhas.append(linha)
    print(linha)


def _salvar_screenshot_e_log():
    repo_root = Path(__file__).resolve().parents[1]
    prints_dir = repo_root / "prints"
    prints_dir.mkdir(parents=True, exist_ok=True)

    resumo = (
        f"Desafio Extra — {NUM_CLIENTES} conexões simultâneas\n"
        f"Alvo: {HOST}:{PORT}\n"
        f"Timeout do cliente: {TIMEOUT_SEC}s\n\n"
        f"SUCESSO:  {_resultados['sucesso']}\n"
        f"TIMEOUT:  {_resultados['timeout']}\n"
        f"RECUSADO: {_resultados['recusado']}\n"
        f"ERRO:     {_resultados['erro']}\n"
    )

    log_path = prints_dir / "desafioextra.txt"
    with log_path.open("w", encoding="utf-8") as f:
        f.write(resumo)
        f.write("\n--- LOG ---\n")
        for linha in _linhas:
            f.write(linha + "\n")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ultimas = _linhas[-40:] if len(_linhas) > 40 else _linhas
        texto = resumo + "\n--- ÚLTIMAS LINHAS ---\n" + "\n".join(ultimas)

        fig = plt.figure(figsize=(12, 9), dpi=150)
        fig.patch.set_facecolor("white")
        plt.axis("off")
        plt.text(0.01, 0.99, texto, va="top", ha="left", family="monospace", fontsize=9)

        img_path = prints_dir / "desafioextra.png"
        plt.savefig(img_path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    except Exception as e:
        _log(f"[AVISO] Não foi possível gerar desafioextra.png: {e}")

def cliente_nervoso(id_cliente):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(TIMEOUT_SEC)
        
        _log(f"[CLIENTE {id_cliente:03d}] Tentando entrar...")
        client.connect((HOST, PORT))
        
        _log(f"[CLIENTE {id_cliente:03d}] Conectou! Esperando resposta...")
        
        msg = client.recv(1024)
        _log(f"[CLIENTE {id_cliente:03d}] SUCESSO: {msg.decode()}")
        with _lock:
            _resultados["sucesso"] += 1
        
    except socket.timeout:
        _log(f"[CLIENTE {id_cliente:03d}] TIMEOUT: O servidor demorou demais para aceitar!")
        with _lock:
            _resultados["timeout"] += 1
    except ConnectionRefusedError:
        _log(f"[CLIENTE {id_cliente:03d}] RECUSADO: A fila estava cheia!")
        with _lock:
            _resultados["recusado"] += 1
    except Exception as e:
        _log(f"[CLIENTE {id_cliente:03d}] ERRO: {e}")
        with _lock:
            _resultados["erro"] += 1
    finally:
        client.close()

if __name__ == "__main__":
    _log(f"--- INICIANDO ATAQUE DE {NUM_CLIENTES} CLIENTES SIMULTÂNEOS ---")
    
    threads = []
    for i in range(1, NUM_CLIENTES + 1):
        t = threading.Thread(target=cliente_nervoso, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

    _log("--- RESUMO ---")
    _log(
        f"SUCESSO={_resultados['sucesso']} TIMEOUT={_resultados['timeout']} "
        f"RECUSADO={_resultados['recusado']} ERRO={_resultados['erro']}"
    )
    _salvar_screenshot_e_log()