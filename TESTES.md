# Testes do microsserviço de IA

**Responsável pelos casos formais:** Rafael · **Cobertura:** 100% (meta da disciplina: 90%) · **37 testes**

O Gemini é substituído por um dublê de teste (`GeminiFalso`, em `tests/conftest.py`). Os testes não precisam de chave, não gastam cota e dão sempre o mesmo resultado.

| Tipo | Pasta | Testes | O que confere |
|---|---|---:|---|
| Unitário | `tests/unitarios/` | 12 | montagem do prompt, limpeza do Markdown, conversão do JSON, chave ausente, modelo e formato pedidos |
| Integração | `tests/integracao/` | 8 | rota → serviço → cliente do Gemini; CORS para o app web (inclui o `test_main.py` original) |
| Funcional | `tests/funcionais/` | 3 | o fluxo do HydroBot no app: pedido com a planta e as leituras, diagnóstico de volta |
| Aceitação | `tests/aceitacao/` | 3 | história "diagnóstico do cultivo pela IA", em BDD (`diagnostico_ia.feature`) |
| Desempenho | `tests/desempenho/` | 2 | 500 diagnósticos seguidos; resposta com 1.000 sugestões |
| Segurança | `tests/seguranca/` | 9 | vazamento de erro interno, abuso de cota, prompt injection, entradas que não são número |

## Defeitos encontrados pelos testes (e corrigidos)

| # | Defeito | Teste que achou | Risco | Correção |
|---|---|---|---|---|
| 1 | O texto do erro interno (com URL do Gemini e detalhes) ia na resposta para o app | `test_erro_interno_nao_vaza_detalhes_nem_a_chave` | Médio: expõe a infraestrutura | Mensagem genérica para o app; o detalhe vai para o log da Azure |
| 2 | `cultura` aceitava texto de qualquer tamanho, inclusive vazio | `test_cultura_gigante_e_recusada_antes_de_gastar_cota` | Médio: prompt gigante gasta a cota do Gemini | Campo limitado a 1–100 caracteres (422 antes de chamar a IA) |

## Como rodar

**Terminal**
```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov                     # tudo, com cobertura (falha abaixo de 90%)
pytest -m seguranca              # só um tipo: unitario, integracao, funcional, aceitacao, desempenho, seguranca
pytest --cov --cov-report=html   # relatório navegável em htmlcov/index.html
```

**PyCharm**: *Settings › Tools › Python Integrated Tools › Testing › Default test runner* = **pytest**. Depois, botão direito na pasta `tests` › **Run 'pytest in tests'** (ou **Run with Coverage**). Para rodar só um tipo, use *Edit Configurations › Additional Arguments*: `-m aceitacao`.

**GitHub**: o workflow `.github/workflows/testes.yml` roda em todo pull request, com Python 3.14 (o mesmo da Azure). A aba *Actions* mostra a tabela por tipo, e *Artifacts › evidencias-testes-ia* traz o relatório de cobertura em HTML.

## Casos de teste formais (1 de cada tipo)

Plataforma de todos: Python 3.14, pytest 9, Ubuntu (GitHub Actions) e Windows (PyCharm).

### IA-UNI-01 · Unitário · Resposta do modelo com moldura de Markdown
| Campo | Valor |
|---|---|
| Cenário | O Gemini devolve o JSON dentro de um bloco ```` ```json ```` |
| Pré-requisitos | Nenhum (função isolada) |
| Passos | Chamar `_limpar_formatacao_markdown(texto)` e converter com `json.loads` |
| Dados | `{"a": 1}` puro, com espaços, com ```` ```json ```` e com ```` ``` ```` (4 execuções) |
| Esperado | Sempre o objeto `{"a": 1}` |
| Obtido | 4 de 4 corretos |
| Status | ✅ Sucesso |
| Teste | `tests/unitarios/test_ia_service.py::test_limpa_a_moldura_de_markdown` |

### IA-INT-01 · Integração · Rota repassa o JSON do modelo
| Campo | Valor |
|---|---|
| Cenário | O app chama `POST /analisar-cultivo` e o serviço consulta o modelo |
| Pré-requisitos | Gemini substituído por dublê; `GEMINI_API_KEY` de teste |
| Passos | 1. Configurar a resposta do dublê. 2. `POST /analisar-cultivo` com a leitura |
| Dados | Alface Crespa, pH 6,0, água 22 °C, umidade 65% |
| Esperado | 200 com o JSON do modelo; o prompt enviado contém a cultura |
| Obtido | Conforme esperado |
| Status | ✅ Sucesso |
| Teste | `tests/integracao/test_rota_analisar.py::test_rota_devolve_o_json_do_modelo` |

### IA-FUN-01 · Funcional · HydroBot com pH fora da faixa
| Campo | Valor |
|---|---|
| Cenário | No app, o usuário escolhe a planta e pede o diagnóstico com o pH alto |
| Pré-requisitos | Gemini substituído por dublê que devolve um alerta |
| Passos | `POST /analisar-cultivo` como o `chat_bot.dart` envia |
| Dados | Alface Crespa, pH 7,6 |
| Esperado | Status "Alerta", `ph` em alerta, sugestões e faixas ideais na resposta |
| Obtido | Conforme esperado |
| Status | ✅ Sucesso |
| Teste | `tests/funcionais/test_fluxo_hydrobot.py::test_cultivo_fora_da_faixa_recebe_alerta_e_sugestoes` |

### IA-ACE-01 · Aceitação (BDD) · Leitura fora da faixa
| Campo | Valor |
|---|---|
| Cenário | *Dado* que eu cultivo "Manjericão" e a IA aponta o pH fora da faixa; *quando* peço o diagnóstico com pH 8,1; *então* o status é "Alerta", o `ph` aparece em alerta e recebo uma sugestão |
| Pré-requisitos | História de usuário "Diagnóstico do cultivo pela IA (HydroBot)" |
| Passos | Executados pelos passos em português de `diagnostico_ia.feature` |
| Dados | pH 8,1 · água 22 °C · umidade 60% |
| Esperado | Os três critérios de aceite |
| Obtido | Conforme esperado (os outros 2 cenários também passaram) |
| Status | ✅ Sucesso |
| Teste | `tests/aceitacao/diagnostico_ia.feature` |

### IA-DES-01 · Desempenho (carga) · 500 diagnósticos seguidos
| Campo | Valor |
|---|---|
| Cenário | Muitos usuários pedindo diagnóstico ao mesmo tempo |
| Pré-requisitos | Gemini substituído por dublê (mede só o custo do serviço) |
| Passos | 500 `POST /analisar-cultivo` com pH variando |
| Dados | pH de 5,0 a 7,9 |
| Esperado | 500 respostas 200 em menos de 20 s (limite folgado) |
| Obtido | 500 de 500 em 1,5 s |
| Status | ✅ Sucesso |
| Teste | `tests/desempenho/test_desempenho_ia.py::test_carga_de_500_diagnosticos` |

### IA-SEG-01 · Segurança · Erro interno não vaza para o app
| Campo | Valor |
|---|---|
| Cenário | O Gemini falha com uma mensagem que traz a URL do serviço e a chave |
| Pré-requisitos | Dublê configurado para lançar o erro |
| Passos | `POST /analisar-cultivo` com uma leitura válida |
| Dados | Erro `"400 API key not valid: chave-de-teste em https://generativelanguage..."` |
| Esperado | 500 com mensagem genérica, sem a chave e sem a URL |
| Obtido | **1ª execução: falhou** (a mensagem ia inteira para o app). Depois da correção em `main.py`: conforme esperado |
| Status | ✅ Sucesso (após correção) |
| Teste | `tests/seguranca/test_seguranca_ia.py::test_erro_interno_nao_vaza_detalhes_nem_a_chave` |
