import streamlit as st

from auth import login, register

from pages.cadastro_questao import tela_cadastro
from pages.resolver_questoes import tela_resolver
from pages.dashboard import tela_dashboard
from pages.historico import tela_historico


st.set_page_config(
    page_title="Concurso AI",
    layout="wide"
)


# =========================
# LOGIN
# =========================

if "user" not in st.session_state:

    aba1, aba2 = st.tabs([
        "Login",
        "Cadastro"
    ])

    with aba1:
        login()

    with aba2:
        register()

# =========================
# APP
# =========================

else:

    # =========================
    # SIDEBAR
    # =========================

    with st.sidebar:

        st.title("📚 Concurso AI")

        st.success(
            f"Usuário:\n"
            f"{st.session_state['user'].email}"
        )

        menu = st.radio(
            "Menu",
            [
                "Resolver Questões",
                "Cadastrar Questão",
                "Dashboard",
                "Histórico"
            ]
        )

        st.divider()

        if st.button("Logout"):

            del st.session_state["user"]

            st.rerun()

    # =========================
    # ROTAS
    # =========================

    if menu == "Resolver Questões":
        tela_resolver()

    elif menu == "Cadastrar Questão":
        tela_cadastro()

    elif menu == "Dashboard":
        tela_dashboard()

    elif menu == "Histórico":
        tela_historico()