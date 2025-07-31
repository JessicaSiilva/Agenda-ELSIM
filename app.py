import streamlit as st
import psycopg2
import pandas as pd
from datetime import date

# Conexão com o banco de dados PostgreSQL
def conectar():
    return psycopg2.connect(
        host="localhost",
        database="agendaEL",
        user="postgres",
        password="020904"
    )

# Função para criar a tabela se não existir
def criar_tabela():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            data DATE,
            cliente VARCHAR(100),
            produto VARCHAR(50),
            servico_limpeza BOOLEAN,
            servico_manutencao BOOLEAN,
            valor_limpeza NUMERIC,
            valor_manutencao NUMERIC,
            total NUMERIC,
            realizado BOOLEAN,
            pago BOOLEAN,
            forma_pagamento VARCHAR(20),
            parcelas INTEGER
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Inserir dados
def inserir_servico(dados):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO servicos (
            data, cliente, produto, servico_limpeza, servico_manutencao,
            valor_limpeza, valor_manutencao, total,
            realizado, pago, forma_pagamento, parcelas
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, dados)
    conn.commit()
    cur.close()
    conn.close()

# Buscar todos os dados
def listar_servicos():
    conn = conectar()
    df = pd.read_sql("SELECT * FROM servicos ORDER BY data DESC", conn)
    conn.close()
    return df

# Filtrar por cliente ou data
def filtrar_servicos(cliente=None, data_escolhida=None):
    conn = conectar()
    query = "SELECT * FROM servicos WHERE 1=1"
    params = []

    if cliente:
        query += " AND cliente ILIKE %s"
        params.append(f"%{cliente}%")
    if data_escolhida:
        query += " AND data = %s"
        params.append(data_escolhida)

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Interface com Streamlit
def main():
    st.set_page_config("Agenda de Servicos", layout="centered")
    st.title(" Agenda de Servicos")

    criar_tabela()

    menu = ["Cadastrar Servico", "Listar Todos", "Relatorio"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "Cadastrar Servico":
        st.subheader(" Cadastro de Servico")

        data_servico = st.date_input("Data", value=date.today())
        cliente = st.text_input("Nome do Cliente")
        produto = st.selectbox("Produto", ["Maquina de lavar", "Fogao", "Forno", "Micro-ondas", "Ventilador", "Climatizador", "Outros"])
        servico_limpeza = st.checkbox("Limpeza")
        servico_manutencao = st.checkbox("Manutencao")

        valor_limpeza = st.number_input("Valor da Limpeza", min_value=0.0) if servico_limpeza else 0.0
        valor_manutencao = st.number_input("Valor da Manutencao", min_value=0.0) if servico_manutencao else 0.0

        total = valor_limpeza + valor_manutencao

        realizado = st.checkbox("Servico Realizado")
        pago = st.checkbox("Servico Pago")
        forma_pagamento = st.selectbox("Forma de Pagamento", ["", "a vista", "Cartao"])
        parcelas = st.number_input("Parcelas (se cartao)", min_value=0, step=1) if forma_pagamento == "Cartao" else 0

        if st.button(" Salvar Servico"):
            if cliente:
                dados = (
                    data_servico, cliente, produto, servico_limpeza, servico_manutencao,
                    valor_limpeza, valor_manutencao, total, realizado, pago, forma_pagamento, parcelas
                )
                inserir_servico(dados)
                st.success(" Servico cadastrado com sucesso!")
            else:
                st.warning(" Informe o nome do cliente.")

    elif escolha == "Listar Todos":
        st.subheader("Lista de Servicos Cadastrados")
        df = listar_servicos()
        st.dataframe(df)

    elif escolha == "Relatorio":
        st.subheader(" Relatorio por Cliente/Data")

        col1, col2 = st.columns(2)
        with col1:
            nome_cliente = st.text_input("Filtrar por nome do cliente")
        with col2:
            data_filtro = st.date_input("Filtrar por data", value=None)

        if st.button(" Buscar"):
            df = filtrar_servicos(cliente=nome_cliente, data_escolhida=data_filtro)
            st.dataframe(df)

# Executar app
if __name__ == '__main__':
    main()

#streamlit run app.py
