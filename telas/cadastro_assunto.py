import streamlit as st

from database.supabase_client import supabase


# ==================================================
# CADASTRO DE ASSUNTOS
# ==================================================

def tela_cadastro_assunto():

    #st.title("📝 Cadastro de Assuntos")

    # ==================================================
    # BUSCAR MATÉRIAS
    # ==================================================

    materias = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    materias_lista = materias.data

    materias_map = {
        item["nome"]: item["id"]
        for item in materias_lista
    }

    # ==================================================
    # SEM MATÉRIAS
    # ==================================================

    if not materias_lista:

        st.warning(
            "Cadastre uma matéria antes."
        )

        return

    # ==================================================
    # FORMULÁRIO
    # ==================================================

    with st.form("form_assunto"):

        materia_nome = st.selectbox(
            "Matéria",
            list(materias_map.keys())
        )

        nome = st.text_input(
            "Nome do Assunto"
        )

        salvar = st.form_submit_button(
            "Salvar Assunto"
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

            nome = nome.upper().strip()

            materia_id = (
                materias_map[materia_nome]
            )

            # =====================================
            # VERIFICAR DUPLICIDADE
            # =====================================

            existe = (
                supabase
                .table("concur_assuntos")
                .select("*")
                .eq(
                    "materia_id",
                    materia_id
                )
                .eq(
                    "nome",
                    nome
                )
                .execute()
            )

            if existe.data:

                st.warning(
                    "Assunto já cadastrado nessa matéria."
                )

                return

            # =====================================
            # INSERT
            # =====================================

            (
                supabase
                .table("concur_assuntos")
                .insert({

                    "materia_id":
                        materia_id,

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

    # ==================================================
    # LISTA
    # ==================================================

    st.divider()

    st.subheader(
        "📋 Assuntos cadastrados"
    )

    response = (
        supabase
        .table("concur_assuntos")
        .select("""
            id,
            nome,
            materia_id,
            concur_materias(nome)
        """)
        .order("nome")
        .execute()
    )

    assuntos = response.data

    # ==================================================
    # SEM DADOS
    # ==================================================

    if not assuntos:

        st.info(
            "Nenhum assunto cadastrado."
        )

        return

    # ==================================================
    # LOOP
    # ==================================================

    for assunto in assuntos:

        with st.container():

            col1, col2, col3, col4 = st.columns(
                [4, 4, 2, 2]
            )

            # =====================================
            # MATÉRIA
            # =====================================

            with col1:

                materia_atual_id = (
                    assunto["materia_id"]
                )

                materia_atual_nome = None

                for nome_materia, id_materia in materias_map.items():

                    if id_materia == materia_atual_id:

                        materia_atual_nome = nome_materia
                        break

                nova_materia = st.selectbox(

                    "Matéria",

                    list(materias_map.keys()),

                    index=list(
                        materias_map.keys()
                    ).index(
                        materia_atual_nome
                    ),

                    key=f"materia_{assunto['id']}"
                )

            # =====================================
            # NOME
            # =====================================

            with col2:

                novo_nome = st.text_input(

                    "Assunto",

                    value=assunto["nome"],

                    key=f"assunto_{assunto['id']}"
                )

            # =====================================
            # EDITAR
            # =====================================

            with col3:

                st.write("")
                st.write("")

                if st.button(

                    "💾 Salvar",

                    key=f"save_{assunto['id']}"
                ):

                    try:

                        novo_nome = (
                            novo_nome
                            .upper()
                            .strip()
                        )

                        nova_materia_id = (
                            materias_map[
                                nova_materia
                            ]
                        )

                        if not novo_nome:

                            st.warning(
                                "Nome inválido."
                            )

                            st.stop()

                        # =========================
                        # DUPLICIDADE
                        # =========================

                        existe = (
                            supabase
                            .table(
                                "concur_assuntos"
                            )
                            .select("*")
                            .eq(
                                "materia_id",
                                nova_materia_id
                            )
                            .eq(
                                "nome",
                                novo_nome
                            )
                            .neq(
                                "id",
                                assunto["id"]
                            )
                            .execute()
                        )

                        if existe.data:

                            st.warning(
                                "Já existe esse assunto nessa matéria."
                            )

                            st.stop()

                        # =========================
                        # UPDATE
                        # =========================

                        (
                            supabase
                            .table(
                                "concur_assuntos"
                            )
                            .update({

                                "materia_id":
                                    nova_materia_id,

                                "nome":
                                    novo_nome
                            })
                            .eq(
                                "id",
                                assunto["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Assunto atualizado!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            # =====================================
            # DELETE
            # =====================================

            with col4:

                st.write("")
                st.write("")

                if st.button(

                    "🗑️ Excluir",

                    key=f"delete_{assunto['id']}"
                ):

                    try:

                        # =========================
                        # VERIFICAR QUESTÕES
                        # =========================

                        questoes = (
                            supabase
                            .table(
                                "concur_questoes"
                            )
                            .select("id")
                            .eq(
                                "assunto_id",
                                assunto["id"]
                            )
                            .execute()
                        )

                        if questoes.data:

                            st.warning(

                                "Não é possível excluir "
                                "esse assunto porque "
                                "existem questões vinculadas."
                            )

                            st.stop()

                        # =========================
                        # DELETE
                        # =========================

                        (
                            supabase
                            .table(
                                "concur_assuntos"
                            )
                            .delete()
                            .eq(
                                "id",
                                assunto["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Assunto excluído!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            st.divider()