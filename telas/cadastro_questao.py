import streamlit as st

from database.supabase_client import supabase


# ==================================================
# MODAL MATÉRIA
# ==================================================

@st.dialog("📚 Nova Matéria")
def modal_materia():

    nome = st.text_input(
        "Nome da Matéria",
        key="nova_materia"
    )

    if st.button(
        "Salvar Matéria"
    ):

        try:

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


# ==================================================
# MODAL BANCA
# ==================================================

@st.dialog("🏛️ Nova Banca")
def modal_banca():

    nome = st.text_input(
        "Nome da Banca",
        key="nova_banca"
    )

    if st.button(
        "Salvar Banca"
    ):

        try:

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
# MODAL ASSUNTO
# ==================================================

@st.dialog("📝 Novo Assunto")
def modal_assunto():

    materias = (
        supabase
        .table("concur_materias")
        .select("*")
        .execute()
    )

    materias_map = {
        item["nome"]: item["id"]
        for item in materias.data
    }

    materia_nome = st.selectbox(
        "Matéria",
        list(materias_map.keys()),
        key="modal_assunto_materia"
    )

    nome = st.text_input(
        "Nome do Assunto",
        key="novo_assunto"
    )

    if st.button(
        "Salvar Assunto"
    ):

        try:

            (
                supabase
                .table("concur_assuntos")
                .insert({
                    "materia_id":
                        materias_map[materia_nome],

                    "nome": nome
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
# TELA PRINCIPAL
# ==================================================

def tela_cadastro():

    st.title("➕ Cadastro de Questão")

    # =====================================
    # BUSCAR DADOS
    # =====================================

    materias = (
        supabase
        .table("concur_materias")
        .select("*")
        .order("nome")
        .execute()
    )

    assuntos = (
        supabase
        .table("concur_assuntos")
        .select("*")
        .order("nome")
        .execute()
    )

    bancas = (
        supabase
        .table("concur_bancas")
        .select("*")
        .order("nome")
        .execute()
    )

    # =====================================
    # MAPAS
    # =====================================

    materias_map = {
        item["nome"]: item["id"]
        for item in materias.data
    }

    assuntos_map = {
        item["nome"]: item["id"]
        for item in assuntos.data
    }

    bancas_map = {
        item["nome"]: item["id"]
        for item in bancas.data
    }

    # =====================================
    # FORMULÁRIO
    # =====================================

    enunciado = st.text_area(
        "Enunciado"
    )

    tipo = st.selectbox(
        "Tipo",
        [
            "multipla_escolha",
            "certo_errado",
            "aberta"
        ]
    )

    # =====================================
    # MATÉRIA
    # =====================================

    col1, col2 = st.columns([10, 1])

    with col1:

        materia_nome = st.selectbox(
            "Matéria",
            list(materias_map.keys())
        )

    with col2:

        st.write("")

        if st.button(
            "➕",
            key="btn_materia"
        ):

            modal_materia()

    # =====================================
    # ASSUNTO
    # =====================================

    col1, col2 = st.columns([10, 1])

    with col1:

        assunto_nome = st.selectbox(
            "Assunto",
            list(assuntos_map.keys())
        )

    with col2:

        st.write("")

        if st.button(
            "➕",
            key="btn_assunto"
        ):

            modal_assunto()

    # =====================================
    # BANCA
    # =====================================

    col1, col2 = st.columns([10, 1])

    with col1:

        banca_nome = st.selectbox(
            "Banca",
            list(bancas_map.keys())
        )

    with col2:

        st.write("")

        if st.button(
            "➕",
            key="btn_banca"
        ):

            modal_banca()

    # =====================================
    # MULTIPLA ESCOLHA
    # =====================================

    alternativas = []

    alternativa_correta = None

    if tipo == "multipla_escolha":

        st.subheader("Alternativas")

        letra_a = st.text_input(
            "Alternativa A"
        )

        letra_b = st.text_input(
            "Alternativa B"
        )

        letra_c = st.text_input(
            "Alternativa C"
        )

        letra_d = st.text_input(
            "Alternativa D"
        )

        letra_e = st.text_input(
            "Alternativa E"
        )

        alternativa_correta = st.selectbox(
            "Alternativa Correta",
            ["A", "B", "C", "D", "E"]
        )

        alternativas = [
            ("A", letra_a),
            ("B", letra_b),
            ("C", letra_c),
            ("D", letra_d),
            ("E", letra_e)
        ]

    # =====================================
    # SALVAR
    # =====================================

    if st.button("Salvar Questão"):

        try:

            # =====================================
            # DADOS QUESTÃO
            # =====================================

            data = {

                "tipo": tipo,

                "enunciado": enunciado,

                "materia_id":
                    materias_map[materia_nome],

                "assunto_id":
                    assuntos_map[assunto_nome],

                "banca_id":
                    bancas_map[banca_nome],

                "resposta_correta":
                    alternativa_correta
            }

            # =====================================
            # SALVAR QUESTÃO
            # =====================================

            response = (
                supabase
                .table("concur_questoes")
                .insert(data)
                .execute()
            )

            questao_id = response.data[0]["id"]

            # =====================================
            # SALVAR ALTERNATIVAS
            # =====================================

            if tipo == "multipla_escolha":

                for letra, texto in alternativas:

                    (
                        supabase
                        .table("concur_alternativas")
                        .insert({

                            "questao_id":
                                questao_id,

                            "letra":
                                letra,

                            "texto":
                                texto,

                            "correta":
                                letra == alternativa_correta
                        })
                        .execute()
                    )

            st.success(
                "Questão salva com sucesso!"
            )

        except Exception as e:

            st.error(str(e))