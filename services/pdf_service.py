import pdfplumber


def extrair_paginas_pdf(arquivo_pdf):
    paginas = []

    with pdfplumber.open(arquivo_pdf) as pdf:
        for indice, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""

            paginas.append({
                "numero": indice,
                "texto": texto
            })

    return paginas


def juntar_texto_paginas(paginas, limite=None):
    textos = []

    paginas_usadas = paginas

    if limite:
        paginas_usadas = paginas[:limite]

    for pagina in paginas_usadas:
        textos.append(
            f"\n\n--- PÁGINA {pagina['numero']} ---\n\n"
            f"{pagina['texto']}"
        )

    return "\n".join(textos)