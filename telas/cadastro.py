import streamlit as st

from telas.cadastro_materia import (
    tela_cadastro_materia
)

from telas.cadastro_assunto import (
    tela_cadastro_assunto
)

from telas.cadastro_banca import (
    tela_cadastro_banca
)


def tela_cadastros():

    st.title("🗂️ Cadastros")

    (
        aba_materia,
        aba_assunto,
        aba_banca,
        aba_questao

    ) = st.tabs([

        "📚 Matérias",
        "📝 Assuntos",
        "🏛️ Bancas",
        "➕ Questões"
    ])

    # =====================================
    # MATÉRIAS
    # =====================================

    with aba_materia:

        tela_cadastro_materia()

    # =====================================
    # ASSUNTOS
    # =====================================

    with aba_assunto:

        tela_cadastro_assunto()

    # =====================================
    # BANCAS
    # =====================================

    with aba_banca:

        tela_cadastro_banca()

    # =====================================
    # QUESTÕES
    # =====================================

    with aba_questao:

        st.subheader(
            "Cadastro de Questões"
        )

        opcao = st.selectbox(

            "Selecione o tipo",

            [
                "✍️ Manual",
                "🤖 Via IA",
                "📄 Via PDF"
            ],

            key="tipo_cadastro_questao"
        )

        if st.button(
            "Abrir",
            key="abrir_cadastro_questao"
        ):

            if opcao == "✍️ Manual":

                st.session_state[
                    "pagina"
                ] = "cadastro_manual"

            elif opcao == "🤖 Via IA":

                st.session_state[
                    "pagina"
                ] = "cadastro_ia"

            elif opcao == "📄 Via PDF":

                st.session_state[
                    "pagina"
                ] = "cadastro_pdf"

            st.rerun()