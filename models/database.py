"""
Este módulo define as funções para criar e conectar ao banco de dados SQLite.

O banco de dados é criado no diretório 'data' com o nome 'database.db'.

As tabelas são criadas com as seguintes colunas:
"""
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / 'data' / 'database.db'


def conectar():
    """
    Conecta ao banco de dados SQLite.
    """
    return sqlite3.connect(DB_PATH)


def criar_tabelas():
    """
    Cria as tabelas no banco de dados SQLite.
    """
    conn = conectar()
    cursor = conn.cursor()

    # Contas
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL, -- ex: 'cartao', 'conta', 'investimento'
        saldo REAL DEFAULT 0.0,
        dia_fechamento INTEGER,
        dia_vencimento INTEGER,
        limite_credito REAL
        )"""
    )

    # Parcelamentos
    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS parcelamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT,
            valor_total REAL,
            parcelas INTEGER,
            data_compra TEXT,
            data_vencimento TEXT,
            conta_id INTEGER,
            categoria_id INTEGER,
            responsavel_id INTEGER,
            pagamento_id INTEGER,
            FOREIGN KEY (conta_id) REFERENCES contas(id),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (responsavel_id) REFERENCES responsaveis(id),
            FOREIGN KEY (pagamento_id) REFERENCES pagamentos(id)
        )"""
    )

    # Categorias
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )"""
    )

    # Responsáveis
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS responsaveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )"""
    )

    # Pagamentos
    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL
        )"""
    )

    # Transações
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL, -- "receita" ou "despesa"
            conta_id INTEGER,
            parcelamento_id INTEGER,
            categoria_id INTEGER,
            responsavel_id INTEGER,
            pagamento_id INTEGER,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
                -- ex: 'pendente', 'paga', 'vencida'
            FOREIGN KEY (conta_id) REFERENCES contas(id),
            FOREIGN KEY (parcelamento_id) REFERENCES parcelamentos(id),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (responsavel_id) REFERENCES responsaveis(id),
            FOREIGN KEY (pagamento_id) REFERENCES pagamentos(id)
        )"""
    )

    # Recorrências
    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS recorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transacao_id INTEGER,
            frequencia TEXT NOT NULL,
                -- ex: 'semanal', 'mensal', 'anual', 'semestral', 'trimestral'
            data_inicio TEXT NOT NULL,
            data_fim TEXT,
            proxima_execucao TEXT,
            ocorrencias INTEGER,
            usar_valor_fixo BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (transacao_id) REFERENCES transacoes(id)
        )"""
    )

    # Faturas
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS faturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_id INTEGER,
            mes INTEGER,
            ano INTEGER,
            valor_total REAL,
            data_fechamento TEXT,
            data_vencimento TEXT,
            limite_disponivel REAL,
            valor_pago REAL,
            status TEXT NOT NULL, -- ex: 'pendente', 'paga', 'vencida'
            FOREIGN KEY (conta_id) REFERENCES contas(id)
        )"""
    )

    conn.commit()
    conn.close()


def atualizar_estrutura_banco():
    """
    Atualiza a estrutura do banco de dados adicionando colunas que possam estar faltando
    em tabelas existentes.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Verificar se a coluna 'ocorrencias' existe na tabela 'recorrencias'
        cursor.execute('PRAGMA table_info(recorrencias)')
        colunas = cursor.fetchall()
        colunas_nomes = [col[1] for col in colunas]

        if 'ocorrencias' not in colunas_nomes:
            cursor.execute(
                'ALTER TABLE recorrencias ADD COLUMN ocorrencias INTEGER DEFAULT 0'
            )
            print("Coluna 'ocorrencias' adicionada à tabela 'recorrencias'.")

        # Verificar se a coluna 'data_vencimento' existe na tabela 'transacoes'
        cursor.execute('PRAGMA table_info(transacoes)')
        colunas = cursor.fetchall()
        colunas_nomes = [col[1] for col in colunas]

        if 'data_vencimento' not in colunas_nomes:
            cursor.execute(
                'ALTER TABLE transacoes ADD COLUMN data_vencimento TEXT'
            )
            print("Coluna 'data_vencimento' adicionada à tabela 'transacoes'.")

        # Verificar se a coluna 'data_vencimento' existe na tabela 'parcelamentos'
        cursor.execute('PRAGMA table_info(parcelamentos)')
        colunas = cursor.fetchall()
        colunas_nomes = [col[1] for col in colunas]

        if 'data_vencimento' not in colunas_nomes:
            cursor.execute(
                'ALTER TABLE parcelamentos ADD COLUMN data_vencimento TEXT'
            )
            print(
                "Coluna 'data_vencimento' adicionada à tabela 'parcelamentos'."
            )

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f'Erro ao atualizar a estrutura do banco: {e}')
        return False
    finally:
        conn.close()
