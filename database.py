import sqlite3
import pandas as pd
import bcrypt
import datetime

DB_NAME = "store.db"

def init_db():
    try:
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
        
        # Migração: Adicionar colunas novas se não existirem
        cols_to_add = [
            ("birth_date", "TEXT"),
            ("email", "TEXT"),
            ("phone", "TEXT"),
            ("cpf", "TEXT")
        ]
        
        for col_name, col_type in cols_to_add:
            try:
                c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass # Coluna já existe
        
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
    except Exception as e:
        print(f"Erro ao inicializar DB: {e}")
    finally:
        try:
            conn.close()
        except:
            pass

def get_connection():
    # Helper para criar conexão com timeout maior para evitar locks
    return sqlite3.connect(DB_NAME, timeout=10)

def check_login(username, password):
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return user # (id, username, password, role, name)
        return None
    except Exception as e:
        print(f"Erro no login: {e}")
        return None
    finally:
        if conn: conn.close()

def create_user(username, password, role, name, birth_date=None, email=None, phone=None, cpf=None):
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password, role, name, birth_date, email, phone, cpf) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (username, hashed.decode('utf-8'), role, name, birth_date, email, phone, cpf))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False
    finally:
        if conn: conn.close()

def get_birthday_clients():
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM users WHERE role='cliente' AND birth_date IS NOT NULL AND birth_date != ''", conn)
        return df
    except Exception as e:
        print(f"Erro ao buscar aniversariantes: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def add_product(nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes, id=None):
    conn = None
    try:
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
    except Exception as e:
        print(f"Erro ao adicionar produto: {e}")
        raise e
    finally:
        if conn: conn.close()

def get_products():
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM products", conn)
        return df
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def update_product(id, nome, marca, estilo, tipo, preco, quantidade, data_validade, image_bytes=None):
    conn = None
    try:
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
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        raise e
    finally:
        if conn: conn.close()

def delete_product(id):
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Erro ao deletar produto: {e}")
    finally:
        if conn: conn.close()

def register_sale(product_id, quantity, user_id=None):
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # Verificar estoque e preço
        c.execute("SELECT price, quantity FROM products WHERE id=?", (product_id,))
        res = c.fetchone()
        if not res:
            return False, "Produto não encontrado"
        
        price, current_qty = res
        if current_qty < quantity:
            return False, "Estoque insuficiente"
        
        total_value = price * quantity
        
        # Atualizar estoque
        c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
        
        # Registrar venda
        c.execute("INSERT INTO sales (product_id, quantity, total_value, user_id) VALUES (?, ?, ?, ?)",
                  (product_id, quantity, total_value, user_id))
        
        conn.commit()
        return True, "Venda realizada com sucesso"
    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro na venda: {e}")
        return False, f"Erro ao processar venda: {e}"
    finally:
        if conn: conn.close()

def get_sales_report():
    conn = None
    try:
        conn = get_connection()
        query = '''
            SELECT s.id, p.name as product_name, s.quantity, s.total_value, s.sale_date, u.name as user_name
            FROM sales s
            LEFT JOIN products p ON s.product_id = p.id
            LEFT JOIN users u ON s.user_id = u.id
        '''
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Erro no relatório: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def get_product_by_id(id):
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE id=?", (id,))
        row = c.fetchone()
        return row
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        return None
    finally:
        if conn: conn.close()

