import streamlit as st

from database.supabase_client import supabase


def tela_cadastro_banca():

    st.title("🏛️ Cadastro de Bancas")

    nome = st.text_input(
        "Nome da Banca"
    )

    if st.button("Salvar Banca"):

        if not nome:

            st.warning(
                "Informe o nome."
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

        except Exception as e:

            st.error(str(e))

    st.divider()

    st.subheader("Bancas cadastradas")

    response = (
        supabase
        .table("concur_bancas")
        .select("*")
        .order("id")
        .execute()
    )

    for banca in response.data:

        st.write(
            f"{banca['id']} - "
            f"{banca['nome']}"
        )