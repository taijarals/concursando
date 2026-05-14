import streamlit as st
from database.supabase_client import supabase


def login():

    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        try:

            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state["user"] = response.user

            st.success("Login realizado!")

            st.rerun()

        except Exception as e:
            st.error("Email ou senha inválidos")


def register():

    st.title("📝 Cadastro")

    email = st.text_input("Novo Email")

    password = st.text_input(
        "Nova Senha",
        type="password"
    )

    if st.button("Cadastrar"):

        try:

            supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            st.success(
                "Usuário criado com sucesso!"
            )

        except Exception as e:
            st.error(str(e))