import streamlit as st
import base64

# Constantes do Sistema
MARCAS = [
    "Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura", 
    "Oui-Original-Unique-Individuel", "Pierre Alexander", "Tupperware", "Outra"
]

ESTILOS = [
    "Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Masculinos", 
    "Femininos Nina Secrets", "Marcas", "Infantil", "Casa", "Solar", "Maquiage", 
    "Teen", "Kits e Presentes", "Cuidados com o Corpo", "Lançamentos", 
    "Acessórios de Casa", "Outro"
]

TIPOS = [
    "Perfumaria masculina", "Perfumaria feminina", "Body splash", "Body spray", 
    "Eau de parfum", "Desodorantes", "Perfumaria infantil", "Perfumaria vegana", 
    "Família olfativa", "Clareador de manchas", "Anti-idade", "Protetor solar facial", 
    "Rosto", "Tratamento para o rosto", "Acne", "Limpeza", "Esfoliante", "Tônico facial", 
    "Kits de tratamento", "Tratamento para cabelos", "Shampoo", "Condicionador", 
    "Leave-in e Creme para Pentear", "Finalizador", "Modelador", "Acessórios", 
    "Kits e looks", "Boca", "Olhos", "Pincis", "Paleta", "Unhas", "Sobrancelhas", 
    "Hidratante", "Cuidados pós-banho", "Cuidados para o banho", "Barba", "Óleo corporal", 
    "Cuidados íntimos", "Unissex", "Bronzeamento", "Protetor solar", "Depilação", 
    "Mãos", "Lábios", "Pés", "Pés sol", "Protetor solar corporal", "Colônias", 
    "Estojo", "Sabonetes", "Sabonete líquido", "Sabonete em barra", 
    "Creme hidratante para as mãos", "Creme hidratante para os pés", "Miniseries", 
    "Kits de perfumes", "Antissinais", "Máscara", "Creme bisnaga", 
    "Roll On Fragrânciado", "Roll On On Duty", "Shampoo 2 em 1", "Spray corporal", 
    "Booster de Tratamento", "Creme para Pentear", "Óleo de Tratamento", 
    "Pré-shampoo", "Sérum de Tratamento", "Shampoo e Condicionador", "Garrafas", 
    "Armazenamentos", "Micro-ondas", "Servir", "Preparo", "Lazer/Outdoor", 
    "Presentes", "Outro"
]

# Paleta de Cores
COLOR_BG = "#FFFFE0"
COLOR_TEXT_SMALL = "#36454F"
COLOR_TEXT_LARGE_1 = "#800020"
COLOR_TEXT_LARGE_2 = "#36454F"

def apply_custom_css():
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT_SMALL};
        }}
        h1, h2, h3 {{
            color: {COLOR_TEXT_LARGE_1} !important;
        }}
        h4, h5, h6 {{
            color: {COLOR_TEXT_LARGE_2} !important;
        }}
        p, label, div, span {{
            color: {COLOR_TEXT_SMALL};
        }}
        .stButton button {{
            background-color: {COLOR_TEXT_LARGE_1};
            color: white;
        }}
        </style>
    """, unsafe_allow_html=True)

from fpdf import FPDF
import pandas as pd
import io

def generate_pdf(products_df):
    pdf = FPDF()
    pdf.add_page()
    # Usar fonte padrão que suporta caracteres básicos, mas para caracteres especiais complexos
    # FPDF padrão tem limitações. Vamos tentar limpar o texto ou usar codificação 'latin-1' compatível
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Relatório de Produtos", ln=1, align='C')
    pdf.ln(10)
    
    for index, row in products_df.iterrows():
        # Função auxiliar para limpar/substituir caracteres problemáticos
        def clean_text(text):
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        # Truncate text to avoid overflow if necessary, or just simple list
        text = f"ID: {row['id']} | Nome: {clean_text(str(row['name'])[:30])} | Marca: {clean_text(str(row['brand'])[:15])}"
        text2 = f"   Qtd: {row['quantity']} | Preço: R$ {row['price']} | Val: {row['expiration_date']}"
        pdf.cell(0, 8, txt=text, ln=1)
        pdf.cell(0, 8, txt=text2, ln=1)
        pdf.ln(2)
        
    output = pdf.output(dest='S')
    return output.encode('latin-1', 'replace') if isinstance(output, str) else bytes(output)

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
