import streamlit as st
import pandas as pd
import sqlalchemy
import datetime
import json

import os
import dotenv
dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

from gen_ai import generate



#Essa linha cria a conexão com o banco de dados (LOCAL)
engine = sqlalchemy.create_engine("sqlite:///database.db")

with open ("query_inteligente.sql") as query_file:
    query = query_file.read()

with open ("prompt_template.md") as prompt_file:
    prompt = prompt_file.read()

with open ("resposta_template.json") as resposta_file:
    resposta = json.load(resposta_file)

# A chave do cache é só a imagem (bytes + tipo): a mesma nota fiscal nunca é
# reenviada ao Gemini, mesmo que a lista de produtos mude entre re-execuções.
# O prefixo "_" no prompt o exclui da chave do cache.
@st.cache_data(show_spinner="Lendo nota fiscal com IA...")
def process_nf(img_bytes, img_mime, _prompt_exec):
    resp = generate(_prompt_exec, img_bytes, img_mime)
    df = pd.DataFrame(json.loads(resp.text))
    return df


def get_produtos(engine):
    try:   
        query = """SELECT DISTINCT produto FROM compras"""
        df = pd.read_sql(query, engine)
        return df["produto"].sort_values().tolist()
    except Exception as err:
        print(err)
        return []


st.set_page_config(
    page_title="Lista de Compras",
    page_icon="🛒",
    layout="centered",
)

st.markdown("# 🛒 Lista de Compras Inteligente")

produtos = get_produtos(engine)

try:

    col, _ = st.columns(2)
 
    numero_dias_adiante = col.number_input("Dias sem compras adiante",
                                          min_value=1,
                                          max_value=60,
                                          step=1)

    df_stats = pd.read_sql(query, engine)
    df_stats["comprar"] = df_stats["dias_ultima_compra"] + numero_dias_adiante > df_stats["avg_dif_dias"]
    df_compra = df_stats[df_stats["comprar"]]

except Exception as err:
    print("err")
    df_compra = pd.DataFrame()
    df_stats = pd.DataFrame()


if df_stats.empty:
    st.warning("Não há dados de compras no banco de dados. Por favor, importe um histórico de compras.")

else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Produtos cadastrados", len(df_stats))
    col2.metric("Precisam repor", len(df_compra))
    col3.metric("Valor médio", f"R$ {df_stats['avg_valor'].mean():.2f}")

    if df_compra.empty:
        st.success(f"Não há produtos que precisam ser comprados considerando {numero_dias_adiante} dias.")

    else:
        df_exibir = df_compra.copy()
        df_exibir["dt_ultima_compra"] = pd.to_datetime(df_exibir["dt_ultima_compra"])
        st.dataframe(
            df_exibir,
            column_config={
                "produto": "Produto",
                "dt_ultima_compra": st.column_config.DateColumn("Última compra", format="DD/MM/YYYY"),
                "avg_valor": st.column_config.NumberColumn("Valor médio", format="R$ %.2f"),
                "avg_dif_dias": st.column_config.NumberColumn("Intervalo médio (dias)", format="%.1f"),
                "dias_ultima_compra": st.column_config.ProgressColumn(
                    "Dias sem comprar",
                    format="%.0f",
                    min_value=0,
                    max_value=max(float(df_stats["dias_ultima_compra"].max()), 1.0),
                ),
                "comprar": None,
            },
            hide_index=True,
        )

st.markdown("## Adcionar Compra")

tab_produto, tab_historico, tab_nota_fiscal = st.tabs(["🛍️ Produtos", "📋 Histórico de Compras", "🧾 Nota Fiscal"])

with tab_produto:
    st.markdown("### Adcionar Produto")
    produto = st.selectbox("Produto", options= ["Novo Produto"] + produtos) 

    if produto == "Novo Produto":
        produto_novo = st.text_input("Inserir novo produto")
        produto = produto_novo

    valor = st.number_input("Valor", min_value=0.01, step=0.01)

    if st.button("Registrar compra"):
        data = {
                "dt_compra": datetime.datetime.now().strftime("%Y-%m-%d"),
                "produto": produto.title(),
                "valor_produto": valor,
                }
        df_insert = pd.DataFrame([data])
        df_insert.to_sql("compras", engine, if_exists="append", index=False)
        st.toast("Compra registrada!", icon="✅")
        st.success("Compra do Produto Registrada com Sucesso!")


with tab_historico:
    st.markdown("### Importar Histórico de Compras")

    open_file = st.file_uploader("Escolha um arquivo Histórico", type="csv")

    if open_file:
        df = pd.read_csv(open_file)
        df = st.data_editor(df)
        
        if st.button("Salvar Histórico de Compras"):
            df.to_sql("compras", engine, if_exists="append", index=False)
            st.toast("Histórico salvo!", icon="✅")
            st.success("Histórico de Compras Salvo com Sucesso!")

with tab_nota_fiscal:
    st.markdown("### Importar Nota Fiscal")
    open_img = st.file_uploader("Envie uma Nota Fiscal", type=["png", "jpeg"])

    if open_img:
        st.image(open_img)
        prompt_exec = prompt.format(produtos="\n".join(produtos), resposta=resposta)
        df = process_nf(open_img.getvalue(), open_img.type, prompt_exec)
        df = st.data_editor(df)

        if st.button("Registrar Dados"):
            df.to_sql("compras", engine, if_exists="append", index=False)
            st.toast("Nota fiscal registrada!", icon="✅")
            st.success("Histórico de Compras Salvo com Sucesso!")