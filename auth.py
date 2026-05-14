import streamlit as st

from database.supabase_client import supabase


# =====================================
# LOGIN
# =====================================

def login():

    st.title("🔐 Login")

    email = st.text_input(
        "Email",
        key="login_email"
    )

    password = st.text_input(
        "Senha",
        type="password",
        key="login_password"
    )

    if st.button(
        "Entrar",
        key="login_button"
    ):

        try:

            response = (
                supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )
            )

            st.session_state["user"] = response.user

            st.success("Login realizado!")

            st.rerun()

        except Exception as e:

            st.error(str(e))


# =====================================
# CADASTRO
# =====================================

def register():

    st.title("📝 Cadastro")

    email = st.text_input(
        "Novo Email",
        key="register_email"
    )

    password = st.text_input(
        "Nova Senha",
        type="password",
        key="register_password"
    )

    if st.button(
        "Cadastrar",
        key="register_button"
    ):

        if not email or not password:

            st.warning(
                "Preencha email e senha."
            )

            return

        try:

            response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password
                }
            )

            st.success(
                "Usuário criado com sucesso!"
            )

        except Exception as e:

            st.error(str(e))