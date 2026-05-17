import re


LETRAS_ALTERNATIVAS = [
    "A",
    "B",
    "C",
    "D",
    "E"
]


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
        numero = pagina.get("numero", "")
        texto = pagina.get("texto", "")

        textos.append(
            f"\n\n--- PÁGINA {numero} ---\n\n{texto}"
        )

    return limpar_texto(
        "\n".join(textos)
    )


def encontrar_marcadores_questoes(texto):
    padrao = re.compile(
        r"""
        (?imx)
        ^
        \s*
        (?:
            quest[aã]o
            |
            questão
        )
        \s*
        (?:n[ºo]\s*)?
        (?P<numero>\d{1,4})
        \b
        |
        ^
        \s*
        (?P<numero_simples>\d{1,4})
        \s*
        [\.\-\–\)]
        \s+
        (?=
            [A-ZÁÉÍÓÚÂÊÔÃÕÇ]
        )
        """,
    )

    marcadores = []

    for match in padrao.finditer(texto):
        numero = (
            match.group("numero")
            or match.group("numero_simples")
        )

        marcadores.append({
            "inicio": match.start(),
            "fim": match.end(),
            "numero": int(numero)
        })

    return marcadores


def separar_blocos_questoes(texto):
    texto = limpar_texto(texto)

    marcadores = encontrar_marcadores_questoes(texto)

    blocos = []

    for indice, marcador in enumerate(marcadores):
        inicio = marcador["inicio"]

        if indice + 1 < len(marcadores):
            fim = marcadores[indice + 1]["inicio"]
        else:
            fim = len(texto)

        bloco_texto = texto[inicio:fim].strip()

        if bloco_texto:
            blocos.append({
                "numero": marcador["numero"],
                "texto": bloco_texto
            })

    return blocos


def encontrar_marcadores_alternativas(texto):
    padrao = re.compile(
        r"""
        (?imx)
        ^
        \s*
        \(?
        (?P<letra>[A-Ea-e])
        \)?
        [\.\-\)]
        \s+
        """,
    )

    marcadores = []

    for match in padrao.finditer(texto):
        letra = match.group("letra").upper()

        marcadores.append({
            "inicio": match.start(),
            "fim": match.end(),
            "letra": letra
        })

    return marcadores


def extrair_alternativas(texto):
    marcadores = encontrar_marcadores_alternativas(texto)

    alternativas = []

    for indice, marcador in enumerate(marcadores):
        inicio_texto = marcador["fim"]

        if indice + 1 < len(marcadores):
            fim_texto = marcadores[indice + 1]["inicio"]
        else:
            fim_texto = len(texto)

        alternativa_texto = texto[inicio_texto:fim_texto].strip()

        alternativas.append({
            "letra": marcador["letra"],
            "texto": limpar_texto(alternativa_texto),
            "correta": False
        })

    alternativas_filtradas = []

    letras_vistas = set()

    for alternativa in alternativas:
        letra = alternativa["letra"]
        texto_alternativa = alternativa["texto"]

        if letra in letras_vistas:
            continue

        if letra not in LETRAS_ALTERNATIVAS:
            continue

        if not texto_alternativa:
            continue

        letras_vistas.add(letra)
        alternativas_filtradas.append(alternativa)

    return alternativas_filtradas


def remover_alternativas_do_enunciado(texto):
    marcadores = encontrar_marcadores_alternativas(texto)

    if not marcadores:
        return limpar_texto(texto)

    primeiro_marcador = marcadores[0]

    return limpar_texto(
        texto[:primeiro_marcador["inicio"]]
    )


def remover_titulo_questao(texto, numero):
    padroes = [
        rf"(?im)^\s*quest[aã]o\s*(?:n[ºo]\s*)?{numero}\b\s*",
        rf"(?im)^\s*questão\s*(?:n[ºo]\s*)?{numero}\b\s*",
        rf"(?im)^\s*{numero}\s*[\.\-\–\)]\s*"
    ]

    texto_limpo = texto

    for padrao in padroes:
        texto_limpo = re.sub(
            padrao,
            "",
            texto_limpo,
            count=1
        )

    return limpar_texto(texto_limpo)


def parece_certo_errado(texto):
    texto_upper = texto.upper()

    indicios = [
        "CERTO OU ERRADO",
        "JULGUE",
        "JULGAR",
        "CERTO",
        "ERRADO",
        "Certo",
        "Errado"
    ]

    return any(
        indicio.upper() in texto_upper
        for indicio in indicios
    )


def identificar_tipo_questao(texto, alternativas):
    if len(alternativas) >= 2:
        return "multipla_escolha"

    if parece_certo_errado(texto):
        return "certo_errado"

    return "aberta"


def inferir_materia_assunto(texto):
    return {
        "materia": "GERAL",
        "assunto": "A CLASSIFICAR"
    }


def montar_fonte(dados_prova):
    partes = []

    instituicao = dados_prova.get("instituicao")
    banca = dados_prova.get("banca")
    ano = dados_prova.get("ano")
    cargo = dados_prova.get("cargo")

    if instituicao:
        partes.append(instituicao)

    if banca:
        partes.append(banca)

    if cargo:
        partes.append(cargo)

    if ano:
        partes.append(str(ano))

    return " - ".join(partes)


def validar_questao_extraida(questao):
    avisos = []

    if not questao["enunciado"]:
        avisos.append("Enunciado vazio.")

    if len(questao["enunciado"]) < 40:
        avisos.append("Enunciado muito curto.")

    if questao["tipo"] == "multipla_escolha":
        quantidade_alternativas = len(
            questao.get("alternativas", [])
        )

        if quantidade_alternativas < 2:
            avisos.append(
                "Questão marcada como múltipla escolha, "
                "mas tem menos de 2 alternativas."
            )

        letras = [
            alternativa["letra"]
            for alternativa in questao.get("alternativas", [])
        ]

        if len(letras) != len(set(letras)):
            avisos.append("Alternativas com letras repetidas.")

    if questao["tipo"] == "certo_errado":
        if questao.get("alternativas"):
            avisos.append(
                "Questão certo/errado contém alternativas detectadas."
            )

    questao["avisos"] = avisos
    questao["revisar"] = bool(avisos)

    return questao


def montar_questao_extraida(bloco, dados_prova):
    numero = bloco["numero"]
    texto_bloco = bloco["texto"]

    texto_sem_titulo = remover_titulo_questao(
        texto_bloco,
        numero
    )

    alternativas = extrair_alternativas(
        texto_sem_titulo
    )

    enunciado = remover_alternativas_do_enunciado(
        texto_sem_titulo
    )

    tipo = identificar_tipo_questao(
        texto_sem_titulo,
        alternativas
    )

    classificacao = inferir_materia_assunto(
        texto_sem_titulo
    )

    if tipo != "multipla_escolha":
        alternativas = []

    questao = {
        "numero": numero,
        "tipo": tipo,
        "enunciado": enunciado,
        "materia": classificacao["materia"],
        "assunto": classificacao["assunto"],
        "banca": dados_prova.get("banca", ""),
        "cargo": dados_prova.get("cargo", ""),
        "instituicao": dados_prova.get("instituicao", ""),
        "ano": dados_prova.get("ano", ""),
        "dificuldade": 3,
        "fonte": montar_fonte(dados_prova),
        "resposta_correta": "",
        "alternativas": alternativas,
        "explicacao_ia": None,
        "texto_original": texto_bloco,
        "revisar": False,
        "avisos": []
    }

    return validar_questao_extraida(questao)


def extrair_questoes_pdf(paginas, dados_prova):
    texto = juntar_texto_paginas(paginas)

    blocos = separar_blocos_questoes(texto)

    questoes = []

    for bloco in blocos:
        questao = montar_questao_extraida(
            bloco,
            dados_prova
        )

        questoes.append(questao)

    return questoes