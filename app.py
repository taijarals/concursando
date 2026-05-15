import streamlit as st

from auth import login, register

from components.sidebar import render_sidebar

from telas.dashboard import tela_dashboard
from telas.cadastro_questao import tela_cadastro
from telas.resolver_questoes import tela_resolver
from telas.cadastro_materia import tela_cadastro_materia
from telas.cadastro_assunto import tela_cadastro_assunto
from telas.cadastro_banca import tela_cadastro_banca
from telas.importar_questoes import tela_importacao
from telas.listar_questoes import tela_listar_questoes
from telas.cadastro import tela_cadastros


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

    elif menu == "Cadastrar Questão":
        tela_cadastro()

    elif menu == "Resolver Questões":
        tela_resolver()

    elif menu == "Cadastrar Matéria":
        tela_cadastro_materia()

    elif menu == "Cadastrar Assunto":
        tela_cadastro_assunto()

    elif menu == "Cadastrar Banca":
        tela_cadastro_banca()
        
    elif menu == "Importar Questões":
        tela_importacao()
    
    elif menu == "Listar Questões":
        tela_listar_questoes()