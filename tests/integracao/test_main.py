import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from ia_service import _limpar_formatacao_markdown

client = TestClient(app)

def test_limpar_formatacao_markdown():
    """Testa a função de utilidade para remover blocos de código Markdown"""
    texto_com_markdown = "```json\n{\"status\": \"Alerta\"}\n```"
    texto_limpo = _limpar_formatacao_markdown(texto_com_markdown)
    # Adicionamos .strip() aqui para ignorar a quebra de linha \n residual
    assert texto_limpo.strip() == "{\"status\": \"Alerta\"}"

    texto_sem_markdown = "{\"status\": \"Normal\"}"
    assert _limpar_formatacao_markdown(texto_sem_markdown) == "{\"status\": \"Normal\"}"

def test_analisar_cultivo_dados_invalidos():
    """Testa se a API rejeita requisições com dados incompletos"""
    payload = {
        "cultura": "Alface",
        "temperatura": 24.5
    }
    response = client.post("/analisar-cultivo", json=payload)
    assert response.status_code == 422 

# Injetamos uma API Key falsa apenas durante o teste para passar pela validação de segurança
@patch('ia_service.API_KEY', 'chave-falsa-para-teste')
@patch('ia_service.genai.Client')
def test_analisar_cultivo_sucesso(mock_client_class):
    """Testa a rota principal simulando uma resposta de sucesso do Google Gemini"""
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance
    
    mock_response = MagicMock()
    mock_response.text = '{"status_sistema": "Normal", "diagnostico_breve": "Tudo excelente."}'
    mock_client_instance.models.generate_content.return_value = mock_response

    payload = {
        "cultura": "Alface Crespa",
        "ph": 6.0,
        "temperatura": 22.0,
        "umidade": 65.0
    }

    response = client.post("/analisar-cultivo", json=payload)

    assert response.status_code == 200
    dados_resposta = response.json()
    assert dados_resposta["status_sistema"] == "Normal"
    assert dados_resposta["diagnostico_breve"] == "Tudo excelente."
    mock_client_instance.models.generate_content.assert_called_once()

@patch('ia_service.API_KEY', 'chave-falsa-para-teste')
@patch('ia_service.genai.Client')
def test_analisar_cultivo_resposta_ia_malformada(mock_client_class):
    """Testa o tratamento de erros caso o Gemini devolva texto que não é JSON válido"""
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance
    
    mock_response = MagicMock()
    mock_response.text = "Parece que a alface precisa de mais água."
    mock_client_instance.models.generate_content.return_value = mock_response

    payload = {
        "cultura": "Tomate",
        "ph": 7.5,
        "temperatura": 28.0,
        "umidade": 50.0
    }

    response = client.post("/analisar-cultivo", json=payload)

    assert response.status_code == 500
    assert "dados processáveis" in response.json()["detail"]