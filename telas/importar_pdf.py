import streamlit as st

from services.pdf_service import extrair_paginas_pdf, juntar_texto_paginas
from services.prova_pdf_parser import identificar_dados_prova


def tela_importar_pdf():
    st.title("📄 Importar Prova PDF")

    st.write(
        "Envie o PDF de uma prova para extrair o texto e tentar "
        "identificar dados como banca, ano, instituição e cargo."
    )

    arquivo_pdf = st.file_uploader(
        "Arquivo PDF",
        type=["pdf"]
    )

    if not arquivo_pdf:
        st.info("Envie um arquivo PDF para começar.")
        return

    if st.button("Analisar PDF"):
        with st.spinner("Lendo PDF..."):
            try:
                paginas = extrair_paginas_pdf(arquivo_pdf)

                dados = identificar_dados_prova(paginas)

                st.session_state["pdf_paginas"] = paginas
                st.session_state["pdf_dados"] = dados

                st.success("PDF analisado com sucesso!")

            except Exception as e:
                st.error(f"Erro ao analisar PDF: {e}")
                return

    if "pdf_paginas" not in st.session_state:
        return

    paginas = st.session_state["pdf_paginas"]
    dados = st.session_state["pdf_dados"]

    st.divider()

    st.subheader("Dados identificados")

    col1, col2 = st.columns(2)

    with col1:
        banca = st.text_input(
            "Banca",
            value=dados.get("banca", "")
        )

        instituicao = st.text_input(
            "Instituição",
            value=dados.get("instituicao", "")
        )

    with col2:
        ano = st.text_input(
            "Ano",
            value=dados.get("ano", "")
        )

        cargo = st.text_input(
            "Cargo",
            value=dados.get("cargo", "")
        )

    st.caption(
        f"Páginas lidas até identificar dados: "
        f"{dados.get('paginas_lidas')}"
    )

    st.session_state["pdf_dados_editados"] = {
        "banca": banca,
        "ano": ano,
        "instituicao": instituicao,
        "cargo": cargo
    }

    st.divider()

    st.subheader("Prévia do texto extraído")

    limite_paginas = st.slider(
        "Quantidade de páginas para prévia",
        min_value=1,
        max_value=len(paginas),
        value=min(3, len(paginas))
    )

    texto_previa = juntar_texto_paginas(
        paginas,
        limite=limite_paginas
    )

    st.text_area(
        "Texto extraído",
        value=texto_previa,
        height=400
    )