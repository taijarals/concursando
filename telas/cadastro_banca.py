import streamlit as st

from database.supabase_client import supabase


# ==================================================
# CADASTRO DE BANCAS
# ==================================================

def tela_cadastro_banca():

    #st.title("🏛️ Cadastro de Bancas")

    # ==================================================
    # FORMULÁRIO
    # ==================================================

    with st.form("form_banca"):

        nome = st.text_input(
            "Nome da Banca"
        )

        salvar = st.form_submit_button(
            "Salvar Banca"
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
                .table("concur_bancas")
                .select("*")
                .eq("nome", nome)
                .execute()
            )

            if existe.data:

                st.warning(
                    "Banca já cadastrada."
                )

                return

            # =====================================
            # INSERT
            # =====================================

            (
                supabase
                .table("concur_bancas")
                .insert({
                    "nome": nome
                })
                .execute()
            )

            st.success(
                "Banca cadastrada!"
            )

            st.rerun()

        except Exception as e:

            st.error(str(e))

    # ==================================================
    # LISTA
    # ==================================================

    st.divider()

    st.subheader(
        "📋 Bancas cadastradas"
    )

    response = (
        supabase
        .table("concur_bancas")
        .select("*")
        .order("nome")
        .execute()
    )

    bancas = response.data

    # ==================================================
    # SEM DADOS
    # ==================================================

    if not bancas:

        st.info(
            "Nenhuma banca cadastrada."
        )

        return

    # ==================================================
    # LOOP
    # ==================================================

    for banca in bancas:

        with st.container():

            col1, col2, col3 = st.columns(
                [8, 2, 2]
            )

            # =====================================
            # NOME
            # =====================================

            with col1:

                novo_nome = st.text_input(

                    f"Banca {banca['id']}",

                    value=banca["nome"],

                    key=f"banca_{banca['id']}"
                )

            # =====================================
            # EDITAR
            # =====================================

            with col2:

                st.write("")
                st.write("")

                if st.button(

                    "💾 Salvar",

                    key=f"save_{banca['id']}"
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
                                "concur_bancas"
                            )
                            .select("*")
                            .eq(
                                "nome",
                                novo_nome
                            )
                            .neq(
                                "id",
                                banca["id"]
                            )
                            .execute()
                        )

                        if existe.data:

                            st.warning(
                                "Já existe uma banca com esse nome."
                            )

                            st.stop()

                        # =========================
                        # UPDATE
                        # =========================

                        (
                            supabase
                            .table(
                                "concur_bancas"
                            )
                            .update({

                                "nome":
                                    novo_nome
                            })
                            .eq(
                                "id",
                                banca["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Banca atualizada!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            # =====================================
            # DELETE
            # =====================================

            with col3:

                st.write("")
                st.write("")

                if st.button(

                    "🗑️ Excluir",

                    key=f"delete_{banca['id']}"
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
                                "banca_id",
                                banca["id"]
                            )
                            .execute()
                        )

                        if questoes.data:

                            st.warning(

                                "Não é possível excluir "
                                "essa banca porque "
                                "existem questões vinculadas."
                            )

                            st.stop()

                        # =========================
                        # DELETE
                        # =========================

                        (
                            supabase
                            .table(
                                "concur_bancas"
                            )
                            .delete()
                            .eq(
                                "id",
                                banca["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Banca excluída!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            st.divider()