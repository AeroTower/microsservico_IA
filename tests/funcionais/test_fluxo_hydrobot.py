"""Teste funcional: o que o HydroBot do app faz, do pedido a resposta exibida."""
from conftest import LEITURA


def test_cultivo_fora_da_faixa_recebe_alerta_e_sugestoes(cliente, gemini):
    """O app manda a planta escolhida e as leituras do painel; mostra o diagnostico."""
    gemini.resposta = """```json
    {"parametros_ideais_utilizados": {"ph": "5.5-6.5", "temperatura": "18-24", "umidade": "50-70"},
     "status_sistema": "Alerta",
     "diagnostico_breve": "pH alto para alface.",
     "parametros_em_alerta": ["ph"],
     "sugestoes_acao": ["Adicione redutor de pH aos poucos."]}
    ```"""
    r = cliente.post("/analisar-cultivo", json={**LEITURA, "ph": 7.6})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["status_sistema"] == "Alerta" and corpo["parametros_em_alerta"] == ["ph"]
    assert corpo["sugestoes_acao"] and set(corpo["parametros_ideais_utilizados"]) == {"ph", "temperatura", "umidade"}
    assert "pH da água: 7.6" in gemini.pedidos[0]["contents"]


def test_cultivo_saudavel_nao_traz_sugestoes(cliente, gemini):
    gemini.resposta = ('{"status_sistema": "Normal", "diagnostico_breve": "Tudo certo.", '
                       '"parametros_em_alerta": [], "sugestoes_acao": []}')
    corpo = cliente.post("/analisar-cultivo", json=LEITURA).json()
    assert corpo["status_sistema"] == "Normal" and corpo["sugestoes_acao"] == []


def test_app_sem_leitura_de_ph_recebe_422(cliente, gemini):
    sem_ph = {k: v for k, v in LEITURA.items() if k != "ph"}
    r = cliente.post("/analisar-cultivo", json=sem_ph)
    assert r.status_code == 422 and gemini.pedidos == []
