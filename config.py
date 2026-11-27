import os
from dotenv import load_dotenv

load_dotenv()

# Carrega a chave, mas se não achar, não derruba o servidor na inicialização
API_KEY = os.getenv("GEMINI_API_KEY")
