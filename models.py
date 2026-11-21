from pydantic import BaseModel, Field

class LeituraSensores(BaseModel):
    # Limite de tamanho: o texto vai inteiro para o prompt, e um nome enorme
    # gastaria cota do Gemini (e abriria espaco para prompt injection).
    cultura: str = Field(..., min_length=1, max_length=100,
                         description="Nome da planta cultivada, ex: Alface Crespa")
    ph: float = Field(..., description="Nível de pH da água")
    temperatura: float = Field(..., description="Temperatura da água em graus Celsius")
    umidade: float = Field(..., description="Umidade relativa do ar em porcentagem")