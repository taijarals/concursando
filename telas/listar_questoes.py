import streamlit as st
import pandas as pd

from database.supabase_client import supabase


# ==================================================
# LISTAR QUESTÕES
# ==================================================

def tela_listar_questoes():

    st.title("📚 Banco de Questões")

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
        .order("id", desc=True)
        .execute()
    )

    questoes = response.data

    # ==================================================
    # BUSCAR TODAS AS ALTERNATIVAS
    # ==================================================

    alternativas_response = (
        supabase
        .table("concur_alternativas")
        .select("*")
        .execute()
    )

    alternativas = alternativas_response.data

    # ==================================================
    # AGRUPAR ALTERNATIVAS POR QUESTÃO
    # ==================================================

    alternativas_por_questao = {}

    for alt in alternativas:

        questao_id = alt["questao_id"]

        if questao_id not in alternativas_por_questao:
            alternativas_por_questao[questao_id] = []

        alternativas_por_questao[questao_id].append(alt)

    # ==================================================
    # TRANSFORMAR EM DATAFRAME
    # ==================================================

    dados = []

    for q in questoes:

        enunciado_preview = (
            q["enunciado"][:120] + "..."
            if len(q["enunciado"]) > 120
            else q["enunciado"]
        )

        dados.append({

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

            "Questão": enunciado_preview
        })

    df = pd.DataFrame(dados)

    # ==================================================
    # FILTROS
    # ==================================================

    st.subheader("🔎 Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        busca = st.text_input(
            "Buscar texto"
        )

    with col2:

        materias = sorted(
            df["Matéria"].dropna().unique()
        )

        filtro_materia = st.selectbox(
            "Matéria",
            ["Todas"] + materias
        )

    with col3:

        bancas = sorted(
            df["Banca"].dropna().unique()
        )

        filtro_banca = st.selectbox(
            "Banca",
            ["Todas"] + bancas
        )

    with col4:

        dificuldades = sorted(
            df["Dificuldade"].dropna().unique()
        )

        filtro_dificuldade = st.selectbox(
            "Dificuldade",
            ["Todas"] + dificuldades
        )

    # ==================================================
    # APLICAR FILTROS
    # ==================================================

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

        df = df[
            df["Matéria"]
            == filtro_materia
        ]

    if filtro_banca != "Todas":

        df = df[
            df["Banca"]
            == filtro_banca
        ]

    if filtro_dificuldade != "Todas":

        df = df[
            df["Dificuldade"]
            == filtro_dificuldade
        ]

    # ==================================================
    # KPIs
    # ==================================================

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Questões",
            len(df)
        )

    with col2:

        st.metric(
            "Matérias",
            df["Matéria"].nunique()
        )

    with col3:

        st.metric(
            "Bancas",
            df["Banca"].nunique()
        )

    st.divider()

    # ==================================================
    # TABELA
    # ==================================================

    st.subheader("📋 Lista de Questões")

    if len(df) == 0:

        st.warning(
            "Nenhuma questão encontrada."
        )

        return

    questao_selecionada = st.selectbox(
        "Selecione uma questão",
        df["ID"].tolist(),
        format_func=lambda x: (
            f"#{x} - "
            f"{df[df['ID'] == x]['Matéria'].iloc[0]} - "
            f"{df[df['ID'] == x]['Questão'].iloc[0][:60]}"
        )
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==================================================
    # DETALHES DA QUESTÃO
    # ==================================================

    questao = next(
        q for q in questoes
        if q["id"] == questao_selecionada
    )

    st.subheader(
        f"📖 Questão #{questao['id']}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Matéria:** "
            f"{questao['concur_materias']['nome']}"
        )

        st.write(
            f"**Assunto:** "
            f"{questao['concur_assuntos']['nome']}"
        )

    with col2:

        st.write(
            f"**Banca:** "
            f"{questao['concur_bancas']['nome']}"
        )

        st.write(
            f"**Dificuldade:** "
            f"{questao['dificuldade']}"
        )

    st.divider()

    # ==================================================
    # ENUNCIADO
    # ==================================================

    st.markdown(
        questao["enunciado"]
    )

    st.divider()

    # ==================================================
    # ALTERNATIVAS
    # ==================================================

    if questao["tipo"] == "multipla_escolha":

        alts = alternativas_por_questao.get(
            questao["id"],
            []
        )

        alts = sorted(
            alts,
            key=lambda x: x["letra"]
        )

        for alt in alts:

            emoji = (
                "✅"
                if alt["correta"]
                else "▪️"
            )

            st.write(
                f"{emoji} "
                f"**{alt['letra']})** "
                f"{alt['texto']}"
            )

    else:

        st.success(
            f"Resposta correta: "
            f"{questao['resposta_correta']}"
        )

    # ==================================================
    # EXPLICAÇÃO IA
    # ==================================================

    if questao["explicacao_ia"]:

        st.divider()

        with st.expander(
            "🤖 Explicação IA",
            expanded=False
        ):

            st.write(
                questao["explicacao_ia"]
            )

    st.divider()

    # ==================================================
    # AÇÕES
    # ==================================================

    col1, col2 = st.columns(2)

    # ==================================================
    # EXCLUIR
    # ==================================================

    with col1:

        if st.button(
            "🗑️ Excluir Questão",
            use_container_width=True
        ):

            try:

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
                    "Questão excluída com sucesso!"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    # ==================================================
    # EDITAR
    # ==================================================

    with col2:

        if st.button(
            "✏️ Editar Questão",
            use_container_width=True
        ):

            st.info(
                "Tela de edição ainda será criada."
            )