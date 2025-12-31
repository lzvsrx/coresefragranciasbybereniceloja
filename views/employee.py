import streamlit as st
import database as db
import views.components as components

def show_employee_view(user):
    st.title(f"Painel do Funcionário - {user[4]}")
    
    tab1, tab2 = st.tabs(["Vendas (PDV)", "Gerenciar Estoque"])
    
    with tab1:
        st.header("Ponto de Venda")
        
        products = db.get_products()
        if not products.empty:
            product_options = {f"{row['id']} - {row['name']} (Estoque: {row['quantity']})": row['id'] for index, row in products.iterrows() if row['quantity'] > 0}
            
            if product_options:
                selected_option = st.selectbox("Selecione o Produto", list(product_options.keys()))
                selected_id = product_options[selected_option]
                
                prod = db.get_product_by_id(selected_id)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if prod[8]: # image
                        st.image(prod[8], caption=prod[1], use_container_width=True)
                    else:
                        st.info("Sem imagem disponível")
                
                with col2:
                    st.write(f"**Produto:** {prod[1]}")
                    st.write(f"**Preço Unitário:** R$ {prod[5]:.2f}")
                    
                    max_qty = int(prod[6])
                    qty_sell = st.number_input("Quantidade", min_value=1, max_value=max_qty, step=1)
                    
                    total = qty_sell * prod[5]
                    st.write(f"### Total a Pagar: R$ {total:.2f}")
                    
                    if st.button("Confirmar Venda", type="primary"):
                        success, msg = db.register_sale(selected_id, qty_sell, user[0])
                        if success:
                            st.balloons()
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.warning("Nenhum produto com estoque disponível.")
        else:
            st.warning("Sem produtos cadastrados.")

    with tab2:
        components.render_product_management()
