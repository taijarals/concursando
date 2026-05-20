import pandas as pd
import streamlit as st

from database.supabase_client import supabase


def tela_cadastro_materia():

    # =====================================
    # TOOLBAR
    # =====================================

    top1, top2 = st.columns([8,2])

    with top1:

        busca = st.text_input(
            "Buscar matéria",
            placeholder="Digite o nome..."
        )

    with top2:

        if st.button(
            "➕ Nova Matéria",
            use_container_width=True
        ):
            st.session_state["abrir_modal"] = True

    st.divider()

    # =====================================
    # DADOS
    # =====================================

    response = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    materias = response.data

    # =====================================
    # FILTRO
    # =====================================

    if busca:

        materias = [

            m for m in materias

            if busca.upper()
            in m["nome"].upper()
        ]

    # =====================================
    # SEM DADOS
    # =====================================

    if not materias:

        st.info(
            "Nenhuma matéria encontrada."
        )

        return

    # =====================================
    # DATAFRAME
    # =====================================

    df = pd.DataFrame(materias)

    df = df.rename(columns={

        "id": "ID",
        "nome": "Matéria"
    })

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True
    )

    # =====================================
    # AÇÕES
    # =====================================

    st.subheader("Ações")

    materia_selecionada = st.selectbox(

        "Selecionar matéria",

        options=df["ID"],

        format_func=lambda x:

            df[df["ID"] == x]
            ["Matéria"]
            .values[0]
    )

    col1, col2 = st.columns(2)

    # =====================================
    # EDITAR
    # =====================================

    with col1:

        novo_nome = st.text_input(
            "Novo nome"
        )

        if st.button(
            "💾 Atualizar",
            use_container_width=True
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
                    materia_selecionada
                )
                .execute()
            )

            st.success(
                "Atualizado!"
            )

            st.rerun()

    # =====================================
    # DELETE
    # =====================================

    with col2:

        st.write("")

        st.write("")

        if st.button(

            "🗑️ Excluir",

            type="primary",

            use_container_width=True
        ):

            (
                supabase
                .table("concur_materias")
                .delete()
                .eq(
                    "id",
                    materia_selecionada
                )
                .execute()
            )

            st.success(
                "Excluído!"
            )

            st.rerun()