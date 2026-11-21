import json
from google import genai
from google.genai import types
from config import API_KEY
from models import LeituraSensores

MODELO_GEMINI = "gemini-2.5-flash"


def _gerar_prompt_agronomico(dados: LeituraSensores) -> str:
    return f"""
    Você é um agrônomo especialista em hidroponia.

    A cultura atual no sistema é: {dados.cultura}

    Leituras atuais dos sensores:
    - pH da água: {dados.ph}
    - Temperatura da água: {dados.temperatura}°C
    - Umidade do ar: {dados.umidade}%

    Sua tarefa:
    1. Busque no seu próprio conhecimento quais são as faixas ideais de pH, temperatura e umidade para a cultura acima.
    2. Compare as leituras atuais com essas faixas ideais.
    3. Se todos os valores estiverem dentro da faixa, o status é "Normal".
    4. Se algum valor estiver fora da faixa, o status é "Alerta". Sugira ações corretivas práticas.

    FORMATO DE SAÍDA OBRIGATÓRIO:
    {{
      "parametros_ideais_utilizados": {{"ph": "faixa", "temperatura": "faixa", "umidade": "faixa"}},
      "status_sistema": "Normal ou Alerta",
      "diagnostico_breve": "Resumo rápido",
      "parametros_em_alerta": ["lista de parametros alterados, vazio se Normal"],
      "sugestoes_acao": ["lista de sugestões, vazio se Normal"]
    }}
    """


def _limpar_formatacao_markdown(texto: str) -> str:
    texto_sem_espacos = texto.strip()
    if texto_sem_espacos.startswith("```"):
        texto_sem_espacos = texto_sem_espacos.strip("`").replace("json\n", "", 1).strip()
    return texto_sem_espacos


def _consultar_modelo_gemini(prompt: str) -> str:
    cliente_ia = genai.Client(api_key=API_KEY)
    resposta = cliente_ia.models.generate_content(
        model=MODELO_GEMINI,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return resposta.text


def _converter_resposta_json(resposta_bruta: str) -> dict:
    texto_limpo = _limpar_formatacao_markdown(resposta_bruta)
    return json.loads(texto_limpo)


def analisar_dados_cultivo(dados: LeituraSensores) -> dict:
    # Checagem de segurança tardia: Se a Azure falhou em ler a chave, a API avisa em vez de quebrar
    if not API_KEY:
        raise ValueError("A chave GEMINI_API_KEY não está configurada no ambiente da Azure.")

    prompt = _gerar_prompt_agronomico(dados)
    resposta_bruta = _consultar_modelo_gemini(prompt)
    return _converter_resposta_json(resposta_bruta)
