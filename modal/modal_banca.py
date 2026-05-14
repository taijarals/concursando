import streamlit as st

from database.supabase_client import supabase


@st.dialog("🏛️ Nova Banca")
def modal_banca():

    nome = st.text_input(
        "Nome da Banca",
        key="nova_banca"
    )

    if st.button(
        "Salvar Banca"
    ):

        if not nome:

            st.warning(
                "Informe o nome da banca."
            )

            return

        try:

            (
                supabase
                .table("concur_bancas")
                .insert({
                    "nome": nome
                })
                .execute()
            )

            st.success(
                "Banca cadastrada!"
            )

            st.rerun()

        except Exception as e:

            st.error(str(e))