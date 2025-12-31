import streamlit as st
import database as db
import utils
from views import admin, employee, client

# Config page
st.set_page_config(page_title="Cores & Fragrâncias", layout="wide", page_icon="🛍️")

# Init DB
db.init_db()

# Apply CSS
utils.apply_custom_css()

# Session State for Auth
if 'user' not in st.session_state:
    st.session_state['user'] = None

def show_logo():
    try:
        st.image("assets/logo.png", width=200)
    except:
        pass

def login():
    col_l1, col_l2, col_l3 = st.columns([1,1,1])
    with col_l2:
        try:
            st.image("assets/logo.png", use_container_width=True)
        except:
            pass
            
    st.markdown("<h1 style='text-align: center;'>Login - Cores & Fragrâncias</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                user = db.check_login(username, password)
                if user:
                    st.session_state['user'] = user
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        
        st.info("Admin padrão: admin / admin123")

def main():
    if not st.session_state['user']:
        login()
    else:
        user = st.session_state['user']
        role = user[3]
        
        # Sidebar for Logout
        with st.sidebar:
            try:
                st.image("assets/logo.png", use_container_width=True)
            except:
                pass
            st.title("Menu")
            st.write(f"Usuário: **{user[4]}**")
            st.write(f"Função: **{role.capitalize()}**")
            st.divider()
            if st.button("Sair"):
                st.session_state['user'] = None
                st.rerun()
        
        if role == 'admin':
            admin.show_admin_view(user)
        elif role == 'funcionario':
            employee.show_employee_view(user)
        elif role == 'cliente':
            client.show_client_view(user)
        else:
            st.error("Função desconhecida.")

if __name__ == "__main__":
    main()
