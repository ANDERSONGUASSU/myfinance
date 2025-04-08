"""
Este módulo implementa o controller para visualização, edição e exclusão de transações.
Segue o padrão MVC e implementa o design pattern Repository para acesso ao banco de dados.
"""

import sqlite3
from models.database import conectar
from datetime import datetime


class TransacoesRepository:
    """
    Repositório para operações CRUD de transações.
    Implementa o padrão Repository para abstrair o acesso ao banco de dados.
    """

    @staticmethod
    def buscar_transacoes(filtros=None):
        """
        Busca transações com base nos filtros fornecidos.

        :param filtros: Dicionário com os filtros a serem aplicados
        :return: Dicionário com resultado e dados
        """
        try:
            conn = conectar()
            cursor = conn.cursor()

            # Construir a query SQL base
            query = """
            SELECT 
                t.id,
                t.data,
                t.data_vencimento,
                t.valor,
                t.tipo,
                t.descricao,
                c.nome as conta_nome,
                c.tipo as conta_tipo,
                cat.nome as categoria_nome,
                r.nome as responsavel_nome,
                p.tipo as pagamento_tipo,
                t.status,
                CASE WHEN par.id IS NOT NULL THEN 'Sim' ELSE 'Não' END as parcelada,
                CASE WHEN rec.id IS NOT NULL THEN rec.frequencia ELSE 'Não' END as recorrente,
                t.conta_id,
                t.categoria_id,
                t.responsavel_id,
                t.pagamento_id
            FROM transacoes t
            LEFT JOIN contas c ON t.conta_id = c.id
            LEFT JOIN categorias cat ON t.categoria_id = cat.id
            LEFT JOIN responsaveis r ON t.responsavel_id = r.id
            LEFT JOIN pagamentos p ON t.pagamento_id = p.id
            LEFT JOIN parcelamentos par ON t.parcelamento_id = par.id
            LEFT JOIN recorrencias rec ON rec.transacao_id = t.id
            """

            # Aplicar filtros
            where_clauses = []
            params = []

            if filtros:
                # Filtro de período
                if filtros.get('periodo') == 'mes' and filtros.get('mes') and filtros.get('ano'):
                    # Construir as datas de início e fim do mês
                    mes = int(filtros['mes'])
                    ano = int(filtros['ano'])

                    # Determinar a data de início e fim do mês
                    if mes == 12:
                        proximo_mes = 1
                        proximo_ano = ano + 1
                    else:
                        proximo_mes = mes + 1
                        proximo_ano = ano

                    data_inicio = f"{ano}-{mes:02d}-01"
                    data_fim = f"{proximo_ano}-{proximo_mes:02d}-01"

                    # Modificar a lógica para considerar data_vencimento para transações de cartão
                    where_clauses.append("""
                        ((c.tipo = 'cartao' AND t.data_vencimento IS NOT NULL AND 
                          t.data_vencimento >= ? AND t.data_vencimento < ?) 
                         OR
                         ((c.tipo != 'cartao' OR t.data_vencimento IS NULL) AND 
                          t.data >= ? AND t.data < ?))
                    """)
                    params.extend([data_inicio, data_fim, data_inicio, data_fim])

                elif filtros.get('periodo') == 'ano' and filtros.get('ano'):
                    ano = int(filtros['ano'])
                    data_inicio = f"{ano}-01-01"
                    data_fim = f"{ano + 1}-01-01"

                    # Modificar a lógica para considerar data_vencimento para transações de cartão
                    where_clauses.append("""
                        ((c.tipo = 'cartao' AND t.data_vencimento IS NOT NULL AND 
                          t.data_vencimento >= ? AND t.data_vencimento < ?) OR
                         (c.tipo != 'cartao' OR t.data_vencimento IS NULL) AND 
                          t.data >= ? AND t.data < ?)
                    """)
                    params.extend([data_inicio, data_fim, data_inicio, data_fim])

                # Filtro de conta
                if filtros.get('conta_id'):
                    where_clauses.append("t.conta_id = ?")
                    params.append(filtros['conta_id'])

                # Filtro de categoria
                if filtros.get('categoria_id'):
                    where_clauses.append("t.categoria_id = ?")
                    params.append(filtros['categoria_id'])

                # Filtro de tipo (receita/despesa)
                if filtros.get('tipo') and filtros['tipo'] != 'todas':
                    where_clauses.append("t.tipo = ?")
                    params.append(filtros['tipo'])

                # Filtro de status
                if filtros.get('status') and filtros['status'] != 'todos':
                    where_clauses.append("t.status = ?")
                    params.append(filtros['status'])

            # Adicionar cláusulas WHERE à query
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            # Ordenação
            query += " ORDER BY t.data DESC"

            # Executar a query
            cursor.execute(query, params)
            transacoes = cursor.fetchall()

            # Formatar os resultados
            resultado = []
            total_receitas = 0
            total_despesas = 0

            for t in transacoes:
                # Converter valores para exibição
                valor = t[3]
                data_exibir = t[1]

                # Se for cartão de crédito e tiver data de vencimento, usar a data de vencimento
                if t[7] == 'cartao' and t[2]:
                    data_exibir = t[2]

                # Acumular totais
                if t[4] == 'receita':
                    total_receitas += valor
                else:  # despesa
                    total_despesas += abs(valor)

                transacao = {
                    'id': t[0],
                    'data': data_exibir,
                    'data_original': t[1],
                    'data_vencimento': t[2],
                    'valor': abs(valor),  # Valor absoluto para exibição
                    'valor_original': valor,  # Valor original para cálculos
                    'tipo': t[4].capitalize(),
                    'descricao': t[5],
                    'conta': t[6],
                    'conta_tipo': t[7],
                    'categoria': t[8],
                    'responsavel': t[9],
                    'forma_pagamento': t[10],
                    'status': t[11].capitalize(),
                    'parcelada': t[12],
                    'recorrente': t[13].capitalize() if t[13] != 'Não' else 'Não',
                    'conta_id': t[14],
                    'categoria_id': t[15],
                    'responsavel_id': t[16],
                    'pagamento_id': t[17]
                }
                resultado.append(transacao)

            return {
                'success': True,
                'transacoes': resultado,
                'total_receitas': total_receitas,
                'total_despesas': total_despesas,
                'saldo': total_receitas - total_despesas
            }

        except sqlite3.Error as e:
            return {
                'success': False,
                'error': str(e),
                'transacoes': [],
                'total_receitas': 0,
                'total_despesas': 0,
                'saldo': 0
            }
        finally:
            conn.close()

    @staticmethod
    def obter_transacao(transacao_id):
        """
        Obtém uma transação específica pelo ID.

        :param transacao_id: ID da transação
        :return: Dicionário com dados da transação
        """
        try:
            conn = conectar()
            cursor = conn.cursor()

            query = """
            SELECT 
                t.id,
                t.data,
                t.valor,
                t.tipo,
                t.descricao,
                t.conta_id,
                t.categoria_id,
                t.responsavel_id,
                t.pagamento_id,
                t.status
            FROM transacoes t
            WHERE t.id = ?
            """

            cursor.execute(query, (transacao_id,))
            t = cursor.fetchone()

            if not t:
                return {
                    'success': False,
                    'error': 'Transação não encontrada'
                }

            # Obter o valor absoluto (para edição)
            valor_abs = abs(t[2])

            transacao = {
                'id': t[0],
                'data': t[1],
                'valor': valor_abs,
                'tipo': t[3],
                'descricao': t[4],
                'conta_id': t[5],
                'categoria_id': t[6],
                'responsavel_id': t[7],
                'pagamento_id': t[8],
                'status': t[9]
            }

            return {
                'success': True,
                'transacao': transacao
            }

        except sqlite3.Error as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()

    @staticmethod
    def atualizar_transacao(transacao_id, dados):
        """
        Atualiza uma transação existente.

        :param transacao_id: ID da transação a ser atualizada
        :param dados: Dicionário com os novos dados
        :return: Dicionário com resultado da operação
        """
        try:
            conn = conectar()
            cursor = conn.cursor()

            # Obter dados atuais da transação para verificar mudanças no saldo
            cursor.execute(
                "SELECT valor, conta_id, tipo FROM transacoes WHERE id = ?",
                (transacao_id,)
            )
            transacao_atual = cursor.fetchone()

            if not transacao_atual:
                return {
                    'success': False,
                    'error': 'Transação não encontrada'
                }

            valor_atual = transacao_atual[0]
            conta_id_atual = transacao_atual[1]
            tipo_atual = transacao_atual[2]

            # Preparar o novo valor com base no tipo
            valor_novo = dados['valor']
            if dados['tipo'] == 'despesa' and valor_novo > 0:
                valor_novo = -valor_novo

            # Atualizar a transação
            cursor.execute(
                """
                UPDATE transacoes
                SET data = ?, valor = ?, tipo = ?, descricao = ?,
                    conta_id = ?, categoria_id = ?, responsavel_id = ?,
                    pagamento_id = ?, status = ?
                WHERE id = ?
                """,
                (
                    dados['data'],
                    valor_novo,
                    dados['tipo'],
                    dados['descricao'],
                    dados['conta_id'],
                    dados['categoria_id'],
                    dados['responsavel_id'],
                    dados['pagamento_id'],
                    dados['status'],
                    transacao_id
                )
            )

            # Atualizar saldos das contas se necessário
            # Se a conta mudou ou o valor mudou
            if (conta_id_atual != dados['conta_id'] or valor_atual != valor_novo) and dados['status'] != 'cancelado':
                # Reverter o efeito no saldo da conta antiga
                if conta_id_atual:
                    cursor.execute(
                        "UPDATE contas SET saldo = saldo - ? WHERE id = ?",
                        (valor_atual, conta_id_atual)
                    )

                # Aplicar o efeito no saldo da nova conta
                if dados['conta_id']:
                    cursor.execute(
                        "UPDATE contas SET saldo = saldo + ? WHERE id = ?",
                        (valor_novo, dados['conta_id'])
                    )

            conn.commit()

            return {
                'success': True,
                'message': 'Transação atualizada com sucesso'
            }

        except sqlite3.Error as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()

    @staticmethod
    def excluir_transacao(transacao_id):
        """
        Exclui uma transação.

        :param transacao_id: ID da transação a ser excluída
        :return: Dicionário com resultado da operação
        """
        try:
            conn = conectar()
            cursor = conn.cursor()

            # Verificar se a transação existe e obter informações para atualizar saldo
            cursor.execute(
                "SELECT valor, conta_id, status FROM transacoes WHERE id = ?",
                (transacao_id,)
            )
            transacao = cursor.fetchone()

            if not transacao:
                return {
                    'success': False,
                    'error': 'Transação não encontrada'
                }

            valor = transacao[0]
            conta_id = transacao[1]
            status = transacao[2]

            # Verificar se a transação faz parte de uma recorrência
            cursor.execute(
                "SELECT id FROM recorrencias WHERE transacao_id = ?",
                (transacao_id,)
            )
            recorrencia = cursor.fetchone()

            # Excluir recorrência se existir
            if recorrencia:
                cursor.execute(
                    "DELETE FROM recorrencias WHERE id = ?",
                    (recorrencia[0],)
                )

            # Excluir a transação
            cursor.execute(
                "DELETE FROM transacoes WHERE id = ?",
                (transacao_id,)
            )

            # Atualizar saldo da conta se a transação não estava cancelada
            if conta_id and status != 'cancelado':
                cursor.execute(
                    "UPDATE contas SET saldo = saldo - ? WHERE id = ?",
                    (valor, conta_id)
                )

            conn.commit()

            return {
                'success': True,
                'message': 'Transação excluída com sucesso'
            }

        except sqlite3.Error as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()


# Funções de interface para o controller

def listar_transacoes(filtros=None):
    """
    Lista transações com base nos filtros fornecidos.

    :param filtros: Dicionário com os filtros a serem aplicados
    :return: Dicionário com resultado e dados
    """
    return TransacoesRepository.buscar_transacoes(filtros)


def obter_transacao(transacao_id):
    """
    Obtém uma transação específica pelo ID.

    :param transacao_id: ID da transação
    :return: Dicionário com dados da transação
    """
    return TransacoesRepository.obter_transacao(transacao_id)


def editar_transacao(transacao_id, dados):
    """
    Edita uma transação existente.

    :param transacao_id: ID da transação
    :param dados: Dicionário com os novos dados
    :return: Dicionário com resultado da operação
    """
    return TransacoesRepository.atualizar_transacao(transacao_id, dados)


def excluir_transacao(transacao_id):
    """
    Exclui uma transação existente.

    :param transacao_id: ID da transação
    :return: Dicionário com resultado da operação
    """
    return TransacoesRepository.excluir_transacao(transacao_id)
