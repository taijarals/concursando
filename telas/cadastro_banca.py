import streamlit as st
import pandas as pd

from database.supabase_client import supabase


# ==================================================
# CADASTRO DE BANCAS
# ==================================================

def tela_cadastro_banca():

    st.title("🏛️ Cadastro de Bancas")

    # ==================================================
    # NOVA BANCA
    # ==================================================

    st.subheader("➕ Nova Banca")

    with st.form("form_banca"):

        nome = st.text_input(
            "Nome da banca"
        )

        salvar = st.form_submit_button(
            "Salvar Banca"
        )

    # ==================================================
    # SALVAR
    # ==================================================

    if salvar:

        try:

            nome = nome.upper().strip()

            if not nome:

                st.warning(
                    "Informe o nome."
                )

                st.stop()

            # ==========================================
            # DUPLICIDADE
            # ==========================================

            existe = (
                supabase
                .table("concur_bancas")
                .select("id")
                .eq(
                    "nome",
                    nome
                )
                .execute()
            )

            if existe.data:

                st.warning(
                    "Essa banca já existe."
                )

                st.stop()

            # ==========================================
            # INSERT
            # ==========================================

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

    st.divider()

    # ==================================================
    # BUSCAR BANCAS
    # ==================================================

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
    # CONTAR QUESTÕES
    # ==================================================

    questoes_response = (
        supabase
        .table("concur_questoes")
        .select("id, banca_id")
        .execute()
    )

    questoes = questoes_response.data

    contagem_questoes = {}

    for q in questoes:

        banca_id = q["banca_id"]

        if banca_id not in contagem_questoes:

            contagem_questoes[
                banca_id
            ] = 0

        contagem_questoes[
            banca_id
        ] += 1

    # ==================================================
    # DATAFRAME
    # ==================================================

    dados = []

    for banca in bancas:

        dados.append({

            "Selecionar": False,

            "ID": banca["id"],

            "Banca": banca["nome"],

            "Questões": contagem_questoes.get(
                banca["id"],
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
        "Buscar banca"
    )

    # ==================================================
    # APLICAR FILTRO
    # ==================================================

    if busca:

        df = df[
            df["Banca"]
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

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Bancas",
            len(df)
        )

    with col2:

        st.metric(
            "Questões Vinculadas",
            df["Questões"].sum()
        )

    st.divider()

    # ==================================================
    # SELECIONAR TODOS
    # ==================================================

    selecionar_todos = st.checkbox(
        "Selecionar todas",
        key="selecionar_todas_bancas"
    )

    if selecionar_todos:

        df["Selecionar"] = True

    # ==================================================
    # TABELA EDITÁVEL
    # ==================================================

    st.subheader(
        "📋 Bancas Cadastradas"
    )

    edited_df = st.data_editor(

        df,

        hide_index=True,

        width='stretch',

        num_rows="fixed",

        column_config={

            "Selecionar": st.column_config.CheckboxColumn(
                "Selecionar"
            ),

            "ID": st.column_config.NumberColumn(
                "ID",
                disabled=True
            ),

            "Banca": st.column_config.TextColumn(
                "Banca",
                required=True
            ),

            "Questões": st.column_config.NumberColumn(
                "Questões",
                disabled=True
            )
        },

        disabled=[
            "ID",
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
            width='stretch',
            key="salvar_alteracoes_banca"
        ):

            try:

                atualizados = 0

                for _, linha_editada in edited_df.iterrows():

                    id_banca = linha_editada["ID"]

                    linha_original = (
                        df_original[
                            df_original["ID"]
                            == id_banca
                        ]
                        .iloc[0]
                    )

                    mudou = (
                        linha_editada["Banca"]
                        != linha_original["Banca"]
                    )

                    if not mudou:

                        continue

                    novo_nome = (
                        linha_editada["Banca"]
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
                        .table("concur_bancas")
                        .select("id")
                        .eq(
                            "nome",
                            novo_nome
                        )
                        .neq(
                            "id",
                            id_banca
                        )
                        .execute()
                    )

                    if existe.data:

                        st.warning(
                            f"A banca "
                            f"{novo_nome} "
                            f"já existe."
                        )

                        continue

                    # ==============================
                    # UPDATE
                    # ==============================

                    (
                        supabase
                        .table("concur_bancas")
                        .update({

                            "nome":
                                novo_nome
                        })
                        .eq(
                            "id",
                            id_banca
                        )
                        .execute()
                    )

                    atualizados += 1

                st.success(
                    f"{atualizados} "
                    f"banca(s) atualizada(s)!"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    # ==================================================
    # EXCLUIR SELECIONADOS
    # ==================================================

    with col2:

        if st.button(
            "🗑️ Excluir Selecionados",
            width='stretch',
            disabled=len(ids_selecionados) == 0,
            key="excluir_selecionados_banca"
        ):

            try:

                bloqueados = []

                permitidos = []

                # ======================================
                # VALIDAR VÍNCULOS
                # ======================================

                for banca_id in ids_selecionados:

                    qtd = contagem_questoes.get(
                        banca_id,
                        0
                    )

                    if qtd > 0:

                        bloqueados.append(
                            banca_id
                        )

                    else:

                        permitidos.append(
                            banca_id
                        )

                # ======================================
                # BLOQUEADOS
                # ======================================

                if bloqueados:

                    st.warning(
                        f"{len(bloqueados)} "
                        f"banca(s) não puderam "
                        f"ser excluídas porque "
                        f"possuem questões vinculadas."
                    )

                # ======================================
                # DELETE
                # ======================================

                if permitidos:

                    (
                        supabase
                        .table("concur_bancas")
                        .delete()
                        .in_(
                            "id",
                            permitidos
                        )
                        .execute()
                    )

                    st.success(
                        f"{len(permitidos)} "
                        f"banca(s) excluída(s)!"
                    )

                    st.rerun()

            except Exception as e:

                st.error(str(e))