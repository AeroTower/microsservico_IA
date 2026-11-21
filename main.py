import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import LeituraSensores
from ia_service import analisar_dados_cultivo

logger = logging.getLogger("ia")

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
    except Exception:
        # O detalhe vai so para o log (Azure > Log stream). A mensagem do erro
        # pode trazer URL, chave ou dados internos, e nao deve chegar ao app.
        logger.exception("Falha ao processar análise")
        raise HTTPException(
            status_code=500,
            detail="Falha interna ao processar a análise. Tente de novo em instantes.",
        )