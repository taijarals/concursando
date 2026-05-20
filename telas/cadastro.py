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

    (
        aba_materia,
        aba_assunto,
        aba_banca,
        aba_questao_manual,
        aba_questao_ia,
        aba_questao_pdf

    ) = st.tabs([

        "📚 Matérias",
        "📝 Assuntos",
        "🏛️ Bancas",
        "✍️ Questões Manual",
        "🤖 Questões IA",
        "📄 Questões PDF"
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
    # QUESTÕES MANUAL
    # =====================================

    with aba_questao_manual:

        tela_cadastro()

    # =====================================
    # QUESTÕES IA
    # =====================================

    with aba_questao_ia:

        tela_cadastrar_questoes_via_ia()

    # =====================================
    # QUESTÕES PDF
    # =====================================

    with aba_questao_pdf:

        tela_cadastrar_questoes_via_pdf()