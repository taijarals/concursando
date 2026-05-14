import streamlit as st

from database.supabase_client import supabase


def tela_cadastro():

    st.title("➕ Cadastro de Questão")

    # =========================
    # ENUNCIADO
    # =========================

    enunciado = st.text_area(
        "Enunciado"
    )

    # =========================
    # TIPO
    # =========================

    tipo = st.selectbox(
        "Tipo",
        [
            "multipla_escolha",
            "certo_errado",
            "aberta"
        ]
    )

    # =========================
    # RESPOSTA CORRETA
    # =========================

    resposta_correta = st.text_input(
        "Resposta Correta"
    )

    # =========================
    # BOTÃO SALVAR
    # =========================

    if st.button("Salvar Questão"):

        data = {
            "tipo": tipo,
            "enunciado": enunciado,
            "resposta_correta": resposta_correta
        }

        try:

            response = (
                supabase
                .table("concur_questoes")
                .insert(data)
                .execute()
            )

            st.success(
                "Questão salva com sucesso!"
            )

        except Exception as e:

            st.error(
                f"Erro ao salvar: {e}"
            )