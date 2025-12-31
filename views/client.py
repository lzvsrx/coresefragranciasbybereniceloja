import streamlit as st
import database as db
import os
from pathlib import Path

def show_client_view(user):
    st.title(f"Catálogo de Produtos - Olá, {user[4]}")
    
    products = db.get_products()
    
    if not products.empty:
        # Filters
        st.sidebar.header("Filtros")
        search = st.sidebar.text_input("Buscar")
        
        filtered_df = products
        if search:
            filtered_df = products[products['name'].str.contains(search, case=False, na=False) |
                                   products['brand'].str.contains(search, case=False, na=False)]
        
        # Grid Layout
        # Streamlit doesn't have a native grid, so we loop with columns
        
        rows = len(filtered_df)
        cols_per_row = 3
        
        # Reset index for easier looping
        filtered_df = filtered_df.reset_index(drop=True)
        
        # List files in assets to find matches by ID
        assets_path = Path("assets")
        assets_files = os.listdir(assets_path) if assets_path.exists() else []

        for i in range(0, rows, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < rows:
                    row = filtered_df.iloc[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            # Try to find image in assets first (by ID prefix)
                            image_path = None
                            for f in assets_files:
                                if f.startswith(f"{row['id']}_"):
                                    image_path = str(assets_path / f)
                                    break
                            
                            if image_path:
                                st.image(image_path, use_container_width=True)
                            elif row['image']:
                                st.image(row['image'], use_container_width=True)
                            else:
                                st.markdown("*Sem Imagem*")
                                
                            st.subheader(row['name'])
                            st.caption(f"{row['brand']} - {row['style']}")
                            st.markdown(f"#### R$ {row['price']:.2f}")
                            
                            if row['quantity'] > 0:
                                st.success(f"Disponível ({row['quantity']})")
                            else:
                                st.error("Esgotado")
    else:
        st.info("Nenhum produto disponível no momento.")
