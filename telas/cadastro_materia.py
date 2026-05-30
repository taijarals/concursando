import pandas as pd
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

    st.subheader("➕ Nova Matéria")

    with st.form("form_materia"):

        nome = st.text_input(
            "Nome da matéria"
        )

        salvar = st.form_submit_button(
            "Salvar Matéria"
        )

    # ==================================================
    # SALVAR
    # ==================================================

    if salvar:

        try:

            nome = nome.upper().strip()

            if not nome:

                st.warning(
                    "Informe o nome da matéria."
                )

                st.stop()

            # ==========================================
            # DUPLICIDADE
            # ==========================================

            existe = (
                supabase
                .table("concur_materias")
                .select("id")
                .eq(
                    "nome",
                    nome
                )
                .execute()
            )

            if existe.data:

                st.warning(
                    "Essa matéria já existe."
                )

                st.stop()

            # ==========================================
            # INSERT
            # ==========================================

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

    st.divider()

    # ==================================================
    # BUSCAR MATÉRIAS
    # ==================================================

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
    # CONTAR QUESTÕES
    # ==================================================

    questoes_response = (
        supabase
        .table("concur_questoes")
        .select("id, materia_id")
        .execute()
    )

    questoes = questoes_response.data

    contagem_questoes = {}

    for q in questoes:

        materia_id = q["materia_id"]

        if materia_id not in contagem_questoes:

            contagem_questoes[
                materia_id
            ] = 0

        contagem_questoes[
            materia_id
        ] += 1

    # ==================================================
    # CONTAR ASSUNTOS
    # ==================================================

    assuntos_response = (
        supabase
        .table("concur_assuntos")
        .select("id, materia_id")
        .execute()
    )

    assuntos = assuntos_response.data

    contagem_assuntos = {}

    for a in assuntos:

        materia_id = a["materia_id"]

        if materia_id not in contagem_assuntos:

            contagem_assuntos[
                materia_id
            ] = 0

        contagem_assuntos[
            materia_id
        ] += 1

    # ==================================================
    # DATAFRAME
    # ==================================================

    dados = []

    for materia in materias:

        dados.append({

            "Selecionar": False,

            "ID": materia["id"],

            "Matéria": materia["nome"],

            "Assuntos": contagem_assuntos.get(
                materia["id"],
                0
            ),

            "Questões": contagem_questoes.get(
                materia["id"],
                0
            )
        })

    df_original = pd.DataFrame(dados)

    df = df_original.copy()

    # ==================================================
    # FILTROS
    # ==================================================

    st.subheader("🔎 Filtros")

    busca = st.text_input(
        "Buscar matéria"
    )

    # ==================================================
    # APLICAR FILTRO
    # ==================================================

    if busca:

        df = df[
            df["Matéria"]
            .str
            .contains(
                busca,
                case=False,
                na=False
            )
        ]

    # ==================================================
    # KPIs
    # ==================================================

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Matérias",
            len(df)
        )

    with col2:

        st.metric(
            "Assuntos",
            df["Assuntos"].sum()
        )

    with col3:

        st.metric(
            "Questões",
            df["Questões"].sum()
        )

    st.divider()

    # ==================================================
    # SELECIONAR TODOS
    # ==================================================

    selecionar_todos = st.checkbox(
        "Selecionar todas"
    )

    if selecionar_todos:

        df["Selecionar"] = True

    # ==================================================
    # TABELA EDITÁVEL
    # ==================================================

    st.subheader(
        "📋 Matérias Cadastradas"
    )

    edited_df = st.data_editor(

        df,

        hide_index=True,

        width='stretch,

        num_rows="fixed",

        column_config={

            "Selecionar": st.column_config.CheckboxColumn(
                "Selecionar"
            ),

            "ID": st.column_config.NumberColumn(
                "ID",
                disabled=True
            ),

            "Matéria": st.column_config.TextColumn(
                "Matéria",
                required=True
            ),

            "Assuntos": st.column_config.NumberColumn(
                "Assuntos",
                disabled=True
            ),

            "Questões": st.column_config.NumberColumn(
                "Questões",
                disabled=True
            )
        },

        disabled=[
            "ID",
            "Assuntos",
            "Questões"
        ]
    )

    # ==================================================
    # SELECIONADOS
    # ==================================================

    selecionados = edited_df[
        edited_df["Selecionar"] == True
    ]

    ids_selecionados = (
        selecionados["ID"]
        .tolist()
    )

    st.divider()

    # ==================================================
    # AÇÕES
    # ==================================================

    col1, col2 = st.columns(2)

    # ==================================================
    # SALVAR ALTERAÇÕES
    # ==================================================

    with col1:

        if st.button(
            "💾 Salvar Alterações",
            width='stretch
        ):

            try:

                atualizados = 0

                for _, linha_editada in edited_df.iterrows():

                    id_materia = linha_editada["ID"]

                    linha_original = (
                        df_original[
                            df_original["ID"]
                            == id_materia
                        ]
                        .iloc[0]
                    )

                    mudou = (
                        linha_editada["Matéria"]
                        != linha_original["Matéria"]
                    )

                    if not mudou:

                        continue

                    novo_nome = (
                        linha_editada["Matéria"]
                        .upper()
                        .strip()
                    )

                    if not novo_nome:

                        continue

                    # ==============================
                    # DUPLICIDADE
                    # ==============================

                    existe = (
                        supabase
                        .table("concur_materias")
                        .select("id")
                        .eq(
                            "nome",
                            novo_nome
                        )
                        .neq(
                            "id",
                            id_materia
                        )
                        .execute()
                    )

                    if existe.data:

                        st.warning(
                            f"A matéria "
                            f"{novo_nome} "
                            f"já existe."
                        )

                        continue

                    # ==============================
                    # UPDATE
                    # ==============================

                    (
                        supabase
                        .table("concur_materias")
                        .update({

                            "nome":
                                novo_nome
                        })
                        .eq(
                            "id",
                            id_materia
                        )
                        .execute()
                    )

                    atualizados += 1

                st.success(
                    f"{atualizados} "
                    f"matéria(s) atualizada(s)!"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    # ==================================================
    # EXCLUIR SELECIONADOS
    # ==================================================

    with col2:

        if st.button(
            "🗑️ Excluir Selecionadas",
            width='stretch,
            disabled=len(ids_selecionados) == 0
        ):

            try:

                bloqueados = []

                permitidos = []

                # ======================================
                # VALIDAR VÍNCULOS
                # ======================================

                for materia_id in ids_selecionados:

                    qtd_assuntos = (
                        contagem_assuntos.get(
                            materia_id,
                            0
                        )
                    )

                    qtd_questoes = (
                        contagem_questoes.get(
                            materia_id,
                            0
                        )
                    )

                    if (
                        qtd_assuntos > 0
                        or
                        qtd_questoes > 0
                    ):

                        bloqueados.append(
                            materia_id
                        )

                    else:

                        permitidos.append(
                            materia_id
                        )

                # ======================================
                # BLOQUEADOS
                # ======================================

                if bloqueados:

                    st.warning(
                        f"{len(bloqueados)} "
                        f"matéria(s) não puderam "
                        f"ser excluídas porque "
                        f"possuem vínculos."
                    )

                # ======================================
                # DELETE
                # ======================================

                if permitidos:

                    (
                        supabase
                        .table("concur_materias")
                        .delete()
                        .in_(
                            "id",
                            permitidos
                        )
                        .execute()
                    )

                    st.success(
                        f"{len(permitidos)} "
                        f"matéria(s) excluída(s)!"
                    )

                    st.rerun()

            except Exception as e:

                st.error(str(e))