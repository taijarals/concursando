import json
import re

import google.generativeai as genai

from config import GEMINI_API_KEY


LETRAS_ALTERNATIVAS = [
    "A",
    "B",
    "C",
    "D",
    "E"
]


GEMINI_PDF_MODEL = "gemini-2.0-flash"


PROMPT_EXTRACAO_GEMINI = """
Você é um extrator especializado em provas de concurso.

Extraia TODAS as questões da prova.

Para cada questão retorne:

{
  "numero": int,
  "tipo": "multipla_escolha" | "certo_errado" | "aberta",
  "enunciado": str,
  "alternativas": [
      {
        "letra": "A",
        "texto": str
      }
  ]
}

REGRAS:
- Ignore cabeçalhos
- Ignore rodapés
- Ignore número das páginas
- Ignore instruções da prova
- NÃO invente informações
- Retorne APENAS JSON válido
"""


def limpar_texto(texto):
    if not texto:
        return ""

    texto = texto.replace("\r", "\n")

    texto = re.sub(
        r"[ \t]+",
        " ",
        texto
    )

    texto = re.sub(
        r"\n{3,}",
        "\n\n",
        texto
    )

    return texto.strip()


def juntar_texto_paginas(paginas):
    textos = []

    for pagina in paginas:
        if pagina:
            textos.append(str(pagina))

    return "\n\n".join(textos)


def obter_modelo_gemini_pdf():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY não configurada no ambiente."
        )

    genai.configure(
        api_key=GEMINI_API_KEY
    )

    return genai.GenerativeModel(
        GEMINI_PDF_MODEL
    )


def ler_bytes_pdf(origem_pdf):
    if isinstance(origem_pdf, bytes):
        return origem_pdf

    if isinstance(origem_pdf, bytearray):
        return bytes(origem_pdf)

    if hasattr(origem_pdf, "getvalue"):
        return origem_pdf.getvalue()

    if hasattr(origem_pdf, "read"):
        posicao_atual = None

        if hasattr(origem_pdf, "tell"):
            posicao_atual = origem_pdf.tell()

        pdf_bytes = origem_pdf.read()

        if (
            posicao_atual is not None
            and hasattr(origem_pdf, "seek")
        ):
            origem_pdf.seek(posicao_atual)

        return pdf_bytes

    with open(origem_pdf, "rb") as arquivo:
        return arquivo.read()


def limpar_resposta_json(texto):
    texto = (texto or "").strip()

    if texto.startswith("```"):
        texto = re.sub(
            r"^```(?:json)?\s*",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\s*```$",
            "",
            texto
        )

    inicio_lista = texto.find("[")
    fim_lista = texto.rfind("]")

    if (
        inicio_lista != -1
        and fim_lista != -1
        and fim_lista > inicio_lista
    ):
        return texto[inicio_lista:fim_lista + 1]

    inicio_objeto = texto.find("{")
    fim_objeto = texto.rfind("}")

    if (
        inicio_objeto != -1
        and fim_objeto != -1
        and fim_objeto > inicio_objeto
    ):
        return texto[inicio_objeto:fim_objeto + 1]

    return texto


def carregar_json_questoes(texto):
    texto_json = limpar_resposta_json(texto)

    dados = json.loads(texto_json)

    if isinstance(dados, dict):
        for chave in [
            "questoes",
            "questions",
            "items"
        ]:
            if isinstance(dados.get(chave), list):
                return dados[chave]

        return [dados]

    if not isinstance(dados, list):
        raise ValueError(
            "A resposta da IA não retornou uma lista de questões."
        )

    return dados


def normalizar_alternativas_gemini(alternativas):
    alternativas_normalizadas = []

    letras_vistas = set()

    if not isinstance(alternativas, list):
        return alternativas_normalizadas

    for alternativa in alternativas:
        if not isinstance(alternativa, dict):
            continue

        letra = str(
            alternativa.get("letra", "")
        ).strip().upper()[:1]

        texto = limpar_texto(
            str(alternativa.get("texto", ""))
        )

        if letra not in LETRAS_ALTERNATIVAS:
            continue

        if letra in letras_vistas:
            continue

        if not texto:
            continue

        letras_vistas.add(letra)

        alternativas_normalizadas.append({
            "letra": letra,
            "texto": texto,
            "correta": bool(
                alternativa.get("correta", False)
            )
        })

    return alternativas_normalizadas


def normalizar_tipo_gemini(
    tipo,
    alternativas,
    enunciado
):
    tipo_normalizado = str(
        tipo or ""
    ).strip().lower()

    tipos_validos = [
        "multipla_escolha",
        "certo_errado",
        "aberta"
    ]

    if tipo_normalizado in tipos_validos:
        return tipo_normalizado

    return "multipla_escolha"


def normalizar_dificuldade_gemini(valor):
    try:
        dificuldade = int(valor or 3)

    except (
        TypeError,
        ValueError
    ):
        dificuldade = 3

    if dificuldade < 1:
        return 1

    if dificuldade > 5:
        return 5

    return dificuldade


def montar_questao_gemini(
    item,
    indice,
    dados_prova
):
    if not isinstance(item, dict):
        item = {}

    try:
        numero = int(
            item.get("numero") or indice
        )

    except (
        TypeError,
        ValueError
    ):
        numero = indice

    enunciado = limpar_texto(
        str(item.get("enunciado", ""))
    )

    alternativas = (
        normalizar_alternativas_gemini(
            item.get("alternativas", [])
        )
    )

    tipo = normalizar_tipo_gemini(
        item.get("tipo"),
        alternativas,
        enunciado
    )

    questao = {
        "numero": numero,
        "tipo": tipo,
        "enunciado": enunciado,
        "materia": item.get("materia", ""),
        "assunto": item.get("assunto", ""),
        "banca": dados_prova.get("banca", ""),
        "cargo": dados_prova.get("cargo", ""),
        "instituicao": dados_prova.get(
            "instituicao",
            ""
        ),
        "ano": dados_prova.get("ano", ""),
        "dificuldade": (
            normalizar_dificuldade_gemini(
                item.get("dificuldade")
            )
        ),
        "fonte": dados_prova.get(
            "fonte",
            ""
        ),
        "resposta_correta": item.get(
            "resposta_correta",
            ""
        ),
        "alternativas": alternativas,
        "explicacao_ia": item.get(
            "explicacao_ia"
        ),
        "texto_original": json.dumps(
            item,
            ensure_ascii=False
        ),
        "revisar": False,
        "avisos": []
    }

    return questao


def extrair_questoes_pdf_gemini(
    origem_pdf,
    dados_prova
):
    pdf_bytes = ler_bytes_pdf(origem_pdf)

    if not pdf_bytes:
        raise ValueError(
            "PDF vazio ou inválido."
        )

    modelo = obter_modelo_gemini_pdf()

    response = modelo.generate_content([
        PROMPT_EXTRACAO_GEMINI,
        {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }
    ])

    itens = carregar_json_questoes(
        response.text
    )

    questoes = []

    for indice, item in enumerate(
        itens,
        start=1
    ):
        questoes.append(
            montar_questao_gemini(
                item,
                indice,
                dados_prova
            )
        )

    return questoes