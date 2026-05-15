import streamlit as st

from auth import login, register

from components.sidebar import render_sidebar

from telas.dashboard import tela_dashboard
from telas.resolver_questoes import tela_resolver
from telas.importar_questoes import tela_importacao
from telas.listar_questoes import tela_listar_questoes
from telas.cadastro import tela_cadastros
from telas.importar_pdf import tela_importar_pdf


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

    elif menu == "Cadastros":
        tela_cadastros()

    elif menu == "Resolver Questões":
        tela_resolver()
        
    elif menu == "Importar Questões":
        tela_importacao()
    
    elif menu == "Listar Questões":
        tela_listar_questoes()

    elif menu == "Importar PDF":
        tela_importar_pdf()