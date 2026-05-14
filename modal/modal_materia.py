import streamlit as st

from database.supabase_client import supabase


@st.dialog("📚 Nova Matéria")
def modal_materia():

    nome = st.text_input(
        "Nome da Matéria",
        key="nova_materia"
    )

    if st.button(
        "Salvar Matéria"
    ):

        if not nome:

            st.warning(
                "Informe o nome da matéria."
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

            st.rerun()

        except Exception as e:

            st.error(str(e))