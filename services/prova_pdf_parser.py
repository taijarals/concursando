import re


BANCAS_CONHECIDAS = [
    "FGV",
    "CEBRASPE",
    "CESPE",
    "FCC",
    "VUNESP",
    "IBFC",
    "AOCP",
    "IDECAN",
    "CONSULPLAN",
    "QUADRIX",
    "IADES",
    "INSTITUTO AOCP"
]


def encontrar_banca(texto):
    texto_upper = texto.upper()

    for banca in BANCAS_CONHECIDAS:
        if banca in texto_upper:
            return banca

    return ""


def encontrar_ano(texto):
    anos = re.findall(
        r"\b(20[0-9]{2})\b",
        texto
    )

    if anos:
        return anos[0]

    return ""


def encontrar_cargo(texto):
    padroes = [
        r"Cargo[:\s]+([^\n]+)",
        r"CARGO[:\s]+([^\n]+)",
        r"Emprego[:\s]+([^\n]+)",
        r"Função[:\s]+([^\n]+)"
    ]

    for padrao in padroes:
        resultado = re.search(
            padrao,
            texto,
            flags=re.IGNORECASE
        )

        if resultado:
            return resultado.group(1).strip()

    return ""


def encontrar_instituicao(texto):
    linhas = [
        linha.strip()
        for linha in texto.splitlines()
        if linha.strip()
    ]

    palavras_chave = [
        "PREFEITURA",
        "TRIBUNAL",
        "SECRETARIA",
        "MINISTÉRIO",
        "UNIVERSIDADE",
        "INSTITUTO",
        "CÂMARA",
        "ASSEMBLEIA",
        "POLÍCIA",
        "DEFENSORIA",
        "PROCURADORIA"
    ]

    for linha in linhas[:30]:
        linha_upper = linha.upper()

        for palavra in palavras_chave:
            if palavra in linha_upper:
                return linha

    return ""


def identificar_dados_prova(paginas):
    dados = {
        "banca": "",
        "ano": "",
        "instituicao": "",
        "cargo": "",
        "paginas_lidas": 0
    }

    texto_acumulado = ""

    for pagina in paginas:
        texto_acumulado += "\n" + pagina["texto"]
        dados["paginas_lidas"] = pagina["numero"]

        if not dados["banca"]:
            dados["banca"] = encontrar_banca(texto_acumulado)

        if not dados["ano"]:
            dados["ano"] = encontrar_ano(texto_acumulado)

        if not dados["instituicao"]:
            dados["instituicao"] = encontrar_instituicao(texto_acumulado)

        if not dados["cargo"]:
            dados["cargo"] = encontrar_cargo(texto_acumulado)

        if (
            dados["banca"]
            and dados["ano"]
            and dados["instituicao"]
            and dados["cargo"]
        ):
            break

    return dados