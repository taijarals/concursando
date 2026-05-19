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


PROMPT_EXTRACAO_PAGINA = """
Você é um extrator especializado em provas de concurso.

IMPORTANTE - Leia com atenção:
- Algumas provas têm uma DIVISÓRIA VERTICAL no meio da página
- Quando isso acontecer, SEMPRE leia PRIMEIRO o lado ESQUERDO da página
- Depois leia o lado DIREITO da página
- Processe como se fossem duas páginas separadas

Identifique a estrutura da prova:
- Uma MATÉRIA/DISCIPLINA (ex: Português, Matemática, Direito Constitucional) pode aparecer uma só vez como título
- TODAS as questões que aparecem depois do título pertencem àquela matéria ATÉ que apareça um novo título de matéria
- O título da matéria geralmente está destacado ou em uma linha separada

Extraia TODAS as questões desta página, identificando:
- O tipo de questão
- A disciplina/matéria (ex: Português, Matemática, Direito Constitucional, etc)
- O assunto específico dentro da disciplina (ex: Regência Verbal, Progressão Aritmética, Separação de Poderes, etc)

Para cada questão retorne:

{
  "numero": int,
  "tipo": "multipla_escolha" | "certo_errado" | "aberta",
  "enunciado": str,
  "materia": "Nome da disciplina/matéria",
  "assunto": "Assunto específico da questão",
  "alternativas": [
      {
        "letra": "A",
        "texto": str,
        "correta": bool (opcional, marcar se souber)
      }
   ],
  "resposta_correta": "A" (se aplicável),
  "explicacao_ia": "Breve justificativa (se possível)"
}

REGRAS:
- Ignore cabeçalhos
- Ignore rodapés
- Ignore número das páginas
- Ignore instruções da prova
- NÃO invente informações
- SEMPRE tente identificar a matéria e assunto baseado no conteúdo da questão
- Se não souber a matéria/assunto, deixe em branco (string vazia)
- Retorne APENAS JSON válido
- Se não encontrar nenhuma questão, retorne []
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


def obter_modelo_deepseek():
    """
    Obtém modelo via OpenRouter (Deepseek).
    Requer OPENROUTER_API_KEY no ambiente.
    """
    import os
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY não configurada no ambiente."
        )
    
    return {
        "type": "openrouter",
        "api_key": api_key,
        "model": "deepseek/deepseek-chat"
    }


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


def prever_resposta_gemini(enunciado, alternativas, numero):
    """
    Usa o modelo Gemini para prever qual alternativa é mais provável correta
    Retorna (letra, explicacao) ou (None, None) em caso de falha.
    """
    try:
        modelo = obter_modelo_gemini_pdf()

        alt_text = "\n".join([
            f"{a['letra']}) {a['texto']}" for a in alternativas
        ])

        prompt = f"""
Você é um especialista em resolver questões de concurso.
Dada a seguinte questão e alternativas, indique qual alternativa é mais provavelmente a correta e forneça uma breve justificativa.
Retorne APENAS um objeto JSON com as chaves: "resposta_prevista" (letra maiúscula) e "explicacao".

Questão (nº {numero}):
{enunciado}

Alternativas:
{alt_text}
"""

        resposta = modelo.generate_content(prompt)
        texto = limpar_resposta_json(resposta.text)
        dados = json.loads(texto)

        letra = dados.get("resposta_prevista") or dados.get("resposta")
        explic = dados.get("explicacao") or dados.get("justificativa") or dados.get("explicacao_ia")

        if isinstance(letra, str):
            letra = letra.strip().upper()[:1]

        return letra, (explic or "").strip()

    except Exception:
        return None, None


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

    materia = limpar_texto(
        str(item.get("materia", ""))
    )

    assunto = limpar_texto(
        str(item.get("assunto", ""))
    )

    # Gerar avisos se necessário
    avisos = gerar_avisos_questao(
        item,
        alternativas,
        enunciado
    )

    questao = {
        "numero": numero,
        "tipo": tipo,
        "enunciado": enunciado,
        "materia": materia,
        "assunto": assunto,
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
        "revisar": len(avisos) > 0,
        "avisos": avisos,
        "pagina": item.get("pagina")
    }

    # Se for múltipla escolha, tente marcar a alternativa correta
    if questao["tipo"] == "multipla_escolha":
        # Se alternativa correta já foi informada nas alternativas, use-a
        marcada = any(a.get("correta") for a in questao.get("alternativas", []))

        if marcada and not questao.get("resposta_correta"):
            for a in questao["alternativas"]:
                if a.get("correta"):
                    questao["resposta_correta"] = a.get("letra")
                    break

        # Se resposta_correta preenchida no item, marcar a alternativa correspondente
        if questao.get("resposta_correta") and not marcada:
            letra = str(questao.get("resposta_correta") or "").strip().upper()[:1]
            for a in questao["alternativas"]:
                a["correta"] = (a.get("letra") == letra)
            marcada = True

        # Caso não exista marcação, pedir ao modelo que preveja
        if not marcada:
            letra_prevista, explic = prever_resposta_gemini(
                questao["enunciado"],
                questao["alternativas"],
                questao["numero"]
            )

            if letra_prevista:
                questao["resposta_correta"] = letra_prevista
                # marcar a alternativa correta
                for a in questao["alternativas"]:
                    a["correta"] = (a.get("letra") == letra_prevista)

                # preencher explicação se não existir
                if not questao.get("explicacao_ia"):
                    questao["explicacao_ia"] = explic

                # adicionar aviso indicando que IA sugeriu a resposta
                questao["avisos"].append(
                    f"IA indicou '{letra_prevista}' como resposta provável"
                )

                # Recomendar revisão humana
                questao["revisar"] = True

    return questao


def gerar_avisos_questao(item, alternativas, enunciado):
    """
    Gera avisos para questões que podem ter problemas.
    """
    avisos = []

    # Aviso se enunciado muito curto
    if enunciado and len(enunciado.strip()) < 10:
        avisos.append("Enunciado muito curto - revise se foi extraído corretamente")

    # Aviso se faltam alternativas
    if len(alternativas) < 2:
        avisos.append(f"Poucas alternativas encontradas ({len(alternativas)} - esperado 4-5)")

    # Aviso se matéria não foi identificada
    materia = str(item.get("materia", "")).strip()
    if not materia:
        avisos.append("Matéria/disciplina não foi identificada - revise e complete manualmente")

    return avisos


def extrair_questoes_com_deepseek(
    texto_pagina,
    numero_pagina,
    dados_prova
):
    """
    Extrai questões usando Deepseek via OpenRouter.
    """
    import requests
    
    modelo_info = obter_modelo_deepseek()
    
    headers = {
        "Authorization": f"Bearer {modelo_info['api_key']}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
{PROMPT_EXTRACAO_PAGINA}

Aqui está o conteúdo da página {numero_pagina}:

{texto_pagina}
"""

    payload = {
        "model": modelo_info["model"],
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(
            f"Erro ao chamar Deepseek: {response.text}"
        )
    
    resposta = response.json()
    texto_resposta = resposta["choices"][0]["message"]["content"]
    
    try:
        itens = carregar_json_questoes(texto_resposta)
    except (json.JSONDecodeError, ValueError):
        return []

    questoes = []

    for indice, item in enumerate(itens, start=1):
        if isinstance(item, dict) and item.get("enunciado"):
            questao = montar_questao_gemini(
                item,
                indice,
                dados_prova
            )
            questao["pagina"] = numero_pagina
            questoes.append(questao)

    return questoes


def extrair_questoes_pagina_texto(
    texto_pagina,
    numero_pagina,
    dados_prova,
    modelo_ia="gemini"
):
    """
    Extrai questões de uma página usando texto simples.
    Suporta múltiplos modelos de IA.
    
    Args:
        texto_pagina: Texto da página
        numero_pagina: Número da página
        dados_prova: Dados da prova
        modelo_ia: "gemini" ou "deepseek"
    """
    if not texto_pagina or not texto_pagina.strip():
        return []

    if modelo_ia == "deepseek":
        return extrair_questoes_com_deepseek(
            texto_pagina,
            numero_pagina,
            dados_prova
        )
    
    # Padrão: Gemini
    modelo = obter_modelo_gemini_pdf()

    prompt = f"""
{PROMPT_EXTRACAO_PAGINA}

Aqui está o conteúdo da página {numero_pagina}:

{texto_pagina}
"""

    response = modelo.generate_content(prompt)

    try:
        itens = carregar_json_questoes(response.text)
    except (json.JSONDecodeError, ValueError):
        return []

    questoes = []

    for indice, item in enumerate(itens, start=1):
        if isinstance(item, dict) and item.get("enunciado"):
            questao = montar_questao_gemini(
                item,
                indice,
                dados_prova
            )
            questao["pagina"] = numero_pagina
            questoes.append(questao)

    return questoes


def extrair_questoes_pdf_gemini(
    origem_pdf,
    dados_prova
):
    """
    Mantém compatibilidade com a versão anterior.
    Processa o PDF inteiro (modo antigo).
    """
    pdf_bytes = ler_bytes_pdf(origem_pdf)

    if not pdf_bytes:
        raise ValueError(
            "PDF vazio ou inválido."
        )

    modelo = obter_modelo_gemini_pdf()

    response = modelo.generate_content([
        PROMPT_EXTRACAO_PAGINA,
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
