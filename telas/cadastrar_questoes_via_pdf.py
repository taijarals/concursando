from io import BytesIO

import streamlit as st

from database.supabase_client import supabase
from services.pdf_service import extrair_paginas_pdf
from services.prova_pdf_parser import identificar_dados_prova
from services.questao_pdf_parser import (
    extrair_questoes_pagina_texto,
    extrair_questoes_pdf_gemini
)


def inicializar_estado_pdf():
    if "pdf_etapa" not in st.session_state:
        st.session_state["pdf_etapa"] = "upload"
    
    if "pdf_modo_processamento" not in st.session_state:
        st.session_state["pdf_modo_processamento"] = "pagina_por_pagina"
    
    if "pdf_modelo_ia" not in st.session_state:
        st.session_state["pdf_modelo_ia"] = "gemini"
    
    if "pdf_questao_editando" not in st.session_state:
        st.session_state["pdf_questao_editando"] = None


def resetar_importacao_pdf():
    chaves = [
        "pdf_etapa",
        "pdf_paginas",
        "pdf_dados",
        "pdf_dados_confirmados",
        "pdf_questoes",
        "pdf_bytes",
        "pdf_nome",
        "pdf_modo_processamento",
        "pdf_pagina_atual",
        "pdf_questoes_por_pagina",
        "pdf_modelo_ia",
        "pdf_questao_editando"
    ]

    for chave in chaves:
        st.session_state.pop(chave, None)

    st.session_state["pdf_etapa"] = "upload"


def normalizar_nome(valor, padrao):
    texto = str(valor or "").strip().upper()

    if texto:
        return texto

    return padrao

def montar_tags_metadados(questao, dados_prova):
    tags = []

    for tag in questao.get("tags") or []:
        tag_texto = str(tag or "").strip()

        if tag_texto:
            tags.append(tag_texto)

    metadados = {
        "cargo": questao.get("cargo") or dados_prova.get("cargo"),
        "instituicao": dados_prova.get("instituicao"),
        "ano": dados_prova.get("ano")
    }

    for chave, valor in metadados.items():
        valor_texto = str(valor or "").strip().upper()

        if valor_texto:
            tag = f"{chave}: {valor_texto}"

            if tag not in tags:
                tags.append(tag)

    return tags


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
    user,
    dados_prova
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
             "tags": montar_tags_metadados(
                questao,
                dados_prova
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
    user,
    dados_prova
):
    ids_importados = []

    for questao in questoes:
        questao_id = salvar_questao_pdf(
            questao,
            user,
            dados_prova
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

    st.info(
        "💡 **Dica:** O sistema processará o PDF página por página "
        "para economizar tokens da IA. Você poderá revisar e editar as questões "
        "encontradas em cada página antes de importar."
    )

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
                    f"PDF analisado com sucesso! ({len(paginas)} páginas)"
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
        ] = "escolher_modelo"

        st.success("Dados confirmados!")

        st.rerun()


def render_escolher_modelo():
    """Permite escolher o modelo de IA a ser utilizado"""
    st.subheader("3. Escolher Modelo de IA")

    st.write(
        "Qual modelo de IA você deseja usar para extrair as questões?"
    )

    modelo = st.radio(
        "Modelo de IA",
        options=[
            "gemini",
            "deepseek"
        ],
        format_func=lambda x: {
            "gemini": "🔵 Gemini 2.0 Flash (Google)",
            "deepseek": "🟣 Deepseek (OpenRouter)"
        }[x],
        key="modelo_ia_selector"
    )

    st.divider()

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown("### 🔵 Gemini 2.0 Flash")
        st.write(
            "- Modelo: Google Gemini\n"
            "- Requer: GEMINI_API_KEY\n"
            "- Limite: Free tier limitado\n"
            "- Velocidade: Rápido"
        )

    with col_info2:
        st.markdown("### 🟣 Deepseek")
        st.write(
            "- Modelo: Deepseek via OpenRouter\n"
            "- Requer: OPENROUTER_API_KEY\n"
            "- Limite: Conforme plano\n"
            "- Velocidade: Rápido"
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Voltar"):
            st.session_state["pdf_etapa"] = "confirmar_dados"
            st.rerun()

    with col2:
        if st.button("Continuar"):
            st.session_state["pdf_modelo_ia"] = modelo
            st.session_state["pdf_etapa"] = "escolher_modo"
            st.rerun()


def render_escolher_modo():
    """Permite escolher entre modo página por página ou tudo de uma vez"""
    st.subheader("4. Escolher modo de processamento")

    st.write(
        "Como você deseja processar as questões?"
    )

    modo = st.radio(
        "Modo de processamento",
        options=[
            "pagina_por_pagina",
            "tudo_de_uma_vez"
        ],
        format_func=lambda x: {
            "pagina_por_pagina": "📄 Página por Página (Economiza tokens)",
            "tudo_de_uma_vez": "⚡ Tudo de Uma Vez (Mais rápido)"
        }[x],
        key="modo_processamento_selector"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Voltar"):
            st.session_state["pdf_etapa"] = "escolher_modelo"
            st.rerun()

    with col2:
        if st.button("Continuar"):
            st.session_state["pdf_modo_processamento"] = modo
            st.session_state["pdf_pagina_atual"] = 0
            st.session_state["pdf_questoes_por_pagina"] = {}

            if modo == "pagina_por_pagina":
                st.session_state["pdf_etapa"] = "processar_pagina"
            else:
                st.session_state["pdf_etapa"] = "processar_tudo"

            st.rerun()


def render_processar_pagina():
    """Processa página por página"""
    st.subheader("5. Processar Questões (Página por Página)")

    paginas = st.session_state.get("pdf_paginas", [])
    pagina_atual = st.session_state.get("pdf_pagina_atual", 0)
    questoes_por_pagina = st.session_state.get(
        "pdf_questoes_por_pagina",
        {}
    )
    dados = st.session_state.get(
        "pdf_dados_confirmados",
        {}
    )
    modelo_ia = st.session_state.get(
        "pdf_modelo_ia",
        "gemini"
    )

    if pagina_atual >= len(paginas):
        st.session_state["pdf_etapa"] = "revisar_questoes"
        st.rerun()
        return

    pagina = paginas[pagina_atual]
    numero_pagina = pagina["numero"]
    texto_pagina = pagina["texto"]

    st.write(
        f"Processando página **{numero_pagina}** de **{len(paginas)}** usando **{modelo_ia.upper()}**"
    )

    progress = st.progress(
        (pagina_atual + 1) / len(paginas)
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.write(f"**Progresso:** {pagina_atual + 1}/{len(paginas)} páginas")

    with col2:
        if st.button("⏭️ Pular"):
            st.session_state["pdf_pagina_atual"] = pagina_atual + 1
            st.rerun()

    with col3:
        if st.button("⬅️ Voltar"):
            st.session_state["pdf_etapa"] = "escolher_modo"
            st.rerun()

    if numero_pagina not in questoes_por_pagina:
        with st.spinner(
            f"Analisando página {numero_pagina} com {modelo_ia}..."
        ):
            try:
                questoes = extrair_questoes_pagina_texto(
                    texto_pagina,
                    numero_pagina,
                    dados,
                    modelo_ia=modelo_ia
                )

                questoes_por_pagina[numero_pagina] = questoes

                st.session_state[
                    "pdf_questoes_por_pagina"
                ] = questoes_por_pagina

                if questoes:
                    st.success(
                        f"✓ {len(questoes)} questão(ões) encontrada(s)"
                    )
                else:
                    st.info("Nenhuma questão encontrada nesta página")

            except Exception as e:
                st.error(
                    f"Erro ao processar página {numero_pagina}: {e}"
                )

    questoes_pagina = questoes_por_pagina.get(
        numero_pagina,
        []
    )

    if questoes_pagina:
        st.subheader(f"Questões da Página {numero_pagina}")

        for idx, questao in enumerate(questoes_pagina, start=1):
            render_card_questao_editavel(
                questao,
                idx,
                numero_pagina,
                questoes_pagina
            )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("⬅️ Voltar (página anterior)"):
            if pagina_atual > 0:
                st.session_state["pdf_pagina_atual"] = pagina_atual - 1
                st.rerun()

    with col2:
        if st.button("⏭️ Próxima página"):
            st.session_state["pdf_pagina_atual"] = pagina_atual + 1
            st.rerun()

    with col3:
        if st.button("✅ Finalizar"):
            # Consolidar todas as questões
            todas_questoes = []
            for questoes_pag in questoes_por_pagina.values():
                todas_questoes.extend(questoes_pag)

            st.session_state["pdf_questoes"] = todas_questoes
            st.session_state["pdf_etapa"] = "revisar_questoes"
            st.rerun()


def render_processar_tudo():
    """Processa o PDF inteiro de uma vez (modo antigo)"""
    st.subheader("5. Processar PDF Completo")

    st.info(
        "⚠️ Modo 'Tudo de uma vez': O PDF inteiro será enviado para a IA. "
        "Isso pode usar mais tokens e ser mais lento."
    )

    dados = st.session_state.get(
        "pdf_dados_confirmados",
        {}
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Voltar"):
            st.session_state["pdf_etapa"] = "escolher_modo"
            st.rerun()

    with col2:
        if st.button(
            "🔎 Processar PDF Completo"
        ):
            with st.spinner(
                "Processando PDF completo..."
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
                        f"Erro ao processar: {e}"
                    )


def render_card_questao_editavel(questao, indice, numero_pagina, questoes_pagina):
    """Renderiza um card de questão com opção de editar"""
    
    # Verificar se há avisos
    avisos = questao.get("avisos", [])
    revisar = questao.get("revisar", False)
    
    # Título com indicador de aviso
    titulo_aviso = ""
    if avisos:
        titulo_aviso = " 🚩"
    
    titulo_expander = f"Questão {indice}: {questao.get('materia', 'Geral')} - {questao.get('enunciado', '')[:50]}...{titulo_aviso}"
    
    with st.expander(titulo_expander):
        # Mostrar avisos se houver
        if avisos:
            with st.container(border=True):
                st.warning("⚠️ **Avisos detectados:**")
                for aviso in avisos:
                    st.write(f"• {aviso}")
                st.divider()
        
        # Formulário editável
        col1, col2 = st.columns(2)
        
        with col1:
            materia_editada = st.text_input(
                "Matéria/Disciplina",
                value=questao.get("materia", ""),
                key=f"materia_{numero_pagina}_{indice}"
            )
            
            tipo_editado = st.selectbox(
                "Tipo de questão",
                options=["multipla_escolha", "certo_errado", "aberta"],
                index=["multipla_escolha", "certo_errado", "aberta"].index(
                    questao.get("tipo", "multipla_escolha")
                ),
                key=f"tipo_{numero_pagina}_{indice}"
            )
        
        with col2:
            assunto_editado = st.text_input(
                "Assunto específico",
                value=questao.get("assunto", ""),
                key=f"assunto_{numero_pagina}_{indice}"
            )
            
            dificuldade_editada = st.slider(
                "Dificuldade",
                min_value=1,
                max_value=5,
                value=questao.get("dificuldade", 3),
                key=f"dificuldade_{numero_pagina}_{indice}"
            )
        
        # Enunciado
        enunciado_editado = st.text_area(
            "Enunciado da questão",
            value=questao.get("enunciado", ""),
            height=100,
            key=f"enunciado_{numero_pagina}_{indice}"
        )
        
        # Alternativas (se múltipla escolha)
        if tipo_editado == "multipla_escolha":
            st.subheader("Alternativas")
            alternativas_editadas = []
            
            alternativas = questao.get("alternativas", [])
            
            # Se não tiver alternativas, criar 5 vazias
            if not alternativas:
                alternativas = [
                    {"letra": l, "texto": "", "correta": False}
                    for l in ["A", "B", "C", "D", "E"]
                ]
            
            for alt_idx, alternativa in enumerate(alternativas):
                col_alt1, col_alt2, col_alt3 = st.columns([0.5, 3, 0.5])
                
                with col_alt1:
                    st.write(f"**{alternativa.get('letra')})**")
                
                with col_alt2:
                    texto_alt = st.text_input(
                        f"Alternativa {alternativa.get('letra')}",
                        value=alternativa.get("texto", ""),
                        label_visibility="collapsed",
                        key=f"alt_texto_{numero_pagina}_{indice}_{alt_idx}"
                    )
                
                with col_alt3:
                    correta = st.checkbox(
                        "Correta",
                        value=alternativa.get("correta", False),
                        key=f"alt_correta_{numero_pagina}_{indice}_{alt_idx}"
                    )
                
                alternativas_editadas.append({
                    "letra": alternativa.get("letra"),
                    "texto": texto_alt,
                    "correta": correta
                })
            
            questao["alternativas"] = alternativas_editadas

            resposta_inferida = inferir_resposta_correta(
                questao
            )

            if resposta_inferida:
                questao["resposta_correta"] = (
                    resposta_inferida
                )
        
        # Campos adicionais
        col_extra1, col_extra2 = st.columns(2)
        
        with col_extra1:
            resposta_correta_editada = st.text_input(
                "Resposta correta (se aplicável)",
                value=questao.get("resposta_correta", ""),
                key=f"resposta_{numero_pagina}_{indice}"
            )
        
        with col_extra2:
            explicacao_editada = st.text_area(
                "Explicação/Gabarito",
                value=questao.get("explicacao_ia", "") or "",
                height=60,
                key=f"explicacao_{numero_pagina}_{indice}"
            )
        
        # Atualizar questão
        questao["materia"] = materia_editada
        questao["assunto"] = assunto_editado
        questao["tipo"] = tipo_editado
        questao["dificuldade"] = dificuldade_editada
        questao["enunciado"] = enunciado_editado
        questao["resposta_correta"] = resposta_correta_editada
        questao["explicacao_ia"] = explicacao_editada


def inferir_resposta_correta(questao):
    """Infere a letra correta com base nas alternativas marcadas."""
    alternativas = questao.get("alternativas") or []

    for alternativa in alternativas:
        if alternativa.get("correta"):
            letra = str(
                alternativa.get("letra") or ""
            ).strip().upper()[:1]

            if letra:
                return letra

    return ""


def render_dados_questao(questao):
    """Renderiza dados de uma questão (somente leitura)"""
    st.write(
        f"**Tipo:** {questao.get('tipo', '')}"
    )

    st.write(
        f"**Matéria:** {questao.get('materia', 'Não identificada')}"
    )

    st.write(
        f"**Assunto:** {questao.get('assunto', 'Não identificado')}"
    )

    st.write(
        f"**Enunciado:** {questao.get('enunciado', '')}"
    )

    if questao.get("pagina"):
        st.write(
            f"**Página:** {questao.get('pagina')}"
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
    st.subheader("6. Revisar e editar questões")

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
    
    st.info(
        "💡 Você pode editar qualquer informação das questões abaixo "
        "antes de importar para o banco de dados."
    )

    for indice, questao in enumerate(
        questoes,
        start=1
    ):
        render_card_questao_editavel(
            questao,
            indice,
            "revisar",
            questoes
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "⬅️ Voltar"
        ):
            modo = st.session_state.get(
                "pdf_modo_processamento"
            )

            if modo == "pagina_por_pagina":
                st.session_state[
                    "pdf_etapa"
                ] = "processar_pagina"
            else:
                st.session_state[
                    "pdf_etapa"
                ] = "processar_tudo"

            st.rerun()

    with col2:
        if st.button(
            "💾 Importar questões"
        ):
            try:
                user = st.session_state.user
                dados_prova = st.session_state.get(
                    "pdf_dados_confirmados",
                    {}
                )

                ids_importados = (
                    importar_questoes_extraidas(
                        questoes,
                        user,
                        dados_prova
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


def tela_cadastrar_questoes_via_pdf():
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

    elif etapa == "escolher_modelo":
        render_escolher_modelo()

    elif etapa == "escolher_modo":
        render_escolher_modo()

    elif etapa == "processar_pagina":
        render_processar_pagina()

    elif etapa == "processar_tudo":
        render_processar_tudo()

    elif etapa == "revisar_questoes":
        render_revisar_questoes()


def tela_importar_pdf():
    """Compatibilidade retroativa."""
    tela_cadastrar_questoes_via_pdf()
