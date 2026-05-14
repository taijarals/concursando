import streamlit as st

from database.supabase_client import supabase


def tela_cadastro():

    st.title("➕ Cadastro de Questão")

    # =====================================
    # BUSCAR DADOS AUXILIARES
    # =====================================

    materias = (
        supabase
        .table("concur_materias")
        .select("*")
        .execute()
    )

    assuntos = (
        supabase
        .table("concur_assuntos")
        .select("*")
        .execute()
    )

    bancas = (
        supabase
        .table("concur_bancas")
        .select("*")
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

    materia_nome = st.selectbox(
        "Matéria",
        list(materias_map.keys())
    )

    assunto_nome = st.selectbox(
        "Assunto",
        list(assuntos_map.keys())
    )

    banca_nome = st.selectbox(
        "Banca",
        list(bancas_map.keys())
    )

    resposta_correta = st.text_input(
        "Resposta Correta"
    )

    # =====================================
    # SALVAR
    # =====================================

    if st.button("Salvar Questão"):

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
                resposta_correta
        }

        try:

            (
                supabase
                .table("concur_questoes")
                .insert(data)
                .execute()
            )

            st.success(
                "Questão salva com sucesso!"
            )

        except Exception as e:

            st.error(str(e))