import json

from openai import OpenAI

from config import OPENROUTER_API_KEY


# ==================================================
# CONFIG
# ==================================================

qtd_questoes = 3

modelo_deepseek = (
    "google/gemma-4-26b-a4b-it:free"
)


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

    Gere {qtd_questoes} questões REALISTAS,
    similares às cobradas pela banca informada.

    IMPORTANTE:

    - Retorne APENAS JSON
    - Não use markdown
    - Não use ```json
    - Não escreva textos fora do JSON
    - Retorne UMA LISTA JSON
    - NÃO envolva em {{ "questoes": [] }}

    Estrutura esperada:

    [
      {{
        "tipo": "multipla_escolha",

        "enunciado": "texto da questão",

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
            "texto": "texto alternativa",
            "correta": true
          }},

          {{
            "letra": "B",
            "texto": "texto alternativa",
            "correta": false
          }}

        ],

        "explicacao_ia":
            "explicação detalhada"
      }}
    ]

    Regras:

    - dificuldade entre 1 e 5
    - alternativas completas
    - explicações detalhadas
    - JSON RFC8259 válido
    - escape caracteres especiais
    """

    # ==================================================
    # REQUEST
    # ==================================================

    response = client.chat.completions.create(

        model=modelo_deepseek,

        messages=[

            {
                "role": "system",

                "content":
                    "Você responde apenas JSON válido."
            },

            {
                "role": "user",

                "content": prompt
            }
        ],

        temperature=0.2
    )

    # ==================================================
    # TEXTO
    # ==================================================

    texto = (
        response
        .choices[0]
        .message
        .content
    )

    # ==================================================
    # DEBUG
    # ==================================================

    print("\n====================")
    print("RESPOSTA IA:")
    print("====================")
    print(texto)
    print("====================\n")

    # ==================================================
    # LIMPEZA
    # ==================================================

    texto = texto.strip()

    if texto.startswith("```json"):

        texto = texto.replace(
            "```json",
            ""
        )

    if texto.startswith("```"):

        texto = texto.replace(
            "```",
            ""
        )

    if texto.endswith("```"):

        texto = texto[:-3]

    texto = texto.strip()

    # ==================================================
    # CONVERTER JSON
    # ==================================================

    try:

        data = json.loads(texto)

        # =====================================
        # CASO VENHA:
        # { "questoes": [...] }
        # =====================================

        if isinstance(data, dict):

            if "questoes" in data:

                return data["questoes"]

        # =====================================
        # CASO JÁ VENHA LISTA
        # =====================================

        return data

    except Exception as e:

        print("\n====================")
        print("ERRO JSON")
        print("====================")
        print(texto)
        print("====================\n")

        raise Exception(
            f"Erro ao converter JSON: {e}"
        )