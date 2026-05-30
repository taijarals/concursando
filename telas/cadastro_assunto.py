import streamlit as st
import pandas as pd

from database.supabase_client import supabase


# ==================================================
# CADASTRO DE ASSUNTOS
# ==================================================

def tela_cadastro_assunto():

    st.title("📝 Cadastro de Assuntos")

    # ==================================================
    # BUSCAR MATÉRIAS
    # ==================================================

    materias_response = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    materias_lista = materias_response.data

    # ==================================================
    # SEM MATÉRIAS
    # ==================================================

    if not materias_lista:

        st.warning(
            "Cadastre uma matéria antes."
        )

        return

    # ==================================================
    # MAPAS
    # ==================================================

    materias_map = {

        item["id"]: item["nome"]

        for item in materias_lista
    }

    materias_nome_para_id = {

        item["nome"]: item["id"]

        for item in materias_lista
    }

    # ==================================================
    # FORMULÁRIO NOVO ASSUNTO
    # ==================================================

    st.subheader("➕ Novo Assunto")

    with st.form("form_novo_assunto"):

        col1, col2 = st.columns([2, 4])

        with col1:

            materia_nome = st.selectbox(
                "Matéria",
                list(materias_nome_para_id.keys())
            )

        with col2:

            nome = st.text_input(
                "Nome do Assunto"
            )

        salvar = st.form_submit_button(
            "Salvar Assunto"
        )

    # ==================================================
    # SALVAR NOVO ASSUNTO
    # ==================================================

    if salvar:

        try:

            nome = nome.upper().strip()

            if not nome:

                st.warning(
                    "Informe o nome."
                )

                st.stop()

            materia_id = (
                materias_nome_para_id[
                    materia_nome
                ]
            )

            # ==========================================
            # DUPLICIDADE
            # ==========================================

            existe = (
                supabase
                .table("concur_assuntos")
                .select("id")
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
                    "Esse assunto já existe nessa matéria."
                )

                st.stop()

            # ==========================================
            # INSERT
            # ==========================================

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

    st.divider()

    # ==================================================
    # BUSCAR ASSUNTOS
    # ==================================================

    assuntos_response = (
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

    assuntos = assuntos_response.data

    # ==================================================
    # SEM DADOS
    # ==================================================

    if not assuntos:

        st.info(
            "Nenhum assunto cadastrado."
        )

        return

    # ==================================================
    # CONTAR QUESTÕES
    # ==================================================

    questoes_response = (
        supabase
        .table("concur_questoes")
        .select("id, assunto_id")
        .execute()
    )

    questoes = questoes_response.data

    contagem_questoes = {}

    for q in questoes:

        assunto_id = q["assunto_id"]

        if assunto_id not in contagem_questoes:

            contagem_questoes[
                assunto_id
            ] = 0

        contagem_questoes[
            assunto_id
        ] += 1

    # ==================================================
    # DATAFRAME
    # ==================================================

    dados = []

    for assunto in assuntos:

        dados.append({

            "Selecionar": False,

            "ID": assunto["id"],

            "Matéria": (
                assunto["concur_materias"]["nome"]
                if assunto["concur_materias"]
                else "-"
            ),

            "Assunto": assunto["nome"],

            "Questões": contagem_questoes.get(
                assunto["id"],
                0
            )
        })

    df_original = pd.DataFrame(dados)

    df = df_original.copy()

    # ==================================================
    # FILTROS
    # ==================================================

    st.subheader("🔎 Filtros")

    col1, col2 = st.columns(2)

    with col1:

        busca = st.text_input(
            "Buscar assunto"
        )

    with col2:

        lista_materias = sorted(
            df["Matéria"]
            .dropna()
            .unique()
        )

        filtro_materia = st.selectbox(
            "Filtrar por matéria",
            ["Todas"] + list(lista_materias)
        )

    # ==================================================
    # APLICAR FILTROS
    # ==================================================

    if busca:

        df = df[
            df["Assunto"]
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

    # ==================================================
    # KPIs
    # ==================================================

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Assuntos",
            len(df)
        )

    with col2:

        st.metric(
            "Matérias",
            df["Matéria"].nunique()
        )

    with col3:

        st.metric(
            "Questões Vinculadas",
            df["Questões"].sum()
        )

    st.divider()

    # ==================================================
    # SELECIONAR TODOS
    # ==================================================

    selecionar_todos = st.checkbox(
        "Selecionar todos"
    )

    if selecionar_todos:

        df["Selecionar"] = True

    # ==================================================
    # TABELA EDITÁVEL
    # ==================================================

    st.subheader(
        "📋 Assuntos Cadastrados"
    )

    edited_df = st.data_editor(

        df,

        hide_index=True,

        use_container_width=True,

        num_rows="fixed",

        column_config={

            "Selecionar": st.column_config.CheckboxColumn(
                "Selecionar"
            ),

            "ID": st.column_config.NumberColumn(
                "ID",
                disabled=True
            ),

            "Matéria": st.column_config.SelectboxColumn(
                "Matéria",
                options=list(
                    materias_nome_para_id.keys()
                ),
                required=True
            ),

            "Assunto": st.column_config.TextColumn(
                "Assunto",
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
            use_container_width=True,
            key="salvar_alteracoes_assunto"
        ):

            try:

                # ======================================
                # COMPARAR ALTERAÇÕES
                # ======================================

                for _, linha_editada in edited_df.iterrows():

                    id_assunto = linha_editada["ID"]

                    linha_original = (
                        df_original[
                            df_original["ID"]
                            == id_assunto
                        ]
                        .iloc[0]
                    )

                    mudou = (

                        linha_editada["Matéria"]
                        != linha_original["Matéria"]

                        or

                        linha_editada["Assunto"]
                        != linha_original["Assunto"]
                    )

                    if not mudou:

                        continue

                    novo_nome = (
                        linha_editada["Assunto"]
                        .upper()
                        .strip()
                    )

                    nova_materia_id = (
                        materias_nome_para_id[
                            linha_editada["Matéria"]
                        ]
                    )

                    if not novo_nome:

                        continue

                    # ==============================
                    # VERIFICAR DUPLICIDADE
                    # ==============================

                    existe = (
                        supabase
                        .table("concur_assuntos")
                        .select("id")
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
                            id_assunto
                        )
                        .execute()
                    )

                    if existe.data:

                        st.warning(
                            f"Duplicidade encontrada "
                            f"para: {novo_nome}"
                        )

                        continue

                    # ==============================
                    # UPDATE
                    # ==============================

                    (
                        supabase
                        .table("concur_assuntos")
                        .update({

                            "materia_id":
                                nova_materia_id,

                            "nome":
                                novo_nome
                        })
                        .eq(
                            "id",
                            id_assunto
                        )
                        .execute()
                    )

                st.success(
                    "Alterações salvas!"
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
            use_container_width=True,
            disabled=len(ids_selecionados) == 0
        ):

            try:

                # ======================================
                # VERIFICAR QUESTÕES VINCULADAS
                # ======================================

                bloqueados = []

                permitidos = []

                for assunto_id in ids_selecionados:

                    qtd = contagem_questoes.get(
                        assunto_id,
                        0
                    )

                    if qtd > 0:

                        bloqueados.append(
                            assunto_id
                        )

                    else:

                        permitidos.append(
                            assunto_id
                        )

                # ======================================
                # BLOQUEADOS
                # ======================================

                if bloqueados:

                    st.warning(
                        f"{len(bloqueados)} assunto(s) "
                        f"não puderam ser excluídos "
                        f"porque possuem questões vinculadas."
                    )

                # ======================================
                # DELETE
                # ======================================

                if permitidos:

                    (
                        supabase
                        .table("concur_assuntos")
                        .delete()
                        .in_(
                            "id",
                            permitidos
                        )
                        .execute()
                    )

                    st.success(
                        f"{len(permitidos)} "
                        f"assunto(s) excluído(s)!"
                    )

                    st.rerun()

            except Exception as e:

                st.error(str(e))