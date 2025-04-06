"""
Este módulo define as funções para o cadastro, listagem, edição e exclusão de contas.
"""

import sqlite3
from models.database import conectar


def cadastrar_conta(
    nome,
    tipo,
    saldo_inicial=0,
    dia_fechamento=None,
    dia_vencimento=None,
    limite=None,
):
    """
    Cadastra uma nova conta no banco de dados.
    """
    if not nome.strip():
        return {
            'success': False,
            'message': 'O nome da conta não pode ser vazio.',
        }

    # Verificação de tipos específicos
    if tipo == 'cartao' and (dia_fechamento is None or dia_vencimento is None):
        return {
            'success': False,
            'message': 'O cartão de crédito precisa ter dia de fechamento e vencimento.',
        }

    try:
        conn = conectar()
        cursor = conn.cursor()

        # Inserir a conta no banco de dados
        cursor.execute(
            """
            INSERT INTO contas (nome, tipo, saldo, dia_fechamento, dia_vencimento, limite_credito) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, tipo, saldo_inicial, dia_fechamento, dia_vencimento, limite),
        )
        conn.commit()
        return {'success': True, 'message': 'Conta cadastrada com sucesso.'}
    except sqlite3.IntegrityError:
        return {
            'success': False,
            'message': 'Já existe uma conta com este nome.',
        }
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao cadastrar conta: {e}'}
    finally:
        conn.close()


def listar_contas():
    """
    Lista todas as contas cadastradas no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome, tipo, saldo, dia_fechamento, dia_vencimento, limite_credito 
            FROM contas 
            ORDER BY nome ASC
            """
        )

        contas = []
        for row in cursor.fetchall():
            conta = {
                'id': row[0],
                'nome': row[1],
                'tipo': row[2],
                'saldo': row[3],
            }

            # Adiciona informações específicas para cartões
            if row[2] == 'cartao':
                conta['dia_fechamento'] = row[4]
                conta['dia_vencimento'] = row[5]
                conta['limite'] = row[6]

            contas.append(conta)

        return {'success': True, 'contas': contas}
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao listar contas: {e}'}
    finally:
        conn.close()


def obter_conta(conta_id):
    """
    Obtém uma conta específica pelo ID.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome, tipo, saldo, dia_fechamento, dia_vencimento, limite_credito 
            FROM contas 
            WHERE id = ?
            """,
            (conta_id,),
        )

        row = cursor.fetchone()
        if not row:
            return {'success': False, 'message': 'Conta não encontrada.'}

        conta = {
            'id': row[0],
            'nome': row[1],
            'tipo': row[2],
            'saldo': row[3],
            'dia_fechamento': row[4],
            'dia_vencimento': row[5],
            'limite': row[6],
        }

        return {'success': True, 'conta': conta}
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao obter conta: {e}'}
    finally:
        conn.close()


def excluir_conta(conta_id):
    """
    Exclui uma conta existente no banco de dados.
    """
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Verificar se há transações vinculadas à conta
        cursor.execute(
            'SELECT COUNT(*) FROM transacoes WHERE conta_id = ?', (conta_id,)
        )
        count = cursor.fetchone()[0]

        if count > 0:
            return {
                'success': False,
                'message': f'Não é possível excluir. Existem {count} transações vinculadas a esta conta.',
            }

        cursor.execute('DELETE FROM contas WHERE id = ?', (conta_id,))
        conn.commit()
        return {'success': True, 'message': 'Conta excluída com sucesso.'}
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao excluir conta: {e}'}
    finally:
        conn.close()


def editar_conta(
    conta_id,
    nome,
    tipo=None,
    saldo=None,
    dia_fechamento=None,
    dia_vencimento=None,
    limite=None,
):
    """
    Atualiza uma conta existente no banco de dados.
    """
    if not nome.strip():
        return {
            'success': False,
            'message': 'O nome da conta não pode ser vazio.',
        }

    try:
        conn = conectar()
        cursor = conn.cursor()

        # Obtém a conta atual para verificar o tipo
        resultado = obter_conta(conta_id)
        if not resultado['success']:
            return resultado

        conta_atual = resultado['conta']

        # Define o tipo da conta
        novo_tipo = tipo if tipo is not None else conta_atual['tipo']

        # Verifica se está mudando de/para cartão de crédito
        if novo_tipo == 'cartao' and (
            dia_fechamento is None or dia_vencimento is None
        ):
            # Se está mudando para cartão mas não informou fechamento/vencimento
            if conta_atual['tipo'] != 'cartao':
                return {
                    'success': False,
                    'message': 'O cartão de crédito precisa ter dia de fechamento e vencimento.',
                }
            # Se já era cartão, mantém os valores anteriores
            dia_fechamento = conta_atual['dia_fechamento']
            dia_vencimento = conta_atual['dia_vencimento']
            limite = limite if limite is not None else conta_atual['limite']

        # Define o saldo
        novo_saldo = saldo if saldo is not None else conta_atual['saldo']

        cursor.execute(
            """
            UPDATE contas 
            SET nome = ?, tipo = ?, saldo = ?, dia_fechamento = ?, dia_vencimento = ?, limite_credito = ?
            WHERE id = ?
            """,
            (
                nome,
                novo_tipo,
                novo_saldo,
                dia_fechamento,
                dia_vencimento,
                limite,
                conta_id,
            ),
        )
        conn.commit()
        return {'success': True, 'message': 'Conta atualizada com sucesso.'}
    except sqlite3.Error as e:
        return {'success': False, 'message': f'Erro ao atualizar conta: {e}'}
    finally:
        conn.close()
