import json
import os
import re

from datetime import datetime

from openai import OpenAI

from config import OPENROUTER_API_KEY


# ==================================================
# CONFIG
# ==================================================

qtd_questoes = 3

modelo_ia = (
    "deepseek/deepseek-v4-flash:free"
)

# outras opções:
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
# FUNÇÃO AUXILIAR
# ==================================================

def salvar_debug(
    nome_arquivo,
    conteudo
):

    try:

        os.makedirs(
            "outputs",
            exist_ok=True
        )

        with open(
            nome_arquivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(str(conteudo))

    except Exception as e:

        print(
            f"Erro ao salvar arquivo debug: {e}"
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
    # TIMESTAMP
    # ==================================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

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
    # SALVAR PROMPT
    # ==================================================

    salvar_debug(
        f"outputs/prompt_{timestamp}.txt",
        prompt
    )

    # ==================================================
    # REQUEST IA
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
    # EXTRAIR TEXTO
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

        salvar_debug(
            f"outputs/response_vazia_{timestamp}.txt",
            str(response)
        )

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
    # SALVAR RESPONSE RAW
    # ==================================================

    salvar_debug(
        f"outputs/response_raw_{timestamp}.txt",
        texto
    )

    # ==================================================
    # LIMPEZA
    # ==================================================

    texto = texto.strip()

    # remove markdown
    texto = texto.replace(
        "```json",
        ""
    )

    texto = texto.replace(
        "```",
        ""
    )

    texto = texto.strip()

    # ==================================================
    # REMOVER CONTROLES INVÁLIDOS
    # ==================================================

    texto_limpo = re.sub(
        r'[\x00-\x1F\x7F]',
        '',
        texto
    )

    # ==================================================
    # SALVAR TEXTO LIMPO
    # ==================================================

    salvar_debug(
        f"outputs/response_limpo_{timestamp}.txt",
        texto_limpo
    )

    # ==================================================
    # CONVERTER JSON
    # ==================================================

    try:

        data = json.loads(
            texto_limpo
        )

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

        salvar_debug(
            f"outputs/error_json_{timestamp}.txt",
            texto_limpo
        )

        print("\n====================")
        print("ERRO JSON")
        print("====================")
        print(texto_limpo)
        print("====================\n")

        raise Exception(
            f"Erro ao converter JSON: {e}"
        )