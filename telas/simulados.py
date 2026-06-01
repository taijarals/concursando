import random
from datetime import datetime

import streamlit as st
from database.supabase_client import supabase


def buscar_materias():
    response = supabase.table("concur_materias").select("*").order("nome").execute()
    return response.data or []


def buscar_questoes(materia_id=None):
    query = (
        supabase
        .table("concur_questoes")
        .select("*")
        .eq("ativo", True)
    )

    if materia_id:
        query = query.eq("materia_id", materia_id)

    response = query.execute()
    return response.data or []


def buscar_alternativas(questao_id):
    response = (
        supabase
        .table("concur_alternativas")
        .select("*")
        .eq("questao_id", questao_id)
        .order("letra")
        .execute()
    )
    return response.data or []


def salvar_resolucao(user_id, questao_id, resposta_usuario, acertou):
    supabase.table("concur_resolucoes").insert({
        "user_id": str(user_id),
        "questao_id": questao_id,
        "resposta_usuario": resposta_usuario,
        "acertou": acertou
    }).execute()


def iniciar_simulado(questoes):
    st.session_state["simulado"] = {
        "inicio": datetime.now(),
        "indice": 0,
        "questoes": questoes,
        "respostas": {},
        "finalizado": False
    }


def tela_simulados():
    st.title("📋 Simulados")

    if "simulado" not in st.session_state:
        st.session_state["simulado"] = None

    if st.session_state["simulado"] is None:

        materias = buscar_materias()
        mapa = {m["nome"]: m["id"] for m in materias}

        materia_nome = st.selectbox(
            "Matéria",
            ["Todas"] + list(mapa.keys())
        )

        qtd = st.number_input(
            "Quantidade de questões",
            min_value=5,
            max_value=100,
            value=20
        )

        if st.button("🚀 Gerar Simulado"):

            materia_id = None

            if materia_nome != "Todas":
                materia_id = mapa[materia_nome]

            questoes = buscar_questoes(materia_id)

            if not questoes:
                st.warning("Nenhuma questão encontrada.")
                return

            random.shuffle(questoes)

            questoes = questoes[:min(qtd, len(questoes))]

            iniciar_simulado(questoes)

            st.rerun()

        return

    simulado = st.session_state["simulado"]

    total = len(simulado["questoes"])
    indice = simulado["indice"]
    questao = simulado["questoes"][indice]

    st.progress((indice + 1) / total)

    tempo = datetime.now() - simulado["inicio"]

    st.caption(
        f"Questão {indice + 1} de {total} | "
        f"Tempo: {tempo.seconds // 60} min"
    )

    st.markdown(questao["enunciado"])

    resposta = None

    if questao["tipo"] == "multipla_escolha":

        alternativas = buscar_alternativas(questao["id"])

        opcoes = [
            f"{a['letra']}) {a['texto']}"
            for a in alternativas
        ]

        valor_atual = simulado["respostas"].get(questao["id"])

        resposta = st.radio(
            "Resposta",
            opcoes,
            index=None if valor_atual is None else 0,
            key=f"simulado_{questao['id']}"
        )

    elif questao["tipo"] == "certo_errado":

        resposta = st.radio(
            "Resposta",
            ["Certo", "Errado"],
            key=f"simulado_{questao['id']}"
        )

    if resposta:
        simulado["respostas"][questao["id"]] = resposta

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("⬅️ Anterior") and indice > 0:
            simulado["indice"] -= 1
            st.rerun()

    with c2:
        if st.button("➡️ Próxima") and indice < total - 1:
            simulado["indice"] += 1
            st.rerun()

    with c3:
        if st.button("🏁 Finalizar"):
            simulado["finalizado"] = True
            st.rerun()

    if simulado["finalizado"]:

        user = st.session_state.get("user")

        acertos = 0
        erros = 0

        for q in simulado["questoes"]:

            resposta_usuario = simulado["respostas"].get(q["id"])

            acertou = False

            if q["tipo"] == "certo_errado":
                acertou = (
                    str(resposta_usuario).lower()
                    == str(q["resposta_correta"]).lower()
                )

            salvar_resolucao(
                user.id,
                q["id"],
                resposta_usuario,
                acertou
            )

            if acertou:
                acertos += 1
            else:
                erros += 1

        taxa = round((acertos / total) * 100, 1) if total else 0

        st.header("📊 Resultado Final")

        st.metric("Acertos", acertos)
        st.metric("Erros", erros)
        st.metric("Taxa", f"{taxa}%")

        if st.button("🔄 Novo Simulado"):
            st.session_state["simulado"] = None
            st.rerun()