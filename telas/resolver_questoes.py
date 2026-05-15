import unicodedata

import streamlit as st

from database.supabase_client import supabase


def normalizar_texto(texto):
    if texto is None:
        return ""

    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)

    return "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )


def buscar_registros(tabela):
    response = (
        supabase
        .table(tabela)
        .select("*")
        .order("nome")
        .execute()
    )

    return response.data or []


def criar_mapa_nome_id(registros):
    return {
        item["nome"]: item["id"]
        for item in registros
    }


def resetar_resolucao():
    st.session_state.pop("resolver_resultado", None)
    st.session_state.pop("resolver_resposta_usuario", None)
    st.session_state.pop("resolver_corrigida", None)


def corrigir_questao(questao, resposta_usuario, alternativas):
    tipo = questao.get("tipo")
    resposta_correta = questao.get("resposta_correta")

    if tipo == "multipla_escolha":
        for alternativa in alternativas:
            if alternativa.get("correta"):
                resposta_correta = alternativa.get("letra")
                break

        acertou = (
            normalizar_texto(resposta_usuario)
            == normalizar_texto(resposta_correta)
        )

        return acertou, resposta_correta

    if tipo == "certo_errado":
        acertou = (
            normalizar_texto(resposta_usuario)
            == normalizar_texto(resposta_correta)
        )

        return acertou, resposta_correta

    return None, resposta_correta


def buscar_assuntos(materia_id):
    query = (
        supabase
        .table("concur_assuntos")
        .select("*")
        .order("nome")
    )

    if materia_id:
        query = query.eq("materia_id", materia_id)

    response = query.execute()

    return response.data or []


def buscar_questoes(
    materia_id,
    assunto_id,
    banca_id,
    tipo,
    dificuldade,
    busca
):
    query = (
        supabase
        .table("concur_questoes")
        .select("""
            *,
            concur_materias(nome),
            concur_assuntos(nome),
            concur_bancas(nome)
        """)
        .order("id", desc=True)
    )

    if materia_id:
        query = query.eq("materia_id", materia_id)

    if assunto_id:
        query = query.eq("assunto_id", assunto_id)

    if banca_id:
        query = query.eq("banca_id", banca_id)

    if tipo != "Todos":
        query = query.eq("tipo", tipo)

    if dificuldade != "Todas":
        query = query.eq("dificuldade", dificuldade)

    response = query.execute()

    questoes = response.data or []

    if busca:
        busca = busca.strip().lower()

        questoes = [
            questao
            for questao in questoes
            if busca in questao.get("enunciado", "").lower()
        ]

    return questoes


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


def obter_indice_questao(questoes):
    if "resolver_indice" not in st.session_state:
        st.session_state["resolver_indice"] = 0

    if st.session_state["resolver_indice"] >= len(questoes):
        st.session_state["resolver_indice"] = 0

    return st.session_state["resolver_indice"]


def avancar_questao(total_questoes):
    indice_atual = st.session_state.get("resolver_indice", 0)

    st.session_state["resolver_indice"] = (
        indice_atual + 1
    ) % total_questoes

    resetar_resolucao()


def tela_resolver():
    st.title("📝 Resolver Questões")

    st.write(
        "Use os filtros abaixo para escolher uma questão, "
        "responda e confira o gabarito."
    )

    try:
        materias = buscar_registros("concur_materias")
        bancas = buscar_registros("concur_bancas")
    except Exception as e:
        st.error(f"Erro ao carregar filtros: {e}")
        return

    materias_map = criar_mapa_nome_id(materias)
    bancas_map = criar_mapa_nome_id(bancas)

    with st.expander("🔎 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            materia_nome = st.selectbox(
                "Matéria",
                ["Todas"] + list(materias_map.keys())
            )

        materia_id = None

        if materia_nome != "Todas":
            materia_id = materias_map[materia_nome]

        try:
            assuntos = buscar_assuntos(materia_id)
        except Exception as e:
            st.error(f"Erro ao carregar assuntos: {e}")
            return

        assuntos_map = criar_mapa_nome_id(assuntos)

        with col2:
            assunto_nome = st.selectbox(
                "Assunto",
                ["Todos"] + list(assuntos_map.keys())
            )

        with col3:
            banca_nome = st.selectbox(
                "Banca",
                ["Todas"] + list(bancas_map.keys())
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            tipo = st.selectbox(
                "Tipo",
                [
                    "Todos",
                    "multipla_escolha",
                    "certo_errado",
                    "aberta"
                ]
            )

        with col5:
            dificuldade = st.selectbox(
                "Dificuldade",
                [
                    "Todas",
                    1,
                    2,
                    3,
                    4,
                    5
                ]
            )

        with col6:
            busca = st.text_input(
                "Buscar no enunciado"
            )

    assunto_id = None
    banca_id = None

    if assunto_nome != "Todos":
        assunto_id = assuntos_map[assunto_nome]

    if banca_nome != "Todas":
        banca_id = bancas_map[banca_nome]

    filtros_atuais = {
        "materia_id": materia_id,
        "assunto_id": assunto_id,
        "banca_id": banca_id,
        "tipo": tipo,
        "dificuldade": dificuldade,
        "busca": busca
    }

    if st.session_state.get("resolver_filtros") != filtros_atuais:
        st.session_state["resolver_filtros"] = filtros_atuais
        st.session_state["resolver_indice"] = 0
        resetar_resolucao()

    try:
        questoes = buscar_questoes(
            materia_id=materia_id,
            assunto_id=assunto_id,
            banca_id=banca_id,
            tipo=tipo,
            dificuldade=dificuldade,
            busca=busca
        )
    except Exception as e:
        st.error(f"Erro ao buscar questões: {e}")
        return

    st.write(f"**Total encontrado:** {len(questoes)} questões")

    if not questoes:
        st.info("Nenhuma questão encontrada para os filtros selecionados.")
        return

    indice = obter_indice_questao(questoes)
    questao = questoes[indice]

    st.caption(
        f"Questão {indice + 1} de {len(questoes)}"
    )

    st.subheader(f"Questão #{questao['id']}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write(
            "**Matéria:** "
            f"{questao['concur_materias']['nome']}"
        )

    with col2:
        st.write(
            "**Assunto:** "
            f"{questao['concur_assuntos']['nome']}"
        )

    with col3:
        st.write(
            "**Banca:** "
            f"{questao['concur_bancas']['nome']}"
        )

    with col4:
        st.write(
            "**Dificuldade:** "
            f"{questao['dificuldade']}"
        )

    st.divider()

    st.markdown(questao["enunciado"])

    alternativas = []
    resposta_usuario = None

    if questao["tipo"] == "multipla_escolha":
        try:
            alternativas = buscar_alternativas(questao["id"])
        except Exception as e:
            st.error(f"Erro ao carregar alternativas: {e}")
            return

        if not alternativas:
            st.warning("Essa questão não possui alternativas cadastradas.")
            return

        opcoes = [
            f"{alternativa['letra']}) {alternativa['texto']}"
            for alternativa in alternativas
        ]

        resposta = st.radio(
            "Escolha uma alternativa",
            opcoes,
            key=f"resposta_{questao['id']}"
        )

        resposta_usuario = resposta.split(")", 1)[0]

    elif questao["tipo"] == "certo_errado":
        resposta_usuario = st.radio(
            "Escolha uma opção",
            [
                "Certo",
                "Errado"
            ],
            key=f"resposta_{questao['id']}"
        )

    else:
        resposta_usuario = st.text_area(
            "Digite sua resposta",
            key=f"resposta_{questao['id']}"
        )

    col_corrigir, col_proxima = st.columns(2)

    with col_corrigir:
        if st.button("✅ Corrigir"):
            if not resposta_usuario:
                st.warning("Informe uma resposta antes de corrigir.")
            else:
                acertou, resposta_correta = corrigir_questao(
                    questao,
                    resposta_usuario,
                    alternativas
                )

                st.session_state["resolver_corrigida"] = True
                st.session_state["resolver_resposta_usuario"] = resposta_usuario
                st.session_state["resolver_resultado"] = {
                    "acertou": acertou,
                    "resposta_correta": resposta_correta
                }

    with col_proxima:
        if st.button("➡️ Próxima questão"):
            avancar_questao(len(questoes))
            st.rerun()

    if st.session_state.get("resolver_corrigida"):
        resultado = st.session_state.get("resolver_resultado", {})

        acertou = resultado.get("acertou")
        resposta_correta = resultado.get("resposta_correta")

        if acertou is True:
            st.success("Você acertou! 🎉")
        elif acertou is False:
            st.error("Você errou.")
        else:
            st.info("Questões abertas precisam de correção manual.")

        st.write(
            "**Sua resposta:** "
            f"{st.session_state.get('resolver_resposta_usuario')}"
        )

        st.write(
            "**Gabarito:** "
            f"{resposta_correta}"
        )

        if questao.get("explicacao_ia"):
            with st.expander("🤖 Explicação IA", expanded=True):
                st.write(questao["explicacao_ia"])