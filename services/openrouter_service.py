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

modelos_ia = [

    "google/gemma-4-31b-it:free",

    "deepseek/deepseek-v4-flash:free",

    "meta-llama/llama-3.3-70b-instruct:free"
]


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
# LIMPAR TEXTO
# ==================================================

def limpar_texto(texto):

    texto = texto.strip()

    texto = texto.replace(
        "```json",
        ""
    )

    texto = texto.replace(
        "```",
        ""
    )

    texto = texto.strip()

    # remove caracteres inválidos
    texto = re.sub(
        r'[\x00-\x1F\x7F]',
        '',
        texto
    )

    # remove reticências quebradas
    texto = texto.replace(
        "…",
        "..."
    )

    return texto


# ==================================================
# PESQUISAR QUESTÕES
# ==================================================

def pesquisar_questoes(
    instituicao,
    banca,
    cargo,
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
    completas e bem escritas.

    NÃO abrevie palavras.
    NÃO use "..." dentro do texto.
    NÃO corte frases.
    NÃO use placeholders.
    NÃO resuma alternativas.

    Dados:

    - Instituição: {instituicao}
    - Banca: {banca}
    - Cargo: {cargo}
    - Ano: {ano}
    - Disciplina: {disciplina}
    - Tipo: {tipo}

    IMPORTANTE:

    - Retorne SOMENTE JSON
    - Não use markdown
    - Não use ```json
    - Não escreva comentários
    - Retorne UMA LISTA JSON
    - NÃO envolva em {{ "questoes": [] }}

    Estrutura esperada:

    [
      {{
        "tipo": "multipla_escolha",

        "enunciado":
            "texto completo da questão",

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
                "texto completo alternativa",

            "correta": true
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
    # MENSAGENS
    # ==================================================

    messages = [

        {
            "role": "system",

            "content":
                "Você responde apenas JSON válido."
        },

        {
            "role": "user",

            "content": prompt
        }
    ]

    # ==================================================
    # FALLBACK MODELOS
    # ==================================================

    ultimo_erro = None

    response = None

    modelo_usado = None

    for modelo in modelos_ia:

        try:

            print(
                f"\nTentando modelo: {modelo}"
            )

            response = (
                client.chat.completions.create(

                    model=modelo,

                    messages=messages,

                    temperature=0.2
                )
            )

            modelo_usado = modelo

            print(
                f"Modelo funcionando: {modelo}"
            )

            break

        except Exception as e:

            ultimo_erro = e

            print(
                f"Erro no modelo {modelo}: {e}"
            )

            salvar_debug(
                f"outputs/erro_modelo_{timestamp}.txt",
                f"Modelo: {modelo}\n\nErro:\n{e}"
            )

    # ==================================================
    # NENHUM FUNCIONOU
    # ==================================================

    if not response:

        raise Exception(
            f"Nenhum modelo funcionou.\n\n"
            f"Último erro:\n{ultimo_erro}"
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
    # RESPOSTA VAZIA
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
    print("MODELO USADO")
    print("====================")
    print(modelo_usado)

    print("\n====================")
    print("RESPOSTA IA")
    print("====================")
    print(texto)
    print("====================\n")

    # ==================================================
    # SALVAR RAW
    # ==================================================

    salvar_debug(
        f"outputs/response_raw_{timestamp}.txt",
        texto
    )

    # ==================================================
    # LIMPAR TEXTO
    # ==================================================

    texto_limpo = limpar_texto(texto)

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

        # ==========================================
        # CASO:
        # { "questoes": [...] }
        # ==========================================

        if isinstance(data, dict):

            if "questoes" in data:

                return data["questoes"]

        # ==========================================
        # CASO:
        # LISTA
        # ==========================================

        return data

    except Exception as e:

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