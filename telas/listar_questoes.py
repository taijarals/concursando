import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from utils.logger import get_logger

logger = get_logger(__name__)

def tela_listar_questoes():
    """Display and manage questions."""
    st.title("📚 Banco de Questões")

    try:
        # Fetch questions from database
        response = (
            supabase
            .table("concur_questoes")
            .select("""
                *,
                concur_materias(nome),
                concur_assuntos(nome),
                concur_bancas(nome)
            """)
            .order("id", desc=True)
            .execute()
        )

        questoes = response.data

        if not questoes:
            st.info("📚 Nenhuma questão cadastrada ainda. Comece criando uma nova questão!")
            return

        # Fetch alternatives
        alternativas_response = (
            supabase
            .table("concur_alternativas")
            .select("*")
            .execute()
        )

        alternativas = alternativas_response.data

        # Group alternatives by question
        alternativas_por_questao = {}

        for alt in alternativas:
            questao_id = alt["questao_id"]

            if questao_id not in alternativas_por_questao:
                alternativas_por_questao[questao_id] = []

            alternativas_por_questao[questao_id].append(alt)

        # Create DataFrame
        dados = []

        for q in questoes:
            preview = (
                q["enunciado"][:120] + "..."
                if len(q["enunciado"]) > 120
                else q["enunciado"]
            )

            dados.append({
                "Selecionar": False,
                "ID": q["id"],
                "Tipo": q["tipo"],
                "Matéria": (
                    q["concur_materias"]["nome"]
                    if q["concur_materias"]
                    else "-"
                ),
                "Assunto": (
                    q["concur_assuntos"]["nome"]
                    if q["concur_assuntos"]
                    else "-"
                ),
                "Banca": (
                    q["concur_bancas"]["nome"]
                    if q["concur_bancas"]
                    else "-"
                ),
                "Dificuldade": q["dificuldade"],
                "Questão": preview
            })

        df = pd.DataFrame(dados)

        # Filters
        st.subheader("🔎 Filtros")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            busca = st.text_input("Buscar questão")

        with col2:
            # Safe filter - check if column has data
            materias_unique = df["Matéria"].dropna().unique()
            materias = sorted(materias_unique) if len(materias_unique) > 0 else []
            
            filtro_materia = st.selectbox(
                "Matéria",
                ["Todas"] + materias
            )

        with col3:
            bancas_unique = df["Banca"].dropna().unique()
            bancas = sorted(bancas_unique) if len(bancas_unique) > 0 else []
            
            filtro_banca = st.selectbox(
                "Banca",
                ["Todas"] + bancas
            )

        with col4:
            dificuldades_unique = df["Dificuldade"].dropna().unique()
            dificuldades = sorted(dificuldades_unique) if len(dificuldades_unique) > 0 else []
            
            filtro_dificuldade = st.selectbox(
                "Dificuldade",
                ["Todas"] + dificuldades
            )

        # Apply filters
        if busca:
            df = df[
                df["Questão"]
                .str
                .contains(
                    busca,
                    case=False,
                    na=False
                )
            ]

        if filtro_materia != "Todas":
            df = df[df["Matéria"] == filtro_materia]

        if filtro_banca != "Todas":
            df = df[df["Banca"] == filtro_banca]

        if filtro_dificuldade != "Todas":
            df = df[df["Dificuldade"] == filtro_dificuldade]

        # KPIs
        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Questões", len(df))

        with col2:
            st.metric("Matérias", df["Matéria"].nunique())

        with col3:
            st.metric("Bancas", df["Banca"].nunique())

        st.divider()

        # Select all
        selecionar_todos = st.checkbox("Selecionar todas as questões")

        if selecionar_todos:
            df["Selecionar"] = True

        # Editable table
        st.subheader("📋 Questões")

        edited_df = st.data_editor(
            df,
            hide_index=True,
            width='stretch',
            disabled=[
                "ID",
                "Tipo",
                "Matéria",
                "Assunto",
                "Banca",
                "Dificuldade",
                "Questão"
            ],
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar"),
                "Questão": st.column_config.TextColumn("Questão", width="large")
            }
        )

        # Selected questions
        selecionadas = edited_df[edited_df["Selecionar"] == True]
        ids_selecionados = selecionadas["ID"].tolist()

        # Bulk actions
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"{len(ids_selecionados)} questão(ões) selecionada(s)")

        with col2:
            if st.button(
                "🗑️ Excluir Selecionadas",
                width='stretch',
                disabled=len(ids_selecionados) == 0,
                key="btn_excluir_selecionadas_questoes"
            ):
                try:
                    # Delete alternatives
                    (
                        supabase
                        .table("concur_alternativas")
                        .delete()
                        .in_("questao_id", ids_selecionados)
                        .execute()
                    )

                    # Delete questions
                    (
                        supabase
                        .table("concur_questoes")
                        .delete()
                        .in_("id", ids_selecionados)
                        .execute()
                    )

                    st.success(f"{len(ids_selecionados)} questão(ões) excluída(s)!")
                    st.rerun()

                except Exception as e:
                    logger.error(f"Error deleting questions: {str(e)}")
                    st.error(f"Erro ao excluir: {str(e)}")

        # View question
        st.divider()

        st.subheader("📖 Visualizar Questão")

        lista_ids = edited_df["ID"].tolist()

        if not lista_ids:
            st.warning("Nenhuma questão para visualizar após os filtros.")
            return

        questao_id = st.selectbox("Selecione uma questão", lista_ids)

        try:
            questao = next(q for q in questoes if q["id"] == questao_id)
        except StopIteration:
            st.error("Questão não encontrada.")
            return

        # Display question information
        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Matéria:** "
                f"{questao['concur_materias']['nome'] if questao['concur_materias'] else '-'}"
            )
            st.write(
                f"**Assunto:** "
                f"{questao['concur_assuntos']['nome'] if questao['concur_assuntos'] else '-'}"
            )

        with col2:
            st.write(
                f"**Banca:** "
                f"{questao['concur_bancas']['nome'] if questao['concur_bancas'] else '-'}"
            )
            st.write(f"**Dificuldade:** {questao['dificuldade']}")

        st.divider()

        # Display enunciation
        st.markdown(questao["enunciado"])

        st.divider()

        # Display alternatives
        if questao["tipo"] == "multipla_escolha":
            alts = alternativas_por_questao.get(questao["id"], [])
            alts = sorted(alts, key=lambda x: x["letra"])

            for alt in alts:
                emoji = "✅" if alt["correta"] else "▪️"
                st.write(f"{emoji} **{alt['letra']})** {alt['texto']}")

        else:
            st.success(f"Resposta correta: {questao['resposta_correta']}")

        # AI explanation
        if questao.get("explicacao_ia"):
            st.divider()

            with st.expander("🤖 Explicação IA"):
                st.write(questao["explicacao_ia"])

        # Individual actions
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ Editar Questão", width='stretch', key="btn_editar_questao_individual"):
                st.info("Tela de edição ainda será criada.")

        with col2:
            if st.button("🗑️ Excluir Esta Questão", width='stretch', key="btn_excluir_questao_individual"):
                try:
                    (
                        supabase
                        .table("concur_alternativas")
                        .delete()
                        .eq("questao_id", questao["id"])
                        .execute()
                    )

                    (
                        supabase
                        .table("concur_questoes")
                        .delete()
                        .eq("id", questao["id"])
                        .execute()
                    )

                    st.success("Questão excluída!")
                    st.rerun()

                except Exception as e:
                    logger.error(f"Error deleting question: {str(e)}")
                    st.error(f"Erro ao excluir: {str(e)}")

    except Exception as e:
        logger.error(f"Error in listar_questoes: {str(e)}")
        st.error(f"Erro ao carregar questões: {str(e)}")
