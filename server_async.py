import asyncio

HOST = '127.0.0.1'
PORT = 65432

async def _processamento_pesado_simulado(addr, msg: str):
    try:
        await asyncio.sleep(5)
        if msg:
            print(f"[{addr}] Processamento pesado concluído: {msg}")
        else:
            print(f"[{addr}] Processamento pesado concluído: <sem dados>")
    except Exception:
        pass


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Corrotina chamada pelo Event Loop para cada nova conexão.
    Substitui a função que antes rodava em uma Thread separada.
    """
    addr = writer.get_extra_info('peername')
    print(f"[NOVA CONEXÃO] {addr}")

    try:
        data = await asyncio.wait_for(reader.read(1024), timeout=0.2)
    except asyncio.TimeoutError:
        data = b""

    msg = data.decode('utf-8', errors='replace')
    if msg:
        print(f"[{addr}] Recebido: {msg}")
    else:
        print(f"[{addr}] Recebido: <sem dados>")

    asyncio.create_task(_processamento_pesado_simulado(addr, msg))

    if msg:
        resposta = f"Processado: {msg}".encode('utf-8')
    else:
        resposta = b"Atendido com sucesso."

    try:
        writer.write(resposta)
        await writer.drain()
    except (ConnectionResetError, BrokenPipeError):
        pass

    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass

    print(f"[DESCONECTADO] {addr}")


async def main():
    """
    Ponto de entrada assíncrono: cria e inicia o servidor.
    """
    server = await asyncio.start_server(handle_client, HOST, PORT)

    sockets = server.sockets or []
    if sockets:
        addrs = ", ".join(str(sock.getsockname()) for sock in sockets)
        print(f"[ASSÍNCRONO] Servidor rodando em {addrs} — Event Loop ativo.")
    else:
        print(f"[ASSÍNCRONO] Servidor rodando em {HOST}:{PORT} — Event Loop ativo.")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
