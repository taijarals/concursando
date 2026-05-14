import streamlit as st

from auth import login, register

from components.sidebar import render_sidebar

from telas.dashboard import tela_dashboard
from telas.cadastro_questao import tela_cadastro
from telas.resolver_questoes import tela_resolver


st.set_page_config(
    page_title="Concurso AI",
    layout="wide"
)


# ==================================
# LOGIN
# ==================================

if "user" not in st.session_state:

    aba1, aba2 = st.tabs([
        "Login",
        "Cadastro"
    ])

    with aba1:
        login()

    with aba2:
        register()


# ==================================
# SISTEMA
# ==================================

else:

    menu = render_sidebar()

    if menu == "Dashboard":
        tela_dashboard()

    elif menu == "Cadastrar Questão":
        tela_cadastro()

    elif menu == "Resolver Questões":
        tela_resolver()