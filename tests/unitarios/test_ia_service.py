"""Testes unitarios do servico de IA (o Gemini e trocado por um duble)."""
import json

import pytest

import ia_service
from models import LeituraSensores


def _leitura(**mudancas):
    return LeituraSensores(**{"cultura": "Alface Crespa", "ph": 6.0, "temperatura": 22.0,
                              "umidade": 65.0, **mudancas})


def test_prompt_leva_a_cultura_e_as_tres_leituras():
    prompt = ia_service._gerar_prompt_agronomico(_leitura(ph=7.8, temperatura=29.5, umidade=40))
    assert "Alface Crespa" in prompt
    assert "pH da água: 7.8" in prompt and "29.5°C" in prompt and "40.0%" in prompt
    assert '"status_sistema"' in prompt        # pede o formato JSON combinado


@pytest.mark.parametrize("bruto, esperado", [
    ('{"a": 1}', '{"a": 1}'),
    ('  {"a": 1}\n', '{"a": 1}'),
    ('```json\n{"a": 1}\n```', '{"a": 1}'),
    ('```\n{"a": 1}\n```', '{"a": 1}'),
])
def test_limpa_a_moldura_de_markdown(bruto, esperado):
    assert json.loads(ia_service._limpar_formatacao_markdown(bruto)) == json.loads(esperado)


def test_resposta_que_nao_e_json_gera_erro_de_json():
    with pytest.raises(json.JSONDecodeError):
        ia_service._converter_resposta_json("A alface está ótima!")


def test_sem_chave_configurada_avisa_antes_de_chamar_o_gemini(monkeypatch):
    monkeypatch.setattr(ia_service, "API_KEY", None)
    monkeypatch.setattr(ia_service.genai, "Client", lambda **k: pytest.fail("não devia chamar"))
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        ia_service.analisar_dados_cultivo(_leitura())


def test_pede_json_ao_modelo_certo(gemini):
    gemini.resposta = '```json\n{"status_sistema": "Alerta"}\n```'
    assert ia_service.analisar_dados_cultivo(_leitura()) == {"status_sistema": "Alerta"}
    pedido = gemini.pedidos[0]
    assert gemini.api_key == "chave-de-teste"
    assert pedido["model"] == "gemini-2.5-flash"
    assert pedido["config"].response_mime_type == "application/json"


@pytest.mark.parametrize("campo", ["cultura", "ph", "temperatura", "umidade"])
def test_leitura_sem_um_campo_e_invalida(campo):
    dados = {"cultura": "Alface", "ph": 6.0, "temperatura": 22.0, "umidade": 65.0}
    dados.pop(campo)
    with pytest.raises(ValueError):
        LeituraSensores(**dados)
