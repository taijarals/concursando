import streamlit as st
from database.supabase_client import supabase

st.title("Cadastro de Questão")

enunciado = st.text_area("Enunciado")

tipo = st.selectbox(
    "Tipo",
    ["multipla_escolha", "certo_errado", "aberta"]
)

resposta_correta = st.text_input(
    "Resposta Correta"
)

if st.button("Salvar"):

    data = {
        "tipo": tipo,
        "enunciado": enunciado,
        "resposta_correta": resposta_correta
    }

    response = (
        supabase
        .table("questoes")
        .insert(data)
        .execute()
    )

    st.success("Questão salva!")