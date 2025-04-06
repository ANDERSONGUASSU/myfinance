"""
Este módulo define as funções para o cadastro, listagem, edição e exclusão de responsáveis.
"""

import sqlite3
from models.database import conectar


def cadastrar_responsavel(nome):
    """
    Cadastra um novo responsável no banco de dados.
    """
    if not nome.strip():
        return {
            'success': False,
            'message': 'O nome do responsável não pode ser vazio.',
        }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO responsaveis (nome) VALUES (?)', (nome,))
        conn.commit()
        return {
            'success': True,
            'message': 'Responsável cadastrado com sucesso.',
        }
    except sqlite3.IntegrityError:
        return {
            'success': False,
            'message': 'Já existe um responsável com este nome.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao cadastrar responsável: {e}',
        }
    finally:
        conn.close()


def listar_responsaveis():
    """
    Lista todos os responsáveis cadastrados no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome FROM responsaveis ORDER BY nome ASC')
        responsaveis = [
            {'id': row[0], 'nome': row[1]} for row in cursor.fetchall()
        ]
        return {'success': True, 'responsaveis': responsaveis}
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao listar responsáveis: {e}',
        }
    finally:
        conn.close()


def excluir_responsavel(responsavel_id):
    """
    Exclui um responsável existente no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM responsaveis WHERE id = ?', (responsavel_id,)
        )
        conn.commit()
        return {
            'success': True,
            'message': 'Responsável excluído com sucesso.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao excluir responsável: {e}',
        }
    finally:
        conn.close()


def editar_responsavel(responsavel_id, novo_nome):
    """
    Atualiza o nome de um responsável existente no banco de dados.
    """
    if not novo_nome.strip():
        return {
            'success': False,
            'message': 'O nome do responsável não pode ser vazio.',
        }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE responsaveis SET nome = ? WHERE id = ?',
            (novo_nome, responsavel_id),
        )
        conn.commit()
        return {
            'success': True,
            'message': 'Responsável atualizado com sucesso.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao atualizar responsável: {e}',
        }
    finally:
        conn.close()
