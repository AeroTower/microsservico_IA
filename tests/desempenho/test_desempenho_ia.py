"""Testes de desempenho do microsservico de IA (Gemini trocado por duble).

Medem o custo do proprio servico (validacao, prompt, JSON), sem a latencia
do Gemini. Limites folgados para nao falhar por oscilacao da maquina.
"""
import time

from conftest import LEITURA


def test_carga_de_500_diagnosticos(cliente, gemini):
    inicio = time.perf_counter()
    respostas = [cliente.post("/analisar-cultivo", json={**LEITURA, "ph": 5 + i % 30 / 10})
                 for i in range(500)]
    duracao = time.perf_counter() - inicio
    assert {r.status_code for r in respostas} == {200}
    assert len(gemini.pedidos) == 500
    assert duracao < 20, f"500 diagnósticos levaram {duracao:.2f}s"


def test_resposta_grande_do_modelo(cliente, gemini):
    """Volume: o modelo devolve 1.000 sugestoes; o servico repassa sem travar."""
    import json
    gemini.resposta = json.dumps({"status_sistema": "Alerta",
                                  "sugestoes_acao": [f"sugestão {i}" for i in range(1_000)]})
    inicio = time.perf_counter()
    r = cliente.post("/analisar-cultivo", json=LEITURA)
    assert r.status_code == 200 and len(r.json()["sugestoes_acao"]) == 1_000
    assert time.perf_counter() - inicio < 2
