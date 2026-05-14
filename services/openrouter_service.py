import json

from openai import OpenAI

from config import OPENROUTER_API_KEY

qtd_questoes = "3"
modelo_deepseek = "deepseek/deepseek-v4-flash:free"


# ==================================================
# CLIENTE
# ==================================================

client = OpenAI(

    base_url=
        "https://openrouter.ai/api/v1",

    api_key=
        OPENROUTER_API_KEY
)


# ==================================================
# PESQUISAR QUESTÕES
# ==================================================

def pesquisar_questoes(
    instituicao,
    banca,
    ano,
    disciplina,
    tipo
):

    prompt = f"""
    Você é um especialista em concursos públicos.

    Gere """+qtd_questoes+""" questões REALISTAS,
    similares às cobradas
    pela banca informada.

    Retorne APENAS JSON válido.

    Estrutura:

    [
      {{
        "tipo": "multipla_escolha",

        "enunciado": "texto",

        "materia": "{disciplina}",

        "assunto": "assunto",

        "banca": "{banca}",

        "dificuldade": 3,

        "fonte":
            "{instituicao} {ano}",

        "resposta_correta": "A",

        "alternativas": [

          {{
            "letra": "A",
            "texto": "texto",
            "correta": true
          }}

        ],

        "explicacao_ia":
            "explicação detalhada"
      }}
    ]

    Regras:

    - retornar SOMENTE JSON
    - não usar markdown
    - não usar ```json
    - alternativas completas
    - explicações detalhadas
    - dificuldade de 1 a 5
    """

    response = client.chat.completions.create(

        model= modelo_deepseek,

        messages=[
            {
                "role": "system",

                "content":
                    "Você retorna apenas JSON válido."
            },

            {
                "role": "user",

                "content": prompt
            }
        ],

        temperature=0.3,

        response_format={
            "type": "json_object"
        }
    )

    texto = (
        response
        .choices[0]
        .message
        .content
    )

    # =====================================
    # LIMPEZA
    # =====================================

    texto = texto.replace(
        "```json",
        ""
    )

    texto = texto.replace(
        "```",
        ""
    )

    texto = texto.strip()

    # =====================================
    # CONVERTER JSON
    # =====================================

    try:

        return json.loads(texto)

    except Exception as e:

        print(texto)

        raise Exception(
            f"Erro ao converter JSON: {e}"
        )