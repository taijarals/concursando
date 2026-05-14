import streamlit as st

from database.supabase_client import supabase


def tela_cadastro_materia():

    st.title("📚 Cadastro de Matérias")

    nome = st.text_input(
        "Nome da Matéria"
    )

    if st.button("Salvar Matéria"):

        if not nome:

            st.warning(
                "Informe o nome."
            )

            return

        try:

            (
                supabase
                .table("concur_materias")
                .insert({
                    "nome": nome
                })
                .execute()
            )

            st.success(
                "Matéria cadastrada!"
            )

        except Exception as e:

            st.error(str(e))

    st.divider()

    st.subheader("Matérias cadastradas")

    response = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("id")
        .execute()
    )

    for materia in response.data:

        st.write(
            f"{materia['id']} - "
            f"{materia['nome']}"
        )