import streamlit as st

from telas.cadastro_materia import tela_cadastro_materia
from telas.cadastro_assunto import tela_cadastro_assunto
from telas.cadastro_banca import tela_cadastro_banca
from telas.cadastro_questao import tela_cadastro


def tela_cadastros():
    st.title("🗂️ Cadastros")

    aba_materia, aba_assunto, aba_banca, aba_questao = st.tabs([
        "📚 Matérias",
        "📝 Assuntos",
        "🏛️ Bancas",
        "➕ Questões"
    ])

    with aba_materia:
        tela_cadastro_materia()

    with aba_assunto:
        tela_cadastro_assunto()

    with aba_banca:
        tela_cadastro_banca()

    with aba_questao:
        tela_cadastro()