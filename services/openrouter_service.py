import json
import os

from datetime import datetime

from openai import OpenAI

from config import OPENROUTER_API_KEY


# ==================================================
# CONFIG
# ==================================================

qtd_questoes = 3

modelo_ia = ("deepseek/deepseek-v4-flash:free")

# outras opções:
# "deepseek/deepseek-v4-flash:free"
# "google/gemma-3-27b-it:free"
# "meta-llama/llama-3.3-70b-instruct:free"


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

    # ==================================================
    # PROMPT
    # ==================================================

    prompt = f"""
    Você é um especialista em concursos públicos.

    Gere {qtd_questoes} questões REALISTAS,
    similares às cobradas pela banca informada.

    Dados:

    - Instituição: {instituicao}
    - Banca: {banca}
    - Ano: {ano}
    - Disciplina: {disciplina}
    - Tipo: {tipo}

    IMPORTANTE:

    - Retorne SOMENTE JSON
    - Não use markdown
    - Não use ```json
    - Não escreva comentários
    - Não escreva explicações fora do JSON
    - Retorne UMA LISTA JSON
    - NÃO envolva em {{ "questoes": [] }}

    Estrutura esperada:

    [
      {{
        "tipo": "multipla_escolha",

        "enunciado":
            "texto da questão",

        "materia":
            "{disciplina}",

        "assunto":
            "assunto",

        "banca":
            "{banca}",

        "dificuldade": 3,

        "fonte":
            "{instituicao} {ano}",

        "resposta_correta":
            "A",

        "alternativas": [

          {{
            "letra": "A",

            "texto":
                "texto alternativa",

            "correta": true
          }},

          {{
            "letra": "B",

            "texto":
                "texto alternativa",

            "correta": false
          }}

        ],

        "explicacao_ia":
            "explicação detalhada"
      }}
    ]

    Regras:

    - JSON RFC8259 válido
    - dificuldade entre 1 e 5
    - alternativas completas
    - explicações detalhadas
    - escape caracteres especiais
    """

    # ==================================================
    # REQUEST
    # ==================================================

    try:

        response = (
            client.chat.completions.create(

                model=modelo_ia,

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
        )

    except Exception as e:

        raise Exception(
            f"Erro na requisição OpenRouter: {e}"
        )

    # ==================================================
    # TEXTO
    # ==================================================

    texto = None

    try:

        if response.choices:

            if response.choices[0].message:

                texto = (
                    response
                    .choices[0]
                    .message
                    .content
                )

    except Exception as e:

        raise Exception(
            f"Erro ao ler resposta IA: {e}"
        )

    # ==================================================
    # VALIDAÇÃO
    # ==================================================

    if not texto:

        print("\n====================")
        print("RESPOSTA VAZIA IA")
        print("====================")
        print(response)
        print("====================\n")

        raise Exception(
            "A IA retornou resposta vazia."
        )

    # ==================================================
    # DEBUG TERMINAL
    # ==================================================

    print("\n====================")
    print("RESPOSTA IA")
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
    # CRIAR PASTA OUTPUTS
    # ==================================================

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    # ==================================================
    # SALVAR PROMPT
    # ==================================================

    with open(
        f"outputs/prompt_{timestamp}.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(prompt)

    # ==================================================
    # SALVAR RESPONSE RAW
    # ==================================================

    with open(
        f"outputs/response_{timestamp}.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(str(texto))

    # ==================================================
    # CONVERTER JSON
    # ==================================================

    try:

        data = json.loads(texto)

        # =====================================
        # CASO:
        # { "questoes": [...] }
        # =====================================

        if isinstance(data, dict):

            if "questoes" in data:

                return data["questoes"]

        # =====================================
        # CASO:
        # LISTA NORMAL
        # =====================================

        return data

    except Exception as e:

        # =====================================
        # SALVAR ERRO JSON
        # =====================================

        with open(
            f"outputs/error_{timestamp}.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(str(texto))

        print("\n====================")
        print("ERRO JSON")
        print("====================")
        print(texto)
        print("====================\n")

        raise Exception(
            f"Erro ao converter JSON: {e}"
        )