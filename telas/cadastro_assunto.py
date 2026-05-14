import streamlit as st

from database.supabase_client import supabase


def tela_cadastro_assunto():

    st.title("📝 Cadastro de Assuntos")

    # =====================================
    # BUSCAR MATÉRIAS
    # =====================================

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

    # =====================================
    # FORMULÁRIO
    # =====================================

    materia_nome = st.selectbox(
        "Matéria",
        list(materias_map.keys())
    )

    nome = st.text_input(
        "Nome do Assunto"
    )

    # =====================================
    # SALVAR
    # =====================================

    if st.button("Salvar Assunto"):

        if not nome:

            st.warning(
                "Informe o nome."
            )

            return

        try:

            (
                supabase
                .table("concur_assuntos")
                .insert({
                    "materia_id":
                        materias_map[materia_nome],

                    "nome": nome
                })
                .execute()
            )

            st.success(
                "Assunto cadastrado!"
            )

        except Exception as e:

            st.error(str(e))

    st.divider()

    st.subheader("Assuntos cadastrados")

    response = (
        supabase
        .table("concur_assuntos")
        .select("""
            id,
            nome,
            concur_materias(nome)
        """)
        .order("id")
        .execute()
    )

    for assunto in response.data:

        materia = (
            assunto["concur_materias"]["nome"]
        )

        st.write(
            f"{assunto['id']} - "
            f"{materia} - "
            f"{assunto['nome']}"
        )