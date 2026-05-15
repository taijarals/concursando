import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("📚 Concurso AI")

        st.divider()

        menu = st.radio(
            "Menu",
            [
                "Dashboard",
                "Cadastros",
                "Resolver Questões",
                "Importar Questões",
                "Importar PDF",
                "Listar Questões"
            ]
        )

        st.divider()

        if st.button("Logout"):

            del st.session_state["user"]

            st.rerun()

    return menu