import streamlit as st

from database.supabase_client import supabase


@st.dialog("📝 Novo Assunto")
def modal_assunto():

    materias = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    materias_map = {
        item["nome"]: item["id"]
        for item in materias.data
    }

    materia_nome = st.selectbox(
        "Matéria",
        list(materias_map.keys())
        if materias_map else [],
        key="modal_assunto_materia"
    )

    nome = st.text_input(
        "Nome do Assunto",
        key="novo_assunto"
    )

    if st.button(
        "Salvar Assunto"
    ):

        if not nome:

            st.warning(
                "Informe o nome do assunto."
            )

            return

        try:

            (
                supabase
                .table("concur_assuntos")
                .insert({

                    "materia_id":
                        materias_map[materia_nome],

                    "nome":
                        nome
                })
                .execute()
            )

            st.success(
                "Assunto cadastrado!"
            )

            st.rerun()

        except Exception as e:

            st.error(str(e))