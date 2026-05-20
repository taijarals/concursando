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

from telas.cadastro_questao import (
    tela_cadastro
)

from telas.cadastrar_questoes_via_ia import (
    tela_cadastrar_questoes_via_ia
)

from telas.cadastrar_questoes_via_pdf import (
    tela_cadastrar_questoes_via_pdf
)


def tela_cadastros():

    st.title("🗂️ Cadastros")

    # =====================================
    # CONTROLE DE SUBTELA
    # =====================================

    if (
        "cadastro_questao_tela"
        not in st.session_state
    ):

        st.session_state[
            "cadastro_questao_tela"
        ] = "menu"

    # =====================================
    # ABAS PRINCIPAIS
    # =====================================

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

        tela_atual = st.session_state[
            "cadastro_questao_tela"
        ]

        # ===============================
        # MENU
        # ===============================

        if tela_atual == "menu":

            st.subheader(
                "Selecione o tipo de cadastro"
            )

            opcao = st.selectbox(

                "Tipo de Importação",

                [
                    "✍️ Manual",
                    "🤖 Via IA",
                    "📄 Via PDF"
                ],

                key="menu_tipo_questao"
            )

            if st.button(
                "Abrir",
                key="abrir_tipo_questao"
            ):

                if opcao == "✍️ Manual":

                    st.session_state[
                        "cadastro_questao_tela"
                    ] = "manual"

                elif opcao == "🤖 Via IA":

                    st.session_state[
                        "cadastro_questao_tela"
                    ] = "ia"

                elif opcao == "📄 Via PDF":

                    st.session_state[
                        "cadastro_questao_tela"
                    ] = "pdf"

                st.rerun()

        # ===============================
        # MANUAL
        # ===============================

        elif tela_atual == "manual":

            if st.button(
                "← Voltar",
                key="voltar_manual"
            ):

                st.session_state[
                    "cadastro_questao_tela"
                ] = "menu"

                st.rerun()

            tela_cadastro()

        # ===============================
        # IA
        # ===============================

        elif tela_atual == "ia":

            if st.button(
                "← Voltar",
                key="voltar_ia"
            ):

                st.session_state[
                    "cadastro_questao_tela"
                ] = "menu"

                st.rerun()

            tela_cadastrar_questoes_via_ia()

        # ===============================
        # PDF
        # ===============================

        elif tela_atual == "pdf":

            if st.button(
                "← Voltar",
                key="voltar_pdf"
            ):

                st.session_state[
                    "cadastro_questao_tela"
                ] = "menu"

                st.rerun()

            tela_cadastrar_questoes_via_pdf()