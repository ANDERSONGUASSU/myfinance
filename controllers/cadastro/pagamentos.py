"""
Este módulo define as funções para o cadastro, listagem, edição e exclusão de tipos de pagamento.
"""

import sqlite3
from models.database import conectar


def cadastrar_pagamento(tipo):
    """
    Cadastra um novo tipo de pagamento no banco de dados.
    """
    if not tipo.strip():
        return {
            'success': False,
            'message': 'O tipo de pagamento não pode ser vazio.',
        }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pagamentos (tipo) VALUES (?)', (tipo,))
        conn.commit()
        return {
            'success': True,
            'message': 'Tipo de pagamento cadastrado com sucesso.',
        }
    except sqlite3.IntegrityError:
        return {
            'success': False,
            'message': 'Já existe um tipo de pagamento com este nome.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao cadastrar tipo de pagamento: {e}',
        }
    finally:
        conn.close()


def listar_pagamentos():
    """
    Lista todos os tipos de pagamento cadastrados no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT id, tipo FROM pagamentos ORDER BY tipo ASC')
        pagamentos = [
            {'id': row[0], 'tipo': row[1]} for row in cursor.fetchall()
        ]
        return {'success': True, 'pagamentos': pagamentos}
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao listar tipos de pagamento: {e}',
        }
    finally:
        conn.close()


def excluir_pagamento(pagamento_id):
    """
    Exclui um tipo de pagamento existente no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Verificar se há transações vinculadas a este tipo de pagamento
        cursor.execute(
            'SELECT COUNT(*) FROM transacoes WHERE pagamento_id = ?',
            (pagamento_id,),
        )
        count = cursor.fetchone()[0]

        if count > 0:
            return {
                'success': False,
                'message': f'Não é possível excluir. Existem {count} transações com este tipo de pagamento.',
            }

        cursor.execute('DELETE FROM pagamentos WHERE id = ?', (pagamento_id,))
        conn.commit()
        return {
            'success': True,
            'message': 'Tipo de pagamento excluído com sucesso.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao excluir tipo de pagamento: {e}',
        }
    finally:
        conn.close()


def editar_pagamento(pagamento_id, novo_tipo):
    """
    Atualiza o nome de um tipo de pagamento existente no banco de dados.
    """
    if not novo_tipo.strip():
        return {
            'success': False,
            'message': 'O tipo de pagamento não pode ser vazio.',
        }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE pagamentos SET tipo = ? WHERE id = ?',
            (novo_tipo, pagamento_id),
        )
        conn.commit()
        return {
            'success': True,
            'message': 'Tipo de pagamento atualizado com sucesso.',
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f'Erro ao atualizar tipo de pagamento: {e}',
        }
    finally:
        conn.close()
