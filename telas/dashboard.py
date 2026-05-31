import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.supabase_client import supabase
from datetime import datetime, timedelta
import random

# ==============================================================================
# CSS CUSTOMIZADO PARA VISUAL PREMIUM
# ==============================================================================
def injetar_css_dashboard():
    st.markdown("""
        <style>
        /* Estilos dos KPI Cards */
        .metric-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-bottom: 15px;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.15);
            border-color: #4f46e5;
        }
        .metric-card.total { border-top: 4px solid #3b82f6; }
        .metric-card.correct { border-top: 4px solid #10b981; }
        .metric-card.streak { border-top: 4px solid #f59e0b; }
        .metric-card.difficulty { border-top: 4px solid #8b5cf6; }

        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8fafc;
            font-family: 'Outfit', 'Inter', sans-serif;
        }

        /* Estilos dos Cards de Recomendação */
        .recom-card {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 12px;
            border: 1px solid #334155;
        }
        .recom-card.strong { border-left: 5px solid #10b981; }
        .recom-card.weak { border-left: 5px solid #ef4444; }
        .recom-title {
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 5px;
            color: #f8fafc;
        }
        .recom-subtitle {
            font-size: 0.85rem;
            color: #94a3b8;
        }
        </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# BUSCA DE DADOS E GERAÇÃO DE MOCK DATA
# ==============================================================================
def buscar_resolucoes(user_id):
    try:
        response = (
            supabase
            .table("concur_resolucoes")
            .select("""
                *,
                concur_questoes (
                    id,
                    tipo,
                    dificuldade,
                    materia_id,
                    concur_materias (nome),
                    assunto_id,
                    concur_assuntos (nome),
                    banca_id,
                    concur_bancas (nome)
                )
            """)
            .eq("user_id", user_id)
            .order("respondida_em", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}")
        return []


def obter_dados_exemplo():
    """Gera dados simulados de alta fidelidade para fins de demonstração"""
    hoje = datetime.now()
    materias_nomes = ["Língua Portuguesa", "Direito Constitucional", "Direito Administrativo", "Raciocínio Lógico", "Informática"]
    bancas_nomes = ["Cebraspe", "FCC", "Cesgranrio", "Vunesp"]
    assuntos_por_materia = {
        "Língua Portuguesa": ["Sintaxe", "Interpretação de Texto", "Pontuação", "Ortografia"],
        "Direito Constitucional": ["Direitos Fundamentais", "Poder Legislativo", "Organização do Estado"],
        "Direito Administrativo": ["Atos Administrativos", "Agentes Públicos", "Licitações e Contratos"],
        "Raciocínio Lógico": ["Proposições e Conectivos", "Lógica de Argumentação", "Probabilidade"],
        "Informática": ["Segurança da Informação", "Redes de Computadores", "Planilhas Eletrônicas"]
    }
    
    mock_data = []
    random.seed(42)  # Manter geração determinística
    
    # Gerar 60 resoluções distribuídas nos últimos 12 dias
    for i in range(60):
        dias_atras = random.randint(0, 11)
        data_tentativa = hoje - timedelta(days=dias_atras, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        materia = random.choice(materias_nomes)
        assunto = random.choice(assuntos_por_materia[materia])
        banca = random.choice(bancas_nomes)
        dificuldade = random.choice([1, 2, 3, 4, 5])
        tipo = random.choice(["multipla_escolha", "certo_errado"])
        
        # Simular uma taxa de acertos realista
        acerto_prob = 0.78 if materia in ["Língua Portuguesa", "Direito Constitucional"] else 0.55
        acertou = random.random() < acerto_prob
        
        mock_data.append({
            "id": 2000 + i,
            "respondida_em": data_tentativa.isoformat(),
            "resposta_usuario": random.choice(["A", "B", "C", "D"]) if tipo == "multipla_escolha" else random.choice(["Certo", "Errado"]),
            "acertou": acertou,
            "concur_questoes": {
                "id": 800 + i,
                "tipo": tipo,
                "dificuldade": dificuldade,
                "concur_materias": {"nome": materia},
                "concur_assuntos": {"nome": assunto},
                "concur_bancas": {"nome": banca}
            }
        })
        
    return mock_data


# ==============================================================================
# REGRAS E MÉTRICAS DE NEGÓCIO
# ==============================================================================
def calcular_streak(datas_resolucao):
    if not datas_resolucao:
        return 0
    
    dates = []
    for d in datas_resolucao:
        try:
            dt = datetime.fromisoformat(d.replace('Z', '+00:00')).date()
            dates.append(dt)
        except Exception:
            try:
                dt = datetime.strptime(d[:10], "%Y-%m-%d").date()
                dates.append(dt)
            except Exception:
                pass
                
    dates = sorted(list(set(dates)), reverse=True)
    if not dates:
        return 0
        
    hoje = datetime.now().date()
    ontem = hoje - timedelta(days=1)
    
    if hoje in dates:
        streak_start = hoje
    elif ontem in dates:
        streak_start = ontem
    else:
        return 0
        
    streak = 0
    current = streak_start
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
        
    return streak


# ==============================================================================
# TEMA DOS GRÁFICOS (PLOTLY DARK / MODERN)
# ==============================================================================
def aplicar_tema_grafico(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family="Outfit, Inter, sans-serif"),
        title=dict(font=dict(size=15, weight="bold", color="#f8fafc")),
        margin=dict(t=50, b=30, l=35, r=20),
        xaxis=dict(
            gridcolor="#334155",
            zerolinecolor="#334155",
            tickfont=dict(color="#94a3b8")
        ),
        yaxis=dict(
            gridcolor="#334155",
            zerolinecolor="#334155",
            tickfont=dict(color="#94a3b8")
        )
    )
    return fig


# ==============================================================================
# TELA PRINCIPAL DO DASHBOARD
# ==============================================================================
def tela_dashboard():
    injetar_css_dashboard()
    
    # Cabeçalho
    st.markdown('<h1 style="margin-bottom:0px;">📊 Painel de Desempenho</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; font-size:0.95rem; margin-bottom:25px;">Monitore suas estatísticas de estudo, evolução diária e taxa de acertos.</p>', unsafe_allow_html=True)

    # Identificar usuário ativo
    user = st.session_state.get("user")
    if not user:
        st.warning("Usuário não autenticado. Por favor, faça login.")
        return

    # Buscar dados no banco
    resolucoes = buscar_resolucoes(user.id)
    modo_demo = False

    # Tratamento para ausência de dados
    if not resolucoes:
        with st.container(border=True):
            st.markdown("### Bem-vindo ao Concurso AI! 🚀")
            st.write(
                "Parece que você ainda não resolveu nenhuma questão no sistema. "
                "Para visualizar suas estatísticas de desempenho, navegue até a tela **'Resolver Questões'** no menu."
            )
            
            # Switch para modo de simulação
            modo_demo = st.toggle("💡 Ativar Modo de Demonstração (Exibir dados de exemplo)", value=True)
            
            if modo_demo:
                resolucoes = obter_dados_exemplo()
                st.info("Visualizando painel em modo de demonstração com dados de exemplo.")
            else:
                return

    # ==============================================================================
    # PROCESSAMENTO DE DADOS (PANDAS DATAFRAME)
    # ==============================================================================
    flat_data = []
    for r in resolucoes:
        q = r.get("concur_questoes") or {}
        mat = q.get("concur_materias") or {}
        ass = q.get("concur_assuntos") or {}
        ban = q.get("concur_bancas") or {}
        
        flat_data.append({
            "id_resolucao": r["id"],
            "respondida_em": r["respondida_em"],
            "resposta_usuario": r["resposta_usuario"],
            "acertou": r["acertou"],
            "questao_id": q.get("id"),
            "tipo": q.get("tipo", "Não informado"),
            "dificuldade": q.get("dificuldade", 3),
            "materia": mat.get("nome", "Geral"),
            "assunto": ass.get("nome", "Não classificado"),
            "banca": ban.get("nome", "Não informada")
        })

    df = pd.DataFrame(flat_data)
    
    # Tratamento de datas
    df["data_formatada"] = pd.to_datetime(df["respondida_em"]).dt.date

    # Métricas Principais
    total_resolvidas = len(df)
    total_acertos = df["acertou"].sum()
    taxa_acerto = (total_acertos / total_resolvidas * 100) if total_resolvidas > 0 else 0
    dificuldade_media = df["dificuldade"].mean()
    streak = calcular_streak(df["respondida_em"].tolist())

    # ==============================================================================
    # RENDERIZAÇÃO DOS KPI CARDS
    # ==============================================================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card total">
                <div class="metric-label">Questões Resolvidas</div>
                <div class="metric-value">{total_resolvidas}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card correct">
                <div class="metric-label">Taxa de Acertos</div>
                <div class="metric-value">{taxa_acerto:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card streak">
                <div class="metric-label">Ofensiva (Dias)</div>
                <div class="metric-value">🔥 {streak}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card difficulty">
                <div class="metric-label">Dificuldade Média</div>
                <div class="metric-value">⚙️ {dificuldade_media:.1f}/5</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==============================================================================
    # SEÇÃO DE GRÁFICOS (Layout de duas colunas)
    # ==============================================================================
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # Gráfico 1: Desempenho por Matéria
        df_mat = df.groupby("materia").agg(
            total=("acertou", "count"),
            acertos=("acertou", "sum")
        ).reset_index()
        df_mat["taxa_acerto"] = (df_mat["acertos"] / df_mat["total"] * 100).round(1)
        df_mat = df_mat.sort_values(by="taxa_acerto", ascending=True)

        fig_mat = px.bar(
            df_mat,
            x="taxa_acerto",
            y="materia",
            orientation="h",
            text=df_mat["taxa_acerto"].apply(lambda x: f"{x}%"),
            color="taxa_acerto",
            color_continuous_scale=["#ef4444", "#3b82f6", "#10b981"],
            labels={"taxa_acerto": "Taxa de Acerto (%)", "materia": "Matéria"},
            title="Taxa de Acerto por Matéria"
        )
        fig_mat.update_layout(xaxis=dict(range=[0, 100]))
        fig_mat.update_traces(textposition='inside', insidetextanchor='end')
        fig_mat.update_coloraxes(showscale=False)
        st.plotly_chart(aplicar_tema_grafico(fig_mat), use_container_width=True)

    with col_g2:
        # Gráfico 2: Evolução Temporal
        df_evo = df.groupby("data_formatada").agg(
            Resolvidas=("acertou", "count"),
            Acertos=("acertou", "sum")
        ).reset_index().sort_values(by="data_formatada")

        fig_evo = go.Figure()
        fig_evo.add_trace(go.Scatter(
            x=df_evo["data_formatada"],
            y=df_evo["Resolvidas"],
            mode="lines+markers",
            name="Resolvidas",
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=6, symbol="circle")
        ))
        fig_evo.add_trace(go.Scatter(
            x=df_evo["data_formatada"],
            y=df_evo["Acertos"],
            mode="lines+markers",
            name="Acertos",
            line=dict(color="#10b981", width=3),
            marker=dict(size=6, symbol="x")
        ))
        fig_evo.update_layout(
            title="Evolução Diária de Estudos",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(aplicar_tema_grafico(fig_evo), use_container_width=True)

    # Segunda fileira de gráficos
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        # Gráfico 3: Distribuição por Banca
        df_ban = df.groupby("banca").size().reset_index(name="Quantidade")
        fig_ban = px.pie(
            df_ban,
            values="Quantidade",
            names="banca",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Dark24,
            title="Distribuição por Banca"
        )
        fig_ban.update_traces(textinfo="percent+label", textposition="inside")
        fig_ban.update_layout(showlegend=False)
        st.plotly_chart(aplicar_tema_grafico(fig_ban), use_container_width=True)

    with col_g4:
        # Gráfico 4: Taxa de Acertos e Erros por Dificuldade
        df_dif = df.groupby(["dificuldade", "acertou"]).size().reset_index(name="Quantidade")
        df_dif["Resultado"] = df_dif["acertou"].map({True: "Acertou", False: "Errou"})
        
        # Garantir ordenação correta das dificuldades
        df_dif = df_dif.sort_values("dificuldade")

        fig_dif = px.bar(
            df_dif,
            x="dificuldade",
            y="Quantidade",
            color="Resultado",
            color_discrete_map={"Acertou": "#10b981", "Errou": "#ef4444"},
            barmode="stack",
            labels={"dificuldade": "Dificuldade (1-5)", "Quantidade": "Qtd Questões"},
            title="Acertos vs Erros por Dificuldade"
        )
        st.plotly_chart(aplicar_tema_grafico(fig_dif), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================================================================
    # SEÇÃO DE RECOMENDAÇÕES E ASSUNTOS
    # ==============================================================================
    st.subheader("💡 Recomendações e Foco de Estudos")
    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.write("**Matérias para Reforçar 📚**")
        st.write("Foque nas disciplinas com rendimento inferior a 70%:")
        
        materias_fracas = df_mat[df_mat["taxa_acerto"] < 70.0].sort_values("taxa_acerto")
        if not materias_fracas.empty:
            for _, row in materias_fracas.head(3).iterrows():
                st.markdown(f"""
                    <div class="recom-card weak">
                        <div class="recom-title">{row['materia']}</div>
                        <div class="recom-subtitle">Rendimento de {row['taxa_acerto']}% • Resolvidas: {row['total']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Excelente! Nenhuma matéria com rendimento abaixo de 70%. Continue assim!")

    with col_rec2:
        st.write("**Tópicos Dominados 🏆**")
        st.write("Continue revisando, mas você já possui alto rendimento nestas áreas:")
        
        materias_fortes = df_mat[df_mat["taxa_acerto"] >= 80.0].sort_values("taxa_acerto", ascending=False)
        if not materias_fortes.empty:
            for _, row in materias_fortes.head(3).iterrows():
                st.markdown(f"""
                    <div class="recom-card strong">
                        <div class="recom-title">{row['materia']}</div>
                        <div class="recom-subtitle">Rendimento de {row['taxa_acerto']}% • Resolvidas: {row['total']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Resolva mais questões para identificar seus pontos fortes com maior precisão.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================================================================
    # TABELA DE HISTÓRICO RECENTE
    # ==============================================================================
    st.subheader("📋 Histórico Recente de Resoluções")
    
    # Selecionar as últimas 10 e exibir de forma amigável
    recentes = df.head(10).copy()
    
    # Formatação visual amigável do status de acerto
    recentes["Resultado"] = recentes["acertou"].apply(lambda x: "✅ Acertou" if x else "❌ Errou")
    recentes["Data/Hora"] = pd.to_datetime(recentes["respondida_em"]).dt.strftime("%d/%m/%Y %H:%M")
    
    # Renomear e ordenar colunas para exibição
    recentes_view = recentes[[
        "Data/Hora", 
        "questao_id", 
        "materia", 
        "banca", 
        "resposta_usuario", 
        "Resultado"
    ]].rename(columns={
        "questao_id": "ID Questão",
        "materia": "Matéria",
        "banca": "Banca",
        "resposta_usuario": "Sua Resposta"
    })
    
    # Exibir no Streamlit
    st.dataframe(
        recentes_view,
        use_container_width=True,
        hide_index=True
    )