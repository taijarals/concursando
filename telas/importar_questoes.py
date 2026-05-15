import streamlit as st

from database.supabase_client import supabase

from services.openrouter_service import pesquisar_questoes


# ==================================================
# TELA
# ==================================================

def tela_importacao():

    user = st.session_state.user

    st.title(
        "🤖 Importar Questões com IA"
    )

    # =====================================
    # FORMULÁRIO
    # =====================================

    instituicao = st.text_input(
        "Instituição"
    )

    cargo = st.text_input(
        "Cargo"
    )

    banca = st.text_input(
        "Banca"
    )

    ano = st.number_input(
        "Ano",
        min_value=2000,
        max_value=2100,
        value=2024
    )

    disciplina = st.text_input(
        "Disciplina"
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
    # GERAR
    # =====================================

    if st.button(
        "Pesquisar Questões"
    ):

        with st.spinner(
            "Pesquisando questões..."
        ):

            try:

                questoes = pesquisar_questoes(
                    instituicao,
                    banca,
                    cargo,
                    ano,
                    disciplina,
                    tipo
                )

                st.session_state[
                    "questoes_ia"
                ] = questoes

            except Exception as e:

                st.error(str(e))

    # =====================================
    # EXIBIR QUESTÕES
    # =====================================

    if "questoes_ia" in st.session_state:

        questoes = st.session_state[
            "questoes_ia"
        ]

        st.divider()

        st.subheader(
            "Questões Encontradas"
        )

        for i, questao in enumerate(questoes):

            with st.expander(
                f"Questão {i + 1}"
            ):

                st.write(
                    f"**Enunciado:** "
                    f"{questao['enunciado']}"
                )

                st.write(
                    f"**Cargo:** "
                    f"{cargo}"
                )

                st.write(
                    f"**Resposta:** "
                    f"{questao['resposta_correta']}"
                )

                st.write(
                    f"**Assunto:** "
                    f"{questao['assunto']}"
                )

                st.write(
                    f"**Dificuldade:** "
                    f"{questao['dificuldade']}"
                )

                if (
                    questao["tipo"]
                    == "multipla_escolha"
                ):

                    st.subheader(
                        "Alternativas"
                    )

                    for alt in questao[
                        "alternativas"
                    ]:

                        st.write(
                            f"{alt['letra']}) "
                            f"{alt['texto']}"
                        )

                st.subheader(
                    "Explicação IA"
                )

                st.info(
                    questao[
                        "explicacao_ia"
                    ]
                )

        # =====================================
        # IMPORTAR
        # =====================================

        if st.button(
            "Importar Todas"
        ):

            try:

                for questao in questoes:

                    # =====================
                    # NORMALIZAR TEXTO
                    # =====================

                    materia_nome = (
                        questao["materia"]
                        .upper()
                        .strip()
                    )

                    assunto_nome = (
                        questao["assunto"]
                        .upper()
                        .strip()
                    )

                    banca_nome = (
                        questao["banca"]
                        .upper()
                        .strip()
                    )

                    # =====================
                    # BUSCAR MATÉRIA
                    # =====================

                    materia = (
                        supabase
                        .table(
                            "concur_materias"
                        )
                        .select("*")
                        .eq(
                            "nome",
                            materia_nome
                        )
                        .execute()
                    )

                    if materia.data:

                        materia_id = (
                            materia.data[0]["id"]
                        )

                    else:

                        nova = (
                            supabase
                            .table(
                                "concur_materias"
                            )
                            .insert({
                                "nome":
                                    materia_nome
                            })
                            .execute()
                        )

                        materia_id = (
                            nova.data[0]["id"]
                        )

                    # =====================
                    # BUSCAR BANCA
                    # =====================

                    banca_db = (
                        supabase
                        .table(
                            "concur_bancas"
                        )
                        .select("*")
                        .eq(
                            "nome",
                            banca_nome
                        )
                        .execute()
                    )

                    if banca_db.data:

                        banca_id = (
                            banca_db.data[0]["id"]
                        )

                    else:

                        nova = (
                            supabase
                            .table(
                                "concur_bancas"
                            )
                            .insert({
                                "nome":
                                    banca_nome
                            })
                            .execute()
                        )

                        banca_id = (
                            nova.data[0]["id"]
                        )

                    # =====================
                    # ASSUNTO
                    # =====================

                    assunto = (
                        supabase
                        .table(
                            "concur_assuntos"
                        )
                        .select("*")
                        .eq(
                            "nome",
                            assunto_nome
                        )
                        .eq(
                            "materia_id",
                            materia_id
                        )
                        .execute()
                    )

                    if assunto.data:

                        assunto_id = (
                            assunto.data[0]["id"]
                        )

                    else:

                        novo = (
                            supabase
                            .table(
                                "concur_assuntos"
                            )
                            .insert({

                                "nome":
                                    assunto_nome,

                                "materia_id":
                                    materia_id
                            })
                            .execute()
                        )

                        assunto_id = (
                            novo.data[0]["id"]
                        )

                    # =====================
                    # SALVAR QUESTÃO
                    # =====================

                    response = (
                        supabase
                        .table(
                            "concur_questoes"
                        )
                        .insert({

                            "tipo":
                                questao["tipo"],

                            "enunciado":
                                questao["enunciado"],

                            "materia_id":
                                materia_id,

                            "assunto_id":
                                assunto_id,

                            "banca_id":
                                banca_id,

                            "cargo":
                                cargo.upper(),

                            "dificuldade":
                                questao[
                                    "dificuldade"
                                ],

                            "explicacao_ia":
                                questao[
                                    "explicacao_ia"
                                ],

                            "resposta_correta":
                                questao[
                                    "resposta_correta"
                                ],

                            "fonte":
                                questao[
                                    "fonte"
                                ],

                            "criado_por":
                                user.id
                        })
                        .execute()
                    )

                    questao_id = (
                        response.data[0]["id"]
                    )

                    # =====================
                    # ALTERNATIVAS
                    # =====================

                    if (
                        questao["tipo"]
                        == "multipla_escolha"
                    ):

                        for alt in questao[
                            "alternativas"
                        ]:

                            (
                                supabase
                                .table(
                                    "concur_alternativas"
                                )
                                .insert({

                                    "questao_id":
                                        questao_id,

                                    "letra":
                                        alt[
                                            "letra"
                                        ],

                                    "texto":
                                        alt[
                                            "texto"
                                        ],

                                    "correta":
                                        alt[
                                            "correta"
                                        ]
                                })
                                .execute()
                            )

                st.success(
                    "Questões importadas com sucesso!"
                )

                del st.session_state[
                    "questoes_ia"
                ]

                st.rerun()

            except Exception as e:

                st.error(str(e))