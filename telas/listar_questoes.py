import streamlit as st

from database.supabase_client import supabase


# ==================================================
# LISTAR QUESTÕES
# ==================================================

def tela_listar_questoes():

    st.title("📚 Questões Cadastradas")

    # ==================================================
    # FILTROS
    # ==================================================

    busca = st.text_input(
        "Buscar questão"
    )

    # ==================================================
    # BUSCAR QUESTÕES
    # ==================================================

    response = (
        supabase
        .table("concur_questoes")
        .select("""
            *,
            concur_materias(nome),
            concur_assuntos(nome),
            concur_bancas(nome)
        """)
        .order(
            "id",
            desc=True
        )
        .execute()
    )

    questoes = response.data

    # ==================================================
    # FILTRO TEXTO
    # ==================================================

    if busca:

        questoes = [

            q for q in questoes

            if busca.lower()
            in q["enunciado"].lower()
        ]

    st.write(
        f"Total: {len(questoes)} questões"
    )

    # ==================================================
    # LOOP QUESTÕES
    # ==================================================

    for questao in questoes:

        titulo = (
            f"#{questao['id']} "
            f"- {questao['tipo']}"
        )

        with st.expander(titulo):

            # =====================================
            # INFO
            # =====================================

            st.write(
                f"**Matéria:** "
                f"{questao['concur_materias']['nome']}"
            )

            st.write(
                f"**Assunto:** "
                f"{questao['concur_assuntos']['nome']}"
            )

            st.write(
                f"**Banca:** "
                f"{questao['concur_bancas']['nome']}"
            )

            st.write(
                f"**Dificuldade:** "
                f"{questao['dificuldade']}"
            )

            st.divider()

            # =====================================
            # ENUNCIADO
            # =====================================

            st.markdown(
                questao["enunciado"]
            )

            # =====================================
            # ALTERNATIVAS
            # =====================================

            if (
                questao["tipo"]
                == "multipla_escolha"
            ):

                alternativas = (
                    supabase
                    .table(
                        "concur_alternativas"
                    )
                    .select("*")
                    .eq(
                        "questao_id",
                        questao["id"]
                    )
                    .order("letra")
                    .execute()
                )

                for alt in alternativas.data:

                    emoji = (
                        "✅"
                        if alt["correta"]
                        else "▪️"
                    )

                    st.write(
                        f"{emoji} "
                        f"{alt['letra']}) "
                        f"{alt['texto']}"
                    )

            else:

                st.write(
                    "**Resposta:** "
                    f"{questao['resposta_correta']}"
                )

            # =====================================
            # EXPLICAÇÃO IA
            # =====================================

            if questao["explicacao_ia"]:

                with st.expander(
                    "🤖 Explicação IA"
                ):

                    st.write(
                        questao["explicacao_ia"]
                    )

            st.divider()

            # =====================================
            # BOTÕES
            # =====================================

            col1, col2 = st.columns(2)

            # =====================================
            # EXCLUIR
            # =====================================

            with col1:

                if st.button(
                    "🗑️ Excluir",
                    key=f"del_{questao['id']}"
                ):

                    try:

                        # deletar alternativas
                        (
                            supabase
                            .table(
                                "concur_alternativas"
                            )
                            .delete()
                            .eq(
                                "questao_id",
                                questao["id"]
                            )
                            .execute()
                        )

                        # deletar questão
                        (
                            supabase
                            .table(
                                "concur_questoes"
                            )
                            .delete()
                            .eq(
                                "id",
                                questao["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "Questão excluída!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            # =====================================
            # EDITAR
            # =====================================

            with col2:

                if st.button(
                    "✏️ Editar",
                    key=f"edit_{questao['id']}"
                ):

                    st.info(
                        "Tela de edição ainda será criada."
                    )