"""
Este módulo define as funções para o cadastro, listagem, edição e exclusão de categorias.
"""

import sqlite3
from models.database import conectar


def cadastrar_categoria(nome):
    """
    Cadastra uma nova categoria no banco de dados.
    """
    if not nome.strip():
        return {
            'success': False,
            'message': 'O nome da categoria não pode ser vazio.',
        }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categorias (nome) VALUES (?)', (nome,))
        conn.commit()
        return {
            'success': True,
            'message': 'Categoria cadastrada com sucesso.',
        }
    except sqlite3.IntegrityError:
        return {
            'success': False,
            'message': 'Já existe uma categoria com este nome.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao cadastrar categoria: {e}',
        }
    finally:
        conn.close()


def listar_categorias():
    """
    Lista todas as categorias cadastradas no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome FROM categorias ORDER BY nome ASC')
        categorias = [
            {'id': row[0], 'nome': row[1]} for row in cursor.fetchall()
        ]
        return {'success': True, 'categorias': categorias}
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao listar categorias: {e}'}
    finally:
        conn.close()


def excluir_categoria(categoria_id):
    """
    Exclui uma categoria existente no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categorias WHERE id = ?', (categoria_id,))
        conn.commit()
        return {'success': True, 'message': 'Categoria excluída com sucesso.'}
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao excluir categoria: {e}'}
    finally:
        conn.close()


def editar_categoria(categoria_id, novo_nome):
    """
    Atualiza o nome de uma categoria existente no banco de dados.
    """
    if not novo_nome.strip():
        return {
            'success': False,
            'message': 'O nome da categoria não pode ser vazio.',
        }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE categorias SET nome = ? WHERE id = ?',
            (novo_nome, categoria_id),
        )
        conn.commit()
        return {
            'success': True,
            'message': 'Categoria atualizada com sucesso.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao atualizar categoria: {e}',
        }
    finally:
        conn.close()
