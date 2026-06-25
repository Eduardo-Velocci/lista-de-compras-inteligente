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

@st.cache_resource(ttl='10min') # se mandar a msm nota fiscal em ate 10 minutos, não vai gerar novamente (pra não jogar tokens no lixo)
def process_nf(prompt, resposta_template, produtos, img_file):
    st.image(open_img)
    prompt_exec = prompt.format(produtos="\n" .join(produtos), resposta=resposta_template ) 
    resp = generate(prompt_exec, img_file.getvalue(),img_file.type)
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


st.set_page_config(page_title="Lista de Compras")

st.markdown("# Lista de Compras Inteligente")

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

elif df_compra.empty:
    st.success(f"Não há produtos que precisam ser comprados considerando {numero_dias_adiante} dias.")

else:
    st.dataframe(df_compra)

st.markdown("## Adcionar Compra")

tab_produto, tab_historico, tab_nota_fiscal = st.tabs(["Produtos", "Histórico de Compras", "Nota Fiscal"])

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
        st.success("Compra do Produto Registrada com Sucesso!")


with tab_historico:
    st.markdown("### Importar Histórico de Compras")

    open_file = st.file_uploader("Escolha um arquivo Histórico", type="csv")

    if open_file:
        df = pd.read_csv(open_file)
        df = st.data_editor(df)
        
        if st.button("Salvar Histórico de Compras"):
            df.to_sql("compras", engine, if_exists="append", index=False)
            st.success("Histórico de Compras Salvo com Sucesso!")

with tab_nota_fiscal:
    st.markdown("### Importar Nota Fiscal")
    open_img = st.file_uploader("Envie uma Nota Fiscal", type=["png", "jpeg"])

    if open_img:
        df = process_nf(prompt=prompt, resposta_template=resposta, produtos=produtos, img_file=open_img)
        df = st.data_editor(df)

        if st.button("Registrar Dados"):
            df.to_sql("compras", engine, if_exists="append", index=False)
            st.success("Histórico de Compras Salvo com Sucesso!")