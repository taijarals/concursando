import pandas as pd
import streamlit as st

from database.supabase_client import supabase


# ==================================================
# CSS GLOBAL
# ==================================================

st.markdown("""

<style>

/* =========================================
BACKGROUND
========================================= */

.stApp {

    background-color: #0e1117;
}


/* =========================================
CONTAINER PRINCIPAL
========================================= */

.block-container {

    padding-top: 2rem;

    max-width: 1200px;
}


/* =========================================
TÍTULO
========================================= */

h1 {

    color: white;

    font-size: 2.5rem !important;

    font-weight: 700 !important;

    letter-spacing: -1px;
}


/* =========================================
INPUTS
========================================= */

.stTextInput input {

    background-color: #161b22 !important;

    color: white !important;

    border: 1px solid #30363d !important;

    border-radius: 12px !important;

    padding: 12px !important;
}


/* =========================================
BOTÕES
========================================= */

.stButton button {

    border-radius: 12px !important;

    border: none !important;

    height: 44px !important;

    font-weight: 600 !important;

    transition: 0.2s;
}

.stButton button:hover {

    transform: translateY(-1px);
}


/* =========================================
DATAFRAME
========================================= */

[data-testid="stDataFrame"] {

    border: 1px solid #30363d;

    border-radius: 18px;

    overflow: hidden;
}


/* =========================================
CARD AÇÕES
========================================= */

.action-card {

    background: #161b22;

    border: 1px solid #30363d;

    border-radius: 18px;

    padding: 25px;

    margin-top: 20px;
}


/* =========================================
SUBTÍTULOS
========================================= */

.section-title {

    font-size: 20px;

    font-weight: 600;

    color: white;

    margin-bottom: 20px;
}

</style>

""", unsafe_allow_html=True)


# ==================================================
# TELA
# ==================================================

def tela_cadastro_materia():

    st.title("📚 Gestão de Matérias")

    # =====================================
    # TOOLBAR
    # =====================================

    top1, top2 = st.columns([8, 2])

    with top1:

        busca = st.text_input(

            "Buscar matéria",

            placeholder="Digite o nome da matéria..."
        )

    with top2:

        st.write("")

        if st.button(

            "➕ Nova Matéria",

            use_container_width=True
        ):

            st.session_state["abrir_modal"] = True

    # =====================================
    # MODAL NOVA MATÉRIA
    # =====================================

    if st.session_state.get("abrir_modal"):

        with st.container(border=True):

            st.subheader("➕ Nova Matéria")

            with st.form("form_nova_materia"):

                nome = st.text_input(
                    "Nome da matéria"
                )

                col1, col2 = st.columns(2)

                with col1:

                    salvar = st.form_submit_button(
                        "💾 Salvar",
                        use_container_width=True
                    )

                with col2:

                    cancelar = st.form_submit_button(
                        "❌ Cancelar",
                        use_container_width=True
                    )

            if cancelar:

                st.session_state["abrir_modal"] = False
                st.rerun()

            if salvar:

                nome = nome.upper().strip()

                if not nome:

                    st.warning(
                        "Informe um nome."
                    )

                else:

                    existe = (

                        supabase
                        .table("concur_materias")
                        .select("*")
                        .eq("nome", nome)
                        .execute()
                    )

                    if existe.data:

                        st.warning(
                            "Essa matéria já existe."
                        )

                    else:

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

                        st.session_state[
                            "abrir_modal"
                        ] = False

                        st.rerun()

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

    st.markdown(
        '<div class="section-title">📋 Matérias cadastradas</div>',
        unsafe_allow_html=True
    )

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True
    )

    # =====================================
    # CARD DE AÇÕES
    # =====================================

    st.markdown(
        '<div class="action-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">⚙️ Gerenciar Matéria</div>',
        unsafe_allow_html=True
    )

    materia_selecionada = st.selectbox(

        "Selecionar matéria",

        options=df["ID"],

        format_func=lambda x:

            df[df["ID"] == x]
            ["Matéria"]
            .values[0]
    )

    nome_atual = (

        df[df["ID"] == materia_selecionada]
        ["Matéria"]
        .values[0]
    )

    novo_nome = st.text_input(

        "Novo nome",

        value=nome_atual
    )

    col1, col2 = st.columns(2)

    # =====================================
    # ATUALIZAR
    # =====================================

    with col1:

        if st.button(

            "💾 Atualizar",

            use_container_width=True
        ):

            novo_nome = (
                novo_nome
                .upper()
                .strip()
            )

            if not novo_nome:

                st.warning(
                    "Nome inválido."
                )

            else:

                existe = (

                    supabase
                    .table("concur_materias")
                    .select("*")
                    .eq(
                        "nome",
                        novo_nome
                    )
                    .neq(
                        "id",
                        materia_selecionada
                    )
                    .execute()
                )

                if existe.data:

                    st.warning(
                        "Já existe uma matéria com esse nome."
                    )

                else:

                    (
                        supabase
                        .table("concur_materias")
                        .update({

                            "nome":
                                novo_nome
                        })
                        .eq(
                            "id",
                            materia_selecionada
                        )
                        .execute()
                    )

                    st.success(
                        "Matéria atualizada!"
                    )

                    st.rerun()

    # =====================================
    # EXCLUIR
    # =====================================

    with col2:

        if st.button(

            "🗑️ Excluir",

            type="primary",

            use_container_width=True
        ):

            assuntos = (

                supabase
                .table("concur_assuntos")
                .select("id")
                .eq(
                    "materia_id",
                    materia_selecionada
                )
                .execute()
            )

            if assuntos.data:

                st.warning(

                    "Não é possível excluir "
                    "uma matéria com assuntos vinculados."
                )

            else:

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
                    "Matéria excluída!"
                )

                st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )