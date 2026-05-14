import json
import google.generativeai as genai

from config import GEMINI_API_KEY


# ==================================================
# CONFIG GEMINI
# ==================================================

genai.configure(
    api_key=GEMINI_API_KEY
)



model = genai.GenerativeModel(
    "gemini-1.5-flash"
)


# ==================================================
# GERAR QUESTÕES
# ==================================================


def pesquisar_questoes(
    instituicao,
    banca,
    ano,
    disciplina,
    tipo
):

    prompt = f"""
    Você é um sistema especialista em concursos públicos.

    Gere questões REAIS ou extremamente próximas
    do estilo da prova solicitada.

    Retorne APENAS JSON.

    Estrutura:

    [
      {{
        "tipo": "multipla_escolha",
        "enunciado": "texto",
        "materia": "Português",
        "assunto": "Crase",
        "banca": "FGV",
        "dificuldade": 3,
        "fonte": "SEFAZ BA 2022",
        "resposta_correta": "A",
        "alternativas": [
          {{
            "letra": "A",
            "texto": "texto",
            "correta": true
          }}
        ],
        "explicacao_ia": "explicação detalhada"
      }}
    ]

    Regras:

    - gerar 10 questões
    - dificuldade entre 1 e 5
    - alternativas completas
    - explicação detalhada
    - retornar apenas JSON válido

    Dados:

    Instituição: {instituicao}
    Banca: {banca}
    Ano: {ano}
    Disciplina: {disciplina}
    Tipo: {tipo}
    """

    response = model.generate_content(
        prompt
    )

    texto = response.text

    texto = texto.replace(
        "```json",
        ""
    )

    texto = texto.replace(
        "```",
        ""
    )

    return json.loads(texto)