"""Configuracao comum dos testes.

Marca cada teste com o tipo, pela pasta onde ele esta.

`pytest -m seguranca` roda so os de seguranca. No PyCharm, o mesmo filtro
vai em Run Configuration > Additional Arguments.
"""
import sys
from pathlib import Path

import pytest

# raiz do repositorio no caminho de import: `import main`, `import ia_service`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_TIPO_POR_PASTA = {
    "unitarios":  "unitario",
    "integracao": "integracao",
    "funcionais": "funcional",
    "aceitacao":  "aceitacao",
    "desempenho": "desempenho",
    "seguranca":  "seguranca",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        tipo = _TIPO_POR_PASTA.get(Path(str(item.fspath)).parent.name)
        if tipo:
            item.add_marker(getattr(pytest.mark, tipo))


# ── Duble do Gemini ─────────────────────────────────────────────
class GeminiFalso:
    """Faz o papel do google-genai: guarda o pedido e devolve um texto pronto."""

    def __init__(self, resposta='{"status_sistema": "Normal"}', erro=None):
        self.resposta, self.erro, self.pedidos = resposta, erro, []
        self.models = self

    def __call__(self, api_key, **opcoes):
        # **opcoes: o cliente real tambem recebe http_options (versao da API).
        self.api_key, self.opcoes = api_key, opcoes
        return self

    def generate_content(self, model, contents, config):
        self.pedidos.append({"model": model, "contents": contents, "config": config})
        if self.erro:
            raise self.erro
        return type("Resposta", (), {"text": self.resposta})()


@pytest.fixture()
def gemini(monkeypatch):
    """Gemini falso ja ligado, com uma chave de API de teste."""
    import ia_service
    falso = GeminiFalso()
    monkeypatch.setattr(ia_service, "API_KEY", "chave-de-teste")
    monkeypatch.setattr(ia_service.genai, "Client", falso)
    return falso


@pytest.fixture()
def cliente():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app)


LEITURA = {"cultura": "Alface Crespa", "ph": 6.0, "temperatura": 22.0, "umidade": 65.0}
