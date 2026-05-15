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

    "deepseek/deepseek-v4-flash:free",

    "meta-llama/llama-3.3-70b-instruct:free",

    "google/gemma-4-31b-it:free"
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
# SALVAR DEBUG
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
            f"Erro ao salvar debug: {e}"
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

    # remove reticências unicode
    texto = texto.replace(
        "…",
        "..."
    )

    return texto


# ==================================================
# VALIDAR QUESTÕES
# ==================================================

def validar_questoes(data):

    questoes_validas = []

    for q in data:

        enunciado = q.get(
            "enunciado",
            ""
        )

        explicacao = q.get(
            "explicacao_ia",
            ""
        )

        alternativas = q.get(
            "alternativas",
            []
        )

        # ======================================
        # ENUNCIADO
        # ======================================

        if len(enunciado) < 80:

            continue

        # ======================================
        # EXPLICAÇÃO
        # ======================================

        if len(explicacao) < 50:

            continue

        # ======================================
        # MÚLTIPLA ESCOLHA
        # ======================================

        if q.get("tipo") == "multipla_escolha":

            if len(alternativas) < 5:

                continue

            valido = True

            for alt in alternativas:

                texto_alt = alt.get(
                    "texto",
                    ""
                )

                if len(texto_alt) < 30:

                    valido = False

                    break

            if not valido:

                continue

        questoes_validas.append(q)

    return questoes_validas


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
    Você é um especialista em concursos públicos brasileiros.

    Sua tarefa é gerar questões COMPLETAS,
    REALISTAS e DETALHADAS.

    IMPORTANTE:

    NÃO abrevie palavras.
    NÃO use letras isoladas.
    NÃO use placeholders.
    NÃO use "...".
    NÃO resuma frases.
    NÃO corte alternativas.

    TODAS as alternativas devem possuir
    frases completas e longas.

    Cada questão deve possuir:

    - enunciado com no mínimo 200 caracteres
    - alternativas com no mínimo 80 caracteres
    - explicação com no mínimo 300 caracteres

    Dados da prova:

    - Instituição: {instituicao}
    - Banca: {banca}
    - Cargo: {cargo}
    - Ano: {ano}
    - Disciplina: {disciplina}
    - Tipo: {tipo}

    Retorne APENAS JSON válido.

    Formato obrigatório:

    [
      {{
        "tipo": "{tipo}",

        "enunciado":
          "texto completo",

        "materia":
          "{disciplina}",

        "assunto":
          "assunto detalhado",

        "banca":
          "{banca}",

        "cargo":
          "{cargo}",

        "dificuldade": 3,

        "fonte":
          "{instituicao} {ano}",

        "resposta_correta":
          "A",

        "alternativas": [

          {{
            "letra": "A",

            "texto":
              "alternativa completa",

            "correta": true
          }},

          {{
            "letra": "B",

            "texto":
              "alternativa completa",

            "correta": false
          }},

          {{
            "letra": "C",

            "texto":
              "alternativa completa",

            "correta": false
          }},

          {{
            "letra": "D",

            "texto":
              "alternativa completa",

            "correta": false
          }},

          {{
            "letra": "E",

            "texto":
              "alternativa completa",

            "correta": false
          }}
        ],

        "explicacao_ia":
          "explicação detalhada"
      }}
    ]

    REGRAS IMPORTANTES:

    - Retorne SOMENTE JSON
    - Não use markdown
    - Não use ```json
    - Não escreva comentários
    - Não invente campos
    - Não use texto curto
    - Não use respostas vazias
    - Não use apenas letras
    - Não use placeholders
    - Não use abreviações
    - Gere conteúdo extenso e completo
    """

    # ==================================================
    # SALVAR PROMPT
    # ==================================================

    salvar_debug(
        f"outputs/prompt_{timestamp}.txt",
        prompt
    )

    # ==================================================
    # MESSAGES
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
    # FALLBACK
    # ==================================================

    response = None

    ultimo_erro = None

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
                f"Erro modelo {modelo}: {e}"
            )

            salvar_debug(
                f"outputs/erro_modelo_{timestamp}.txt",
                f"Modelo: {modelo}\n\nErro:\n{e}"
            )

    # ==================================================
    # NENHUM MODELO
    # ==================================================

    if not response:

        raise Exception(
            f"Nenhum modelo funcionou.\n\n"
            f"{ultimo_erro}"
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
    # DEBUG
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

    texto_limpo = limpar_texto(
        texto
    )

    salvar_debug(
        f"outputs/response_limpo_{timestamp}.txt",
        texto_limpo
    )

    # ==================================================
    # JSON
    # ==================================================

    try:

        data = json.loads(
            texto_limpo
        )

    except Exception as e:

        salvar_debug(
            f"outputs/error_json_{timestamp}.txt",
            texto_limpo
        )

        raise Exception(
            f"Erro ao converter JSON: {e}"
        )

    # ==================================================
    # CASO:
    # { "questoes": [...] }
    # ==================================================

    if isinstance(data, dict):

        if "questoes" in data:

            data = data["questoes"]

    # ==================================================
    # VALIDAR QUESTÕES
    # ==================================================

    questoes_validas = validar_questoes(
        data
    )

    # ==================================================
    # SEM QUESTÕES VÁLIDAS
    # ==================================================

    if not questoes_validas:

        salvar_debug(
            f"outputs/questoes_invalidas_{timestamp}.txt",
            texto_limpo
        )

        raise Exception(
            "A IA retornou apenas questões inválidas."
        )

    # ==================================================
    # RETORNO
    # ==================================================

    return questoes_validas