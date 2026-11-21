"""Testes de integracao: rota HTTP -> servico -> cliente do Gemini (duble)."""
from conftest import LEITURA


def test_rota_devolve_o_json_do_modelo(cliente, gemini):
    gemini.resposta = '{"status_sistema": "Normal", "sugestoes_acao": []}'
    r = cliente.post("/analisar-cultivo", json=LEITURA)
    assert r.status_code == 200 and r.json() == {"status_sistema": "Normal", "sugestoes_acao": []}
    assert "Alface Crespa" in gemini.pedidos[0]["contents"]


def test_sem_chave_na_azure_responde_500_com_aviso(cliente, monkeypatch):
    import ia_service
    monkeypatch.setattr(ia_service, "API_KEY", "")
    r = cliente.post("/analisar-cultivo", json=LEITURA)
    assert r.status_code == 500


def test_gemini_fora_do_ar_responde_500(cliente, gemini):
    gemini.erro = ConnectionError("503 UNAVAILABLE")
    assert cliente.post("/analisar-cultivo", json=LEITURA).status_code == 500


def test_cors_libera_o_app_web(cliente):
    r = cliente.options("/analisar-cultivo", headers={
        "Origin": "https://app.aerotower.com.br", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] in ("*", "https://app.aerotower.com.br")
