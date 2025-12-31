import streamlit as st
import pandas as pd
import database as db
import utils
import views.components as components

def show_admin_view(user):
    st.title(f"Painel Administrativo - Bem-vindo, {user[4]}")
    
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Gerenciar Produtos", "Gerenciar Usuários"])
    
    with tab1:
        st.header("Visão Geral")
        products = db.get_products()
        sales = db.get_sales_report()
        
        col1, col2, col3 = st.columns(3)
        
        total_stock = products['quantity'].sum() if not products.empty else 0
        total_sold = sales['quantity'].sum() if not sales.empty else 0
        total_revenue = sales['total_value'].sum() if not sales.empty else 0.0
        
        col1.metric("Produtos em Estoque", int(total_stock))
        col2.metric("Produtos Vendidos", int(total_sold))
        col3.metric("Receita Total", f"R$ {total_revenue:.2f}")

        # Nova linha de métricas
        st.subheader("Valores Totais")
        col4, col5 = st.columns(2)
        
        # Valor total em estoque (preço * quantidade para cada produto)
        total_stock_value = (products['price'] * products['quantity']).sum() if not products.empty else 0.0
        
        col4.metric("Valor Total em Estoque", f"R$ {total_stock_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Valor total vendido formatado com destaque
        formatted_revenue = f"R$ {total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col5.metric("Valor Total Vendido (Receita)", formatted_revenue)
        
        st.markdown(f"""
        <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; color: #155724; font-weight: bold; margin-top: 10px; border: 1px solid #c3e6cb;">
            💰 VALOR TOTAL DOS PRODUTOS VENDIDOS: {formatted_revenue}
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Estoque vs Vendas")
        if not products.empty or not sales.empty:
            chart_data = pd.DataFrame({
                'Categoria': ['Estoque', 'Vendidos'],
                'Quantidade': [total_stock, total_sold]
            })
            st.bar_chart(chart_data, x='Categoria', y='Quantidade', color="#800020")
            
        st.subheader("Últimas Vendas")
        if not sales.empty:
            st.dataframe(sales.sort_values(by='sale_date', ascending=False).head(10))
        else:
            st.info("Nenhuma venda registrada.")

    with tab2:
        components.render_product_management()

    with tab3:
        st.header("Gerenciar Usuários")
        with st.form("add_user"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Senha", type="password")
            new_role = st.selectbox("Função", ["admin", "funcionario", "cliente"])
            new_name = st.text_input("Nome Completo")
            
            if st.form_submit_button("Criar Usuário"):
                if new_user and new_pass:
                    if db.create_user(new_user, new_pass, new_role, new_name):
                        st.success("Usuário criado!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar (usuário já existe?)")
                else:
                    st.error("Preencha todos os campos")
                    
        st.subheader("Usuários Existentes")
        conn = db.get_connection()
        users_df = pd.read_sql("SELECT id, username, role, name FROM users", conn)
        conn.close()
        st.dataframe(users_df)
