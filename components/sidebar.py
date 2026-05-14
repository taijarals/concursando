import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("📚 Concurso AI")

        st.divider()

        menu = st.radio(
            "Menu",
            [
                "Dashboard",
                "Cadastrar Matéria",
                "Cadastrar Assunto",
                "Cadastrar Banca",
                "Cadastrar Questão",
                "Resolver Questões",
                "Importar Questões"
            ]
        )

        st.divider()

        if st.button("Logout"):

            del st.session_state["user"]

            st.rerun()

    return menu