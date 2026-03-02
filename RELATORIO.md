# Relatório Técnico — Laboratório 2
## Questão 1 — Backlog e Recusa de Conexões

No teste com o servidor com gargalo ([src/servergargalo.py](src/servergargalo.py)), o `listen(1)` configura um *backlog* muito pequeno (fila de conexões pendentes gerenciada pelo Sistema Operacional). Como esse servidor atende de forma sequencial e fica “ocupado” por +/-5s antes de voltar ao `accept()`, ele deixa de drenar a fila com rapidez. Quando o [src/clientenervoso.py](src/clientenervoso.py) dispara 10 conexões simultâneas, a fila do SO tende a esgotar.

- Quando o backlog esgota, novas tentativas de conexão podem ser **recusadas** imediatamente (erro `ConnectionRefusedError`) ou podem **demorar demais** e estourar o tempo limite do cliente (`socket.timeout`).
- O roteiro já antecipa essa variabilidade: o valor passado ao `listen()` é uma “dica” para o kernel, e o comportamento exato (recusar vs esperar até expirar) pode variar entre Windows/Linux e até entre configurações.

**Observação experimental (meu teste):** ao atacar o `servergargalo.py` com 10 clientes, o `clientenervoso.py` apresentou *timeouts* (nenhum cliente completou a leitura de resposta dentro do limite de 2s), indicando que o servidor não conseguiu aceitar/atender a carga no tempo do cliente devido ao gargalo e à fila pequena.

Já no servidor multithread ([src/server.py](src/server.py)), cada conexão aceita é imediatamente delegada para uma **thread**. Isso faz o loop principal voltar rapidamente ao `accept()` e “drenar” o backlog muito mais rápido. Na prática, isso reduz a chance da fila encher e faz com que as conexões sejam aceitas quase imediatamente, mesmo que cada atendimento individual ainda tenha latência (o `sleep(5)` do processamento).

---

## Questão 2 — Custo de Recursos: Threads vs. Event Loop

**Dado observado no `server.py`:** o log do servidor mostrou pico de **10 conexões simultâneas** (linha `[ATIVO] Conexões simultâneas: 10`). Como o código imprime `threading.active_count() - 1`, isso corresponde a **10 threads de trabalho** (uma por cliente) além da thread principal do processo.

### Multithread (1 thread por conexão)

- **Memória:** cada thread do SO tem custo de alocação e manutenção, principalmente devido à *stack* (tamanho depende do SO/configuração, mas não é desprezível). No experimento, para 10 conexões simultâneas, o processo precisou manter +/-10 threads adicionais ativas.
- **CPU:** o SO precisa escalonar várias threads e fazer mais **trocas de contexto** (*context switches*). Mesmo com boa parte do tempo em espera (I/O ou `sleep`), existe overhead do escalonador e do gerenciamento das threads.

### Assíncrono (Event Loop)

- **Memória:** o modelo assíncrono atende várias conexões com **uma única thread** e múltiplas corrotinas/tarefas, que são bem mais leves que threads do SO. Para o mesmo cenário de 10 conexões, a tendência é consumir menos memória por conexão.
- **CPU:** o controle de concorrência ocorre cooperativamente com `await` no Event Loop, reduzindo a necessidade de context switch entre várias threads do SO.

**Síntese baseada no experimento:** no `server.py`, para suportar 10 conexões simultâneas foi necessário escalar até 10 threads de atendimento (além da thread principal). No servidor assíncrono, a mesma quantidade de clientes pode ser atendida com 1 thread e várias corrotinas, reduzindo o overhead de threads e trocas de contexto.
