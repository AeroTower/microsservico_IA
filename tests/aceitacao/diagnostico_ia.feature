# language: pt
Funcionalidade: Diagnóstico do cultivo pela IA (HydroBot)
  Como cultivador com uma torre AeroTower
  Quero pedir ao HydroBot um diagnóstico da planta que escolhi
  Para saber se o cultivo está bem e o que corrigir

  Cenário: Leituras boas para a cultura
    Dado que eu cultivo "Alface Crespa"
    E a IA considera as leituras dentro da faixa ideal
    Quando eu peço o diagnóstico com pH 6.0, água a 22 graus e umidade 65
    Então o status do sistema é "Normal"
    E não recebo nenhuma sugestão de ação

  Cenário: Leitura fora da faixa
    Dado que eu cultivo "Manjericão"
    E a IA aponta o pH fora da faixa ideal
    Quando eu peço o diagnóstico com pH 8.1, água a 22 graus e umidade 60
    Então o status do sistema é "Alerta"
    E o parâmetro "ph" aparece em alerta
    E recebo pelo menos uma sugestão de ação

  Cenário: IA responde fora do formato combinado
    Dado que eu cultivo "Tomate"
    E a IA responde com texto solto em vez de JSON
    Quando eu peço o diagnóstico com pH 6.5, água a 24 graus e umidade 55
    Então recebo um aviso de que a IA não retornou dados processáveis
