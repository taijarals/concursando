import streamlit as st

from auth import login, register

st.set_page_config(
    page_title="lorem ipsum",
    layout="wide"
)

if "user" not in st.session_state:

    aba1, aba2 = st.tabs([
        "Login",
        "Cadastro"
    ])

    with aba1:
        login()

    with aba2:
        register()

else:

    st.sidebar.success(
        f"Logado como: "
        f"{st.session_state['user'].email}"
    )

    if st.sidebar.button("Logout"):

        del st.session_state["user"]

        st.rerun()

    st.title("📚 Concurso AI")

    st.write("Sistema carregado!")