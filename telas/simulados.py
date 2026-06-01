import random
from datetime import datetime

import streamlit as st
from database.supabase_client import supabase


# =========================
# CONSULTAS
# =========================

def buscar_materias():
    return supabase.table("concur_materias").select("*").order("nome").execute().data or []


def buscar_bancas():
    return supabase.table("concur_bancas").select("*").order("nome").execute().data or []


def buscar_assuntos(materias_ids=None):
    query = supabase.table("concur_assuntos").select("*").order("nome")

    if materias_ids:
        query = query.in_("materia_id", materias_ids)

    return query.execute().data or []


def buscar_questoes(materias_ids=None, assuntos_ids=None, bancas_ids=None, dificuldades=None):
    query = (
        supabase
        .table("concur_questoes")
        .select("""
            *,
            concur_materias(nome),
            concur_assuntos(nome),
            concur_bancas(nome)
        """)
        .eq("ativo", True)
    )

    if materias_ids:
        query = query.in_("materia_id", materias_ids)

    if assuntos_ids:
        query = query.in_("assunto_id", assuntos_ids)

    if bancas_ids:
        query = query.in_("banca_id", bancas_ids)

    if dificuldades:
        query = query.in_("dificuldade", dificuldades)

    return query.execute().data or []


def buscar_alternativas(questao_id):
    return (
        supabase
        .table("concur_alternativas")
        .select("*")
        .eq("questao_id", questao_id)
        .order("letra")
        .execute()
        .data
        or []
    )


def salvar_resolucao(user_id, questao_id, resposta_usuario, acertou):
    supabase.table("concur_resolucoes").insert({
        "user_id": str(user_id),
        "questao_id": questao_id,
        "resposta_usuario": resposta_usuario,
        "acertou": acertou
    }).execute()


# =========================
# ESTADO
# =========================

def iniciar_simulado(questoes):
    st.session_state["simulado"] = {
        "inicio": datetime.now(),
        "indice": 0,
        "questoes": questoes,
        "respostas": {},
        "salvo": False
    }


def resetar_simulado():
    st.session_state["simulado"] = None


# =========================
# CORREÇÃO
# =========================

def corrigir(q, resposta_usuario):
    if resposta_usuario is None:
        return False

    if q["tipo"] == "multipla_escolha":

        alternativas = buscar_alternativas(q["id"])

        correta = None

        for alt in alternativas:
            if alt.get("correta"):
                correta = alt.get("letra")
                break

        if correta is None:
            return False

        resposta_usuario = resposta_usuario.split(")", 1)[0]

        return resposta_usuario.strip().upper() == correta.strip().upper()

    return (
        str(resposta_usuario).strip().lower()
        == str(q.get("resposta_correta")).strip().lower()
    )


# =========================
# TELA
# =========================

def tela_simulados():

    st.title("📋 Simulados")

    if "simulado" not in st.session_state:
        st.session_state["simulado"] = None

    simulado = st.session_state["simulado"]

    # =========================
    # CONFIGURAÇÃO
    # =========================

    if simulado is None:

        materias = buscar_materias()
        bancas = buscar_bancas()

        mapa_materias = {x["nome"]: x["id"] for x in materias}
        mapa_bancas = {x["nome"]: x["id"] for x in bancas}

        disciplinas = st.multiselect(
            "📚 Disciplinas",
            list(mapa_materias.keys())
        )

        materias_ids = [mapa_materias[x] for x in disciplinas]

        assuntos = buscar_assuntos(materias_ids)

        mapa_assuntos = {x["nome"]: x["id"] for x in assuntos}

        assuntos_sel = st.multiselect(
            "📖 Assuntos",
            list(mapa_assuntos.keys())
        )

        bancas_sel = st.multiselect(
            "🏛️ Bancas",
            list(mapa_bancas.keys())
        )

        dificuldades = st.multiselect(
            "⚙️ Dificuldades",
            [1, 2, 3, 4, 5],
            default=[1, 2, 3, 4, 5]
        )

        quantidade = st.number_input(
            "🔢 Quantidade de questões",
            min_value=1,
            value=20,
            step=1
        )

        if st.button("🚀 Gerar Simulado", use_container_width=True):

            questoes = buscar_questoes(
                materias_ids=materias_ids,
                assuntos_ids=[mapa_assuntos[x] for x in assuntos_sel],
                bancas_ids=[mapa_bancas[x] for x in bancas_sel],
                dificuldades=dificuldades
            )

            if not questoes:
                st.warning("Nenhuma questão encontrada.")
                return

            random.shuffle(questoes)

            questoes = questoes[:min(quantidade, len(questoes))]

            iniciar_simulado(questoes)

            st.rerun()

        return

    # =========================
    # RESOLUÇÃO
    # =========================

    questoes = simulado["questoes"]
    indice = simulado["indice"]

    q = questoes[indice]

    total = len(questoes)

    respondidas = len(simulado["respostas"])
    pendentes = total - respondidas

    tempo = datetime.now() - simulado["inicio"]

    horas = int(tempo.total_seconds() // 3600)
    minutos = int((tempo.total_seconds() % 3600) // 60)
    segundos = int(tempo.total_seconds() % 60)

    st.progress((indice + 1) / total)

    c1, c2, c3 = st.columns(3)

    c1.metric("Respondidas", respondidas)
    c2.metric("Pendentes", pendentes)
    c3.metric("Tempo", f"{horas:02d}:{minutos:02d}:{segundos:02d}")

    st.subheader(f"Questão {indice + 1} de {total}")

    materia = (q.get("concur_materias") or {}).get("nome", "-")
    assunto = (q.get("concur_assuntos") or {}).get("nome", "-")
    banca = (q.get("concur_bancas") or {}).get("nome", "-")
    fonte = q.get("fonte") or "-"

    st.info(
        f"""
📚 Disciplina: {materia}

📖 Assunto: {assunto}

🏛️ Banca: {banca}

📋 Fonte: {fonte}

⚙️ Dificuldade: {q.get("dificuldade", "-")}
"""
    )

    st.markdown(q["enunciado"])

    resposta = None

    if q["tipo"] == "multipla_escolha":

        alternativas = buscar_alternativas(q["id"])

        opcoes = [
            f"{a['letra']}) {a['texto']}"
            for a in alternativas
        ]

        resposta = st.radio(
            "Resposta",
            opcoes,
            key=f"q_{q['id']}"
        )

    elif q["tipo"] == "certo_errado":

        resposta = st.radio(
            "Resposta",
            ["Certo", "Errado"],
            key=f"q_{q['id']}"
        )

    else:

        resposta = st.text_area(
            "Resposta",
            key=f"q_{q['id']}"
        )

    if resposta:
        simulado["respostas"][q["id"]] = resposta

    st.divider()

    cols = st.columns(min(total, 10))

    for i in range(min(total, 10)):
        if cols[i].button(str(i + 1)):
            simulado["indice"] = i
            st.rerun()

    a, b, c = st.columns(3)

    if a.button("⬅️ Anterior", use_container_width=True):
        if indice > 0:
            simulado["indice"] -= 1
            st.rerun()

    if b.button("➡️ Próxima", use_container_width=True):
        if indice < total - 1:
            simulado["indice"] += 1
            st.rerun()

    finalizar = c.button("🏁 Finalizar", use_container_width=True)

    if finalizar:

        st.warning(
            f"Você respondeu {respondidas} de {total} questões."
        )

        acertos = 0
        erros = 0

        user = st.session_state.get("user")

        if not simulado["salvo"]:

            for questao in questoes:

                resposta_usuario = simulado["respostas"].get(questao["id"])

                acertou = corrigir(
                    questao,
                    resposta_usuario
                )

                salvar_resolucao(
                    user.id,
                    questao["id"],
                    resposta_usuario,
                    acertou
                )

                if acertou:
                    acertos += 1
                else:
                    erros += 1

            simulado["salvo"] = True

            taxa = round((acertos / total) * 100, 2)

            st.success("Simulado finalizado!")

            st.metric("Acertos", acertos)
            st.metric("Erros", erros)
            st.metric("Taxa", f"{taxa}%")

            if st.button("🔄 Novo Simulado"):
                resetar_simulado()
                st.rerun()