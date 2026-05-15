import streamlit as st

from database.supabase_client import supabase


# ==================================================
# CADASTRO DE MATÉRIAS
# ==================================================

def tela_cadastro_materia():

    st.title("📚 Cadastro de Matérias")

    # ==================================================
    # NOVA MATÉRIA
    # ==================================================

    with st.form("form_materia"):

        nome = st.text_input(
            "Nome da Matéria"
        )

        salvar = st.form_submit_button(
            "Salvar Matéria"
        )

    # ==================================================
    # SALVAR
    # ==================================================

    if salvar:

        if not nome:

            st.warning(
                "Informe o nome."
            )

            return

        try:

            # =====================================
            # CAIXA ALTA
            # =====================================

            nome = nome.upper().strip()

            # =====================================
            # VERIFICAR DUPLICIDADE
            # =====================================

            existe = (
                supabase
                .table("concur_materias")
                .select("*")
                .eq("nome", nome)
                .execute()
            )

            if existe.data:

                st.warning(
                    "Matéria já cadastrada."
                )

                return

            # =====================================
            # INSERT
            # =====================================

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

        except Exception as e:

            st.error(str(e))

    # ==================================================
    # LISTA
    # ==================================================

    st.divider()

    st.subheader(
        "📋 Matérias cadastradas"
    )

    response = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    materias = response.data

    # ==================================================
    # SEM DADOS
    # ==================================================

    if not materias:

        st.info(
            "Nenhuma matéria cadastrada."
        )

        return

    # ==================================================
    # LOOP
    # ==================================================

    for materia in materias:

        with st.container():

            col1, col2, col3 = st.columns(
                [8, 2, 2]
            )

            # =====================================
            # NOME
            # =====================================

            with col1:

                novo_nome = st.text_input(

                    f"Matéria {materia['id']}",

                    value=materia["nome"],

                    key=f"materia_{materia['id']}"
                )

            # =====================================
            # EDITAR
            # =====================================

            with col2:

                st.write("")

                if st.button(

                    "💾 Salvar",

                    key=f"save_{materia['id']}"
                ):

                    try:

                        novo_nome = (
                            novo_nome
                            .upper()
                            .strip()
                        )

                        if not novo_nome:

                            st.warning(
                                "Nome inválido."
                            )

                            st.stop()

                        # =========================
                        # VERIFICAR DUPLICIDADE
                        # =========================

                        existe = (
                            supabase
                            .table(
                                "concur_materias"
                            )
                            .select("*")
                            .eq(
                                "nome",
                                novo_nome
                            )
                            .neq(
                                "id",
                                materia["id"]
                            )
                            .execute()
                        )

                        if existe.data:

                            st.warning(
                                "Já existe uma matéria com esse nome."
                            )

                            st.stop()

                        # =========================
                        # UPDATE
                        # =========================

                        (
                            supabase
                            .table(
                                "concur_materias"
                            )
                            .update({

                                "nome":
                                    novo_nome
                            })
                            .eq(
                                "id",
                                materia["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Matéria atualizada!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            # =====================================
            # DELETE
            # =====================================

            with col3:

                st.write("")

                if st.button(

                    "🗑️ Excluir",

                    key=f"delete_{materia['id']}"
                ):

                    try:

                        # =========================
                        # VERIFICAR ASSUNTOS
                        # =========================

                        assuntos = (

                            supabase
                            .table(
                                "concur_assuntos"
                            )
                            .select("id")
                            .eq(
                                "materia_id",
                                materia["id"]
                            )
                            .execute()
                        )

                        if assuntos.data:

                            st.warning(

                                "Não é possível excluir "
                                "essa matéria porque "
                                "existem assuntos vinculados."
                            )

                            st.stop()

                        # =========================
                        # DELETE
                        # =========================

                        (
                            supabase
                            .table(
                                "concur_materias"
                            )
                            .delete()
                            .eq(
                                "id",
                                materia["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Matéria excluída!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            st.divider()