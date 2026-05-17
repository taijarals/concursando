from io import BytesIO

import streamlit as st

from database.supabase_client import supabase
from services.pdf_service import extrair_paginas_pdf
from services.prova_pdf_parser import identificar_dados_prova
from services.questao_pdf_parser import (
    extrair_questoes_pdf_gemini
)


def inicializar_estado_pdf():
    if "pdf_etapa" not in st.session_state:
        st.session_state["pdf_etapa"] = "upload"


def resetar_importacao_pdf():
    chaves = [
        "pdf_etapa",
        "pdf_paginas",
        "pdf_dados",
        "pdf_dados_confirmados",
        "pdf_questoes",
        "pdf_bytes",
        "pdf_nome"
    ]

    for chave in chaves:
        st.session_state.pop(chave, None)

    st.session_state["pdf_etapa"] = "upload"


def normalizar_nome(valor, padrao):
    texto = str(valor or "").strip().upper()

    if texto:
        return texto

    return padrao


def buscar_ou_criar_registro(tabela, nome):
    registro = (
        supabase
        .table(tabela)
        .select("*")
        .eq("nome", nome)
        .execute()
    )

    if registro.data:
        return registro.data[0]["id"]

    novo = (
        supabase
        .table(tabela)
        .insert({
            "nome": nome
        })
        .execute()
    )

    return novo.data[0]["id"]


def buscar_ou_criar_assunto(
    nome,
    materia_id
):
    registro = (
        supabase
        .table("concur_assuntos")
        .select("*")
        .eq("nome", nome)
        .eq("materia_id", materia_id)
        .execute()
    )

    if registro.data:
        return registro.data[0]["id"]

    novo = (
        supabase
        .table("concur_assuntos")
        .insert({
            "nome": nome,
            "materia_id": materia_id
        })
        .execute()
    )

    return novo.data[0]["id"]


def salvar_questao_pdf(
    questao,
    user
):
    materia_nome = normalizar_nome(
        questao.get("materia"),
        "GERAL"
    )

    assunto_nome = normalizar_nome(
        questao.get("assunto"),
        "A CLASSIFICAR"
    )

    banca_nome = normalizar_nome(
        questao.get("banca"),
        "NÃO INFORMADA"
    )

    materia_id = buscar_ou_criar_registro(
        "concur_materias",
        materia_nome
    )

    banca_id = buscar_ou_criar_registro(
        "concur_bancas",
        banca_nome
    )

    assunto_id = buscar_ou_criar_assunto(
        assunto_nome,
        materia_id
    )

    response = (
        supabase
        .table("concur_questoes")
        .insert({
            "tipo": questao.get(
                "tipo",
                "aberta"
            ),
            "enunciado": questao.get(
                "enunciado",
                ""
            ),
            "materia_id": materia_id,
            "assunto_id": assunto_id,
            "banca_id": banca_id,
            "cargo": normalizar_nome(
                questao.get("cargo"),
                "NÃO INFORMADO"
            ),
            "dificuldade": questao.get(
                "dificuldade",
                3
            ),
            "explicacao_ia": questao.get(
                "explicacao_ia"
            ),
            "resposta_correta": questao.get(
                "resposta_correta",
                ""
            ),
            "fonte": questao.get(
                "fonte",
                ""
            ),
            "criado_por": user.id
        })
        .execute()
    )

    questao_id = response.data[0]["id"]

    if questao.get("tipo") != "multipla_escolha":
        return questao_id

    for alternativa in questao.get(
        "alternativas",
        []
    ):
        (
            supabase
            .table("concur_alternativas")
            .insert({
                "questao_id": questao_id,
                "letra": alternativa.get(
                    "letra"
                ),
                "texto": alternativa.get(
                    "texto",
                    ""
                ),
                "correta": alternativa.get(
                    "correta",
                    False
                )
            })
            .execute()
        )

    return questao_id


def importar_questoes_extraidas(
    questoes,
    user
):
    ids_importados = []

    for questao in questoes:
        questao_id = salvar_questao_pdf(
            questao,
            user
        )

        ids_importados.append(
            questao_id
        )

    return ids_importados


def render_upload_pdf():
    st.subheader("1. Enviar PDF")

    arquivo_pdf = st.file_uploader(
        "Arquivo PDF",
        type=["pdf"]
    )

    if not arquivo_pdf:
        st.info(
            "Envie um arquivo PDF para começar."
        )
        return

    if st.button("Analisar PDF"):
        with st.spinner(
            "Lendo PDF e identificando dados da prova..."
        ):
            try:
                pdf_bytes = arquivo_pdf.getvalue()

                paginas = extrair_paginas_pdf(
                    BytesIO(pdf_bytes)
                )

                dados = identificar_dados_prova(
                    paginas
                )

                st.session_state[
                    "pdf_paginas"
                ] = paginas

                st.session_state[
                    "pdf_bytes"
                ] = pdf_bytes

                st.session_state[
                    "pdf_nome"
                ] = arquivo_pdf.name

                st.session_state[
                    "pdf_dados"
                ] = dados

                st.session_state[
                    "pdf_etapa"
                ] = "confirmar_dados"

                st.success(
                    "PDF analisado com sucesso!"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    f"Erro ao analisar PDF: {e}"
                )


def render_confirmar_dados():
    st.subheader(
        "2. Confirmar dados da prova"
    )

    dados = st.session_state.get(
        "pdf_dados",
        {}
    )

    st.write(
        "Confira os dados identificados automaticamente."
    )

    col1, col2 = st.columns(2)

    with col1:
        banca = st.text_input(
            "Banca",
            value=dados.get("banca", "")
        )

        instituicao = st.text_input(
            "Instituição",
            value=dados.get(
                "instituicao",
                ""
            )
        )

    with col2:
        cargo = st.text_input(
            "Cargo",
            value=dados.get("cargo", "")
        )

        ano = st.text_input(
            "Ano",
            value=dados.get("ano", "")
        )

    if st.button("Continuar"):
        st.session_state[
            "pdf_dados_confirmados"
        ] = {
            "banca": banca.strip().upper(),
            "ano": str(ano).strip(),
            "instituicao": (
                instituicao.strip().upper()
            ),
            "cargo": cargo.strip().upper()
        }

        st.session_state[
            "pdf_etapa"
        ] = "identificar_questoes"

        st.success("Dados confirmados!")

        st.rerun()


def render_identificar_questoes():
    st.subheader(
        "3. Identificar questões"
    )

    dados = st.session_state.get(
        "pdf_dados_confirmados",
        {}
    )

    st.write("Dados confirmados:")

    st.json(dados)

    st.info(
        "O sistema enviará o PDF para o Gemini "
        "e tentará extrair as questões."
    )

    if st.button(
        "🔎 Identificar questões do PDF"
    ):
        with st.spinner(
            "Identificando questões..."
        ):
            try:
                pdf_bytes = st.session_state.get(
                    "pdf_bytes"
                )

                if not pdf_bytes:
                    st.warning(
                        "PDF não encontrado."
                    )
                    return

                questoes = (
                    extrair_questoes_pdf_gemini(
                        pdf_bytes,
                        dados
                    )
                )

                st.session_state[
                    "pdf_questoes"
                ] = questoes

                st.session_state[
                    "pdf_etapa"
                ] = "revisar_questoes"

                st.success(
                    f"{len(questoes)} questões identificadas!"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    f"Erro ao identificar questões: {e}"
                )


def render_dados_questao(questao):
    st.write(
        f"**Tipo:** {questao.get('tipo', '')}"
    )

    st.write(
        f"**Enunciado:** "
        f"{questao.get('enunciado', '')}"
    )

    alternativas = questao.get(
        "alternativas",
        []
    )

    if alternativas:
        st.write("**Alternativas:**")

        for alternativa in alternativas:
            st.write(
                f"{alternativa.get('letra')}) "
                f"{alternativa.get('texto', '')}"
            )


def render_revisar_questoes():
    st.subheader("4. Revisar questões")

    questoes = st.session_state.get(
        "pdf_questoes",
        []
    )

    if not questoes:
        st.warning(
            "Nenhuma questão encontrada."
        )

        return

    st.success(
        f"{len(questoes)} questões carregadas."
    )

    for indice, questao in enumerate(
        questoes,
        start=1
    ):
        with st.expander(
            f"Questão {indice}"
        ):
            render_dados_questao(
                questao
            )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "⬅️ Voltar"
        ):
            st.session_state[
                "pdf_etapa"
            ] = "identificar_questoes"

            st.rerun()

    with col2:
        if st.button(
            "💾 Importar questões"
        ):
            try:
                user = st.session_state.user

                ids_importados = (
                    importar_questoes_extraidas(
                        questoes,
                        user
                    )
                )

                st.success(
                    f"{len(ids_importados)} "
                    f"questões importadas!"
                )

                resetar_importacao_pdf()

                st.rerun()

            except Exception as e:
                st.error(
                    f"Erro ao importar: {e}"
                )


def tela_importar_pdf():
    inicializar_estado_pdf()

    st.title("📄 Importar Prova PDF")

    st.write(
        "Envie uma prova em PDF "
        "para extração das questões."
    )

    if st.button(
        "🧹 Reiniciar importação PDF"
    ):
        resetar_importacao_pdf()

        st.rerun()

    st.divider()

    etapa = st.session_state.get(
        "pdf_etapa",
        "upload"
    )

    if etapa == "upload":
        render_upload_pdf()

    elif etapa == "confirmar_dados":
        render_confirmar_dados()

    elif etapa == "identificar_questoes":
        render_identificar_questoes()

    elif etapa == "revisar_questoes":
        render_revisar_questoes()