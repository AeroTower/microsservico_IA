import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import LeituraSensores
from ia_service import analisar_dados_cultivo

app = FastAPI(title="Microserviço IA - Hidroponia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O "*" libera o acesso para qualquer site/localhost
    allow_credentials=True,
    allow_methods=["*"],  # Libera POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)


@app.post("/analisar-cultivo")
async def analisar_cultivo(dados: LeituraSensores):
    try:
        return analisar_dados_cultivo(dados)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="O serviço de inteligência artificial não retornou dados processáveis.",
        )
    except Exception as erro_inesperado:
        raise HTTPException(
            status_code=500,
            detail=f"Falha interna ao processar análise: {str(erro_inesperado)}",
        )