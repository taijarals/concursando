import streamlit as st

from database.supabase_client import supabase

from services.openrouter_service import gerar_explicacao_questao


def tela_gerar_explicacoes_ia():

    st.title(
        "🤖 Gerador de Explicações IA"
    )

    questoes = (
        supabase
        .table(
            "concur_questoes"
        )
        .select("*")
        .or_(
            "explicacao_ia.is.null,comentario.is.null"
        )
        .execute()
    )

    total = len(
        questoes.data
    )

    st.metric(
        "Questões Pendentes",
        total
    )

    if total == 0:

        st.success(
            "Nenhuma questão pendente."
        )

        return

    if st.button(
        "Processar Questões"
    ):

        progress = st.progress(0)

        status = st.empty()

        erros = []

        for i, questao in enumerate(
            questoes.data
        ):

            try:

                status.info(
                    f"Processando questão "
                    f"{i+1}/{total}"
                )

                alternativas = (
                    supabase
                    .table(
                        "concur_alternativas"
                    )
                    .select("*")
                    .eq(
                        "questao_id",
                        questao["id"]
                    )
                    .execute()
                )

                resultado = (
                    gerar_explicacao_questao(
                        questao,
                        alternativas.data
                    )
                )

                (
                    supabase
                    .table(
                        "concur_questoes"
                    )
                    .update({

                        "explicacao_ia":
                            resultado[
                                "explicacao_ia"
                            ],

                        "comentario":
                            resultado[
                                "comentario"
                            ]

                    })
                    .eq(
                        "id",
                        questao["id"]
                    )
                    .execute()
                )

            except Exception as e:

                erros.append(
                    {
                        "id":
                            questao["id"],
                        "erro":
                            str(e)
                    }
                )

            progress.progress(
                (i + 1) / total
            )

        st.success(
            "Processamento concluído."
        )

        if erros:

            st.warning(
                f"{len(erros)} erro(s)"
            )

            st.json(erros)