import streamlit as st

from services.pdf_service import extrair_paginas_pdf, juntar_texto_paginas
from services.prova_pdf_parser import identificar_dados_prova


def inicializar_estado_pdf():
    if "pdf_etapa" not in st.session_state:
        st.session_state["pdf_etapa"] = "upload"


def resetar_importacao_pdf():
    chaves = [
        "pdf_etapa",
        "pdf_paginas",
        "pdf_dados",
        "pdf_dados_confirmados",
        "pdf_questoes"
    ]

    for chave in chaves:
        st.session_state.pop(chave, None)

    st.session_state["pdf_etapa"] = "upload"


def render_upload_pdf():
    st.subheader("1. Enviar PDF")

    arquivo_pdf = st.file_uploader(
        "Arquivo PDF",
        type=["pdf"]
    )

    if not arquivo_pdf:
        st.info("Envie um arquivo PDF para começar.")
        return

    if st.button("Analisar PDF"):
        with st.spinner("Lendo PDF e identificando dados da prova..."):
            try:
                paginas = extrair_paginas_pdf(arquivo_pdf)
                dados = identificar_dados_prova(paginas)

                st.session_state["pdf_paginas"] = paginas
                st.session_state["pdf_dados"] = dados
                st.session_state["pdf_etapa"] = "confirmar_dados"

                st.success("PDF analisado com sucesso!")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao analisar PDF: {e}")


def render_confirmar_dados():
    st.subheader("2. Confirmar dados da prova")

    dados = st.session_state.get("pdf_dados", {})

    st.write(
        "Confira os dados identificados automaticamente. "
        "Se algum estiver errado, corrija antes de continuar."
    )

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
        f"Páginas lidas para identificar dados: "
        f"{dados.get('paginas_lidas', '')}"
    )

    with st.expander("Prévia do texto extraído"):
        paginas = st.session_state.get("pdf_paginas", [])

        if paginas:
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
                height=300
            )

    col_voltar, col_confirmar = st.columns(2)

    with col_voltar:
        if st.button("🔄 Trocar PDF"):
            resetar_importacao_pdf()
            st.rerun()

    with col_confirmar:
        if st.button("✅ Confirmar dados da prova"):
            if not banca or not ano or not instituicao or not cargo:
                st.warning(
                    "Preencha banca, ano, instituição e cargo antes de continuar."
                )
                return

            st.session_state["pdf_dados_confirmados"] = {
                "banca": banca.strip().upper(),
                "ano": str(ano).strip(),
                "instituicao": instituicao.strip().upper(),
                "cargo": cargo.strip().upper()
            }

            st.session_state["pdf_etapa"] = "identificar_questoes"

            st.success("Dados confirmados!")
            st.rerun()


def render_identificar_questoes():
    st.subheader("3. Identificar questões")

    dados = st.session_state.get("pdf_dados_confirmados", {})

    st.write("Dados confirmados:")

    st.json(dados)

    st.info(
        "Na próxima etapa, o sistema vai usar esses dados como contexto "
        "para tentar identificar as questões do PDF."
    )

    if st.button("🔎 Identificar questões do PDF"):
        with st.spinner("Identificando questões..."):
            try:
                # Por enquanto, esta etapa ainda é um placeholder.
                # No próximo passo vamos implementar a extração real.
                st.session_state["pdf_questoes"] = []
                st.session_state["pdf_etapa"] = "revisar_questoes"

                st.success("Processo de identificação iniciado!")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao identificar questões: {e}")


def render_revisar_questoes():
    st.subheader("4. Revisar questões")

    questoes = st.session_state.get("pdf_questoes", [])

    if not questoes:
        st.warning(
            "Nenhuma questão foi identificada ainda. "
            "A extração real das questões será implementada no próximo passo."
        )

        if st.button("⬅️ Voltar para identificação"):
            st.session_state["pdf_etapa"] = "identificar_questoes"
            st.rerun()

        return

    for indice, questao in enumerate(questoes, start=1):
        with st.expander(f"Questão {indice}"):
            st.write(questao)

    if st.button("💾 Importar questões para o banco"):
        st.info(
            "A importação para o banco será implementada depois da revisão."
        )


def tela_importar_pdf():
    inicializar_estado_pdf()

    st.title("📄 Importar Prova PDF")

    st.write(
        "Envie uma prova em PDF, confirme os dados identificados "
        "e depois avance para a extração das questões."
    )

    if st.button("🧹 Reiniciar importação PDF"):
        resetar_importacao_pdf()
        st.rerun()

    st.divider()

    etapa = st.session_state.get("pdf_etapa", "upload")

    if etapa == "upload":
        render_upload_pdf()

    elif etapa == "confirmar_dados":
        render_confirmar_dados()

    elif etapa == "identificar_questoes":
        render_identificar_questoes()

    elif etapa == "revisar_questoes":
        render_revisar_questoes()