# 🛒 Lista de Compras Inteligente

Aplicação em **Streamlit** que ajuda a decidir **o que precisa ser recomprado** com base no histórico de compras. Em vez de uma lista manual, o sistema analisa a frequência com que cada produto costuma ser comprado e avisa quando um item está prestes a "acabar" — comparando há quantos dias ele não é comprado com o intervalo médio entre compras daquele produto.

Além disso, permite registrar compras de três formas, incluindo a **leitura automática de notas fiscais por IA** (Google Gemini), que extrai produtos, valores e datas direto de uma foto do cupom.

---

## 🎯 Objetivo

- Manter um histórico de compras de produtos do dia a dia.
- Estimar a **periodicidade de compra** de cada produto (a cada quantos dias, em média, ele é comprado).
- Sugerir uma **lista de reposição**: produtos cujo tempo desde a última compra (mais uma margem de dias escolhida pelo usuário) já passou do intervalo médio.
- Facilitar a entrada de dados, inclusive **a partir de fotos de notas fiscais**, sem digitação manual.

---

## ⚙️ Como funciona

### 1. Banco de dados
Um banco **SQLite** local (`database.db`) guarda todas as compras numa tabela `compras` com os campos:

| campo | descrição |
|---|---|
| `dt_compra` | data da compra (YYYY-MM-DD) |
| `produto` | nome do produto |
| `valor_produto` | valor pago |

A conexão é feita com **SQLAlchemy** e a leitura/escrita com **pandas** (`read_sql` / `to_sql`).

### 2. A lógica de "o que comprar" (`query_inteligente.sql`)
Uma query SQL com CTEs faz o trabalho analítico:

- **`tb_lag`** — usa `LAG()` para pegar, em cada compra, a data da compra anterior do mesmo produto.
- **`tb_avg`** — calcula o **intervalo médio em dias** entre compras de cada produto (`avg_dif_dias`).
- **`tb_stats_produto`** — pega a **data da última compra** e o **valor médio** de cada produto.
- **Consulta final** — junta tudo e calcula `dias_ultima_compra` (`julianday('now') - última compra`).

No app, um produto entra na lista de reposição quando:

```
dias_ultima_compra + dias_adiante > intervalo_médio
```

O campo **"Dias sem compras adiante"** permite antecipar a lista (ex.: "o que vou precisar comprar considerando os próximos 7 dias?").

### 3. Entrada de dados (3 abas)
- **Produtos** — registra uma compra individual (produto + valor), com data de hoje.
- **Histórico de Compras** — importa um CSV completo de histórico (`dt_compra,produto,valor_produto`), editável antes de salvar.
- **Nota Fiscal** — envia uma foto (PNG/JPEG) de um cupom; a IA extrai os itens automaticamente e preenche uma tabela editável antes de gravar.

### 4. Extração por IA (`gen_ai.py`)
- Usa o SDK **`google-genai`** com o modelo **Gemini**.
- A imagem da nota e um **prompt estruturado** (`prompt_template.md`) são enviados juntos.
- O prompt instrui o modelo a extrair **nome do produto** (sem marca/medida/quantidade), **valor unitário** (ou total, se vendido por kg/g) e **data**, retornando **JSON** no formato de `resposta_template.json`.
- A lista de produtos já existentes é injetada no prompt para padronizar os nomes.
- O resultado é convertido em `DataFrame` e exibido para revisão antes de salvar.

> 💡 A função de extração tem cache de **10 minutos** (`@st.cache_resource`): reenviar a mesma nota nesse intervalo não gasta tokens da API novamente.

---

## 📁 Estrutura do projeto

```
lista_compras/
├── main.py                  # App Streamlit (UI + lógica)
├── gen_ai.py                # Integração com o Gemini (extração de NF)
├── query_inteligente.sql    # Query analítica de reposição
├── prompt_template.md       # Template do prompt enviado à IA
├── resposta_template.json   # Formato esperado da resposta da IA
├── init_data.csv            # Dados iniciais de exemplo
├── database.db              # Banco SQLite (gerado/local)
└── .env                     # Chave da API (não versionar)
```

---

## 🚀 Como rodar

### 1. Pré-requisitos
- Python 3.12+ (o projeto foi desenvolvido em um ambiente **conda** chamado `lista-app`)
- Uma chave de API do **Google Gemini**

### 2. Instalar dependências
```bash
pip install streamlit pandas sqlalchemy python-dotenv google-genai
```

### 3. Configurar a chave da API
Crie um arquivo `.env` na raiz do projeto:
```
GEMINI_API_KEY=sua_chave_aqui
```

### 4. Executar
```bash
streamlit run main.py
```

O app abre no navegador. Importe um histórico (CSV) ou uma nota fiscal para popular o banco e comece a ver as sugestões de reposição.

---

## 🧰 Tecnologias

- **Streamlit** — interface web
- **SQLite + SQLAlchemy** — armazenamento
- **pandas** — manipulação de dados
- **Google Gemini (`google-genai`)** — extração de dados de notas fiscais
- **python-dotenv** — gerenciamento da chave de API

---

## 🙏 Créditos

Projeto desenvolvido seguindo a aula do **Teo Me Why**.
