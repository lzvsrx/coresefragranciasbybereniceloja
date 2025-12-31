import sqlite3
import pandas as pd
import bcrypt
import datetime

DB_NAME = "store.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabela de Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    name TEXT
                )''')
    
    # Tabela de Produtos
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand TEXT,
                    style TEXT,
                    type TEXT,
                    price REAL,
                    quantity INTEGER,
                    expiration_date TEXT,
                    image BLOB
                )''')
    
    # Tabela de Vendas
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    quantity INTEGER,
                    total_value REAL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY(product_id) REFERENCES products(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    
    # Criar admin padrão se não existir
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                  ('admin', hashed.decode('utf-8'), 'admin', 'Administrador'))
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)

def check_login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return user # (id, username, password, role, name)
    return None

def create_user(username, password, role, name):
    conn = get_connection()
    c = conn.cursor()
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                  (username, hashed.decode('utf-8'), role, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def add_product(nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes, id=None):
    conn = get_connection()
    c = conn.cursor()
    if id is not None:
        c.execute('''INSERT OR REPLACE INTO products (id, name, brand, style, type, price, quantity, expiration_date, image)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (id, nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes))
    else:
        c.execute('''INSERT INTO products (name, brand, style, type, price, quantity, expiration_date, image)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes))
    conn.commit()
    conn.close()

def get_products():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

def update_product(id, nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes=None):
    conn = get_connection()
    c = conn.cursor()
    if image_bytes:
        c.execute('''UPDATE products SET name=?, brand=?, style=?, type=?, price=?, quantity=?, expiration_date=?, image=?
                     WHERE id=?''',
                  (nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes, id))
    else:
        c.execute('''UPDATE products SET name=?, brand=?, style=?, type=?, price=?, quantity=?, expiration_date=?
                     WHERE id=?''',
                  (nome, marca, estilo, tipo, preco, quantidade, data_validade, id))
    conn.commit()
    conn.close()

def delete_product(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()

def register_sale(product_id, quantity, user_id=None):
    conn = get_connection()
    c = conn.cursor()
    
    # Verificar estoque e preço
    c.execute("SELECT price, quantity FROM products WHERE id=?", (product_id,))
    res = c.fetchone()
    if not res:
        conn.close()
        return False, "Produto não encontrado"
    
    price, current_qty = res
    if current_qty < quantity:
        conn.close()
        return False, "Estoque insuficiente"
    
    total_value = price * quantity
    
    # Atualizar estoque
    c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
    
    # Registrar venda
    c.execute("INSERT INTO sales (product_id, quantity, total_value, user_id) VALUES (?, ?, ?, ?)",
              (product_id, quantity, total_value, user_id))
    
    conn.commit()
    conn.close()
    return True, "Venda realizada com sucesso"

def get_sales_report():
    conn = get_connection()
    query = '''
        SELECT s.id, p.name as product_name, s.quantity, s.total_value, s.sale_date, u.name as user_name
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        LEFT JOIN users u ON s.user_id = u.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_product_by_id(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()
    return row

