"""Testes de aceitacao (BDD) da historia do diagnostico pela IA."""
import json

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("diagnostico_ia.feature")


@given(parsers.parse('que eu cultivo "{cultura}"'), target_fixture="cenario")
def eu_cultivo(cultura, cliente, gemini):
    return {"cultura": cultura, "cliente": cliente, "gemini": gemini}


@given("a IA considera as leituras dentro da faixa ideal")
def ia_normal(cenario):
    cenario["gemini"].resposta = json.dumps({"status_sistema": "Normal", "diagnostico_breve": "Ok",
                                            "parametros_em_alerta": [], "sugestoes_acao": []})


@given("a IA aponta o pH fora da faixa ideal")
def ia_alerta(cenario):
    cenario["gemini"].resposta = json.dumps({
        "status_sistema": "Alerta", "diagnostico_breve": "pH alto",
        "parametros_em_alerta": ["ph"], "sugestoes_acao": ["Corrija o pH com redutor."]})


@given("a IA responde com texto solto em vez de JSON")
def ia_texto_solto(cenario):
    cenario["gemini"].resposta = "Seu tomate parece ótimo, continue assim!"


@when(parsers.parse("eu peço o diagnóstico com pH {ph:g}, água a {temp:g} graus e umidade {umidade:g}"))
def peco_diagnostico(cenario, ph, temp, umidade):
    cenario["resposta"] = cenario["cliente"].post("/analisar-cultivo", json={
        "cultura": cenario["cultura"], "ph": ph, "temperatura": temp, "umidade": umidade})


@then(parsers.parse('o status do sistema é "{status}"'))
def status_e(cenario, status):
    assert cenario["resposta"].status_code == 200
    assert cenario["resposta"].json()["status_sistema"] == status
    assert cenario["cultura"] in cenario["gemini"].pedidos[-1]["contents"]


@then("não recebo nenhuma sugestão de ação")
def sem_sugestao(cenario):
    assert cenario["resposta"].json()["sugestoes_acao"] == []


@then(parsers.parse('o parâmetro "{parametro}" aparece em alerta'))
def parametro_em_alerta(cenario, parametro):
    assert parametro in cenario["resposta"].json()["parametros_em_alerta"]


@then("recebo pelo menos uma sugestão de ação")
def com_sugestao(cenario):
    assert len(cenario["resposta"].json()["sugestoes_acao"]) >= 1


@then("recebo um aviso de que a IA não retornou dados processáveis")
def aviso(cenario):
    assert cenario["resposta"].status_code == 500
    assert "dados processáveis" in cenario["resposta"].json()["detail"]
