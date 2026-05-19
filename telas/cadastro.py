import streamlit as st

from telas.cadastro_materia import tela_cadastro_materia
from telas.cadastro_assunto import tela_cadastro_assunto
from telas.cadastro_banca import tela_cadastro_banca
from telas.cadastro_questao import tela_cadastro
from telas.cadastrar_questoes_via_ia import (
    tela_cadastrar_questoes_via_ia
)
from telas.cadastrar_questoes_via_pdf import (
    tela_cadastrar_questoes_via_pdf
)


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
        (
            aba_manual,
            aba_ia,
            aba_pdf
        ) = st.tabs([
            "✍️ Manual",
            "🤖 Via IA",
            "📄 Via PDF"
        ])

        with aba_manual:
            tela_cadastro()

        with aba_ia:
            tela_cadastrar_questoes_via_ia()

        with aba_pdf:
            tela_cadastrar_questoes_via_pdf()
