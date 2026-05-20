import streamlit as st
from database.supabase_client import supabase


def tela_cadastro_materia():

    st.title("📚 Matérias")

    # ==========================================
    # BUSCAR DADOS
    # ==========================================

    response = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    materias = response.data

    # ==========================================
    # MÉTRICAS
    # ==========================================

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total de matérias",
            len(materias)
        )

    with col2:
        st.metric(
            "Status",
            "Ativo"
        )

    # ==========================================
    # NOVA MATÉRIA
    # ==========================================

    with st.expander("➕ Nova matéria"):

        with st.form("nova_materia"):

            nome = st.text_input(
                "Nome da matéria"
            )

            salvar = st.form_submit_button(
                "Salvar"
            )

        if salvar:

            nome = nome.upper().strip()

            if nome:

                existe = (
                    supabase
                    .table("concur_materias")
                    .select("*")
                    .eq("nome", nome)
                    .execute()
                )

                if existe.data:

                    st.warning(
                        "Matéria já existe."
                    )

                else:

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

    st.divider()

    # ==========================================
    # BUSCA
    # ==========================================

    busca = st.text_input(
        "🔍 Buscar matéria"
    )

    if busca:

        materias = [

            m for m in materias

            if busca.upper()
            in m["nome"].upper()
        ]

    # ==========================================
    # LISTA
    # ==========================================

    if not materias:

        st.info(
            "Nenhuma matéria encontrada."
        )

        return

    for materia in materias:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [6, 2, 2]
            )

            # ==========================
            # NOME
            # ==========================

            with col1:

                st.subheader(
                    f"📘 {materia['nome']}"
                )

            # ==========================
            # EDITAR
            # ==========================

            with col2:

                if st.button(
                    "✏️ Editar",
                    key=f"edit_{materia['id']}"
                ):

                    st.session_state[
                        "editar_id"
                    ] = materia["id"]

            # ==========================
            # EXCLUIR
            # ==========================

            with col3:

                if st.button(
                    "🗑️ Excluir",
                    key=f"delete_{materia['id']}"
                ):

                    (
                        supabase
                        .table("concur_materias")
                        .delete()
                        .eq(
                            "id",
                            materia["id"]
                        )
                        .execute()
                    )

                    st.success(
                        "Excluído!"
                    )

                    st.rerun()

            # ==========================
            # ÁREA DE EDIÇÃO
            # ==========================

            if st.session_state.get(
                "editar_id"
            ) == materia["id"]:

                novo_nome = st.text_input(

                    "Novo nome",

                    value=materia["nome"],

                    key=f"novo_{materia['id']}"
                )

                if st.button(

                    "💾 Salvar alteração",

                    key=f"save_{materia['id']}"
                ):

                    (
                        supabase
                        .table("concur_materias")
                        .update({

                            "nome":
                                novo_nome.upper()
                        })
                        .eq(
                            "id",
                            materia["id"]
                        )
                        .execute()
                    )

                    st.success(
                        "Atualizado!"
                    )

                    st.session_state[
                        "editar_id"
                    ] = None

                    st.rerun()