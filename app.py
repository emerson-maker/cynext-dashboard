import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Pipeline de Vendas - CyNext", page_icon="🚀", layout="wide")

# CSS customizado
st.markdown("""
    <style>
        .metric-card { background-color: #1e1e2e; border-radius: 10px; padding: 20px; }
        .stMetric { background-color: #1e1e2e; border-radius: 10px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# Conexão
url = "https://avbmvgdznnircllxigrb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF2Ym12Z2R6bm5pcmNsbHhpZ3JiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczODg2MzYsImV4cCI6MjA5Mjk2NDYzNn0.ilfyH9MlHgFVxs8ix9q57rJrsN__mSKRJoAGsyztMoY"
supabase = create_client(url, key)

# Dados
response = supabase.table("leads").select("*").execute()
df = pd.DataFrame(response.data) if response.data else pd.DataFrame()

# Header
st.title("🚀 Pipeline de Vendas - CyNext")
st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

if df.empty:
    st.info("Nenhum lead encontrado. Envie dados via n8n primeiro!")
    st.stop()

# Prepara dados
if "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["data"] = df["created_at"].dt.date

if "status" not in df.columns:
    df["status"] = "novo"

if "custo_lead" not in df.columns:
    df["custo_lead"] = 0

if "cidade" not in df.columns:
    df["cidade"] = "Não informada"

# ── KPIs ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total = len(df)
convertidos = len(df[df["status"] == "convertido"]) if "status" in df.columns else 0
taxa = round((convertidos / total) * 100, 1) if total > 0 else 0
custo_medio = round(df["custo_lead"].mean(), 2) if "custo_lead" in df.columns else 0

col1.metric("📋 Total de Leads", total)
col2.metric("✅ Convertidos", convertidos)
col3.metric("📈 Taxa de Conversão", f"{taxa}%")
col4.metric("💰 Custo Médio por Lead", f"R$ {custo_medio}")

st.markdown("---")

# ── GRÁFICOS ──────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Leads por Origem")
    if "origem" in df.columns:
        origem_count = df["origem"].value_counts().reset_index()
        origem_count.columns = ["origem", "total"]
        fig1 = px.pie(origem_count, values="total", names="origem",
                      color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("🔄 Status do Pipeline")
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["status", "total"]
    fig2 = px.bar(status_count, x="status", y="total",
                  color="status", color_discrete_sequence=px.colors.sequential.Viridis)
    st.plotly_chart(fig2, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("📅 Leads por Dia")
    if "data" in df.columns:
        leads_dia = df.groupby("data").size().reset_index(name="total")
        fig3 = px.line(leads_dia, x="data", y="total", markers=True,
                       color_discrete_sequence=["#7c3aed"])
        st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("🌎 Leads por Cidade")
    cidade_count = df["cidade"].value_counts().reset_index()
    cidade_count.columns = ["cidade", "total"]
    fig4 = px.bar(cidade_count, x="cidade", y="total",
                  color_discrete_sequence=["#06b6d4"])
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── TABELA COMPLETA ───────────────────────────────────
st.subheader("📋 Lista Completa de Leads")

# Filtros
col_f1, col_f2 = st.columns(2)
with col_f1:
    if "origem" in df.columns:
        origens = ["Todas"] + df["origem"].dropna().unique().tolist()
        filtro_origem = st.selectbox("Filtrar por origem:", origens)
        if filtro_origem != "Todas":
            df = df[df["origem"] == filtro_origem]

with col_f2:
    status_opts = ["Todos"] + df["status"].dropna().unique().tolist()
    filtro_status = st.selectbox("Filtrar por status:", status_opts)
    if filtro_status != "Todos":
        df = df[df["status"] == filtro_status]

st.dataframe(df, use_container_width=True)py -m pip install plotly