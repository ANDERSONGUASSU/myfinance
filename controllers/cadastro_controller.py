"""
Este módulo define as funções de controller para o cadastro de itens.
Ele inclui funções para manipular categorias, contas, tipos de pagamento e responsáveis.
"""

from dash import Input, Output, State, callback
from models.database import conectar
import controllers.cadastro


# Removido para evitar duplicação de callbacks
# @callback(
#     Output('feedback-categoria', 'children', allow_duplicate=True),
#     [Input('btn-salvar-categoria', 'n_clicks')],
#     [State('input-categoria', 'value')],
#     prevent_initial_call=True
# )
# def salvar_categoria(n_clicks, nome):
#     """
#     Salvar uma nova categoria no banco de dados.
#     """
#     if not nome:
#         return "Por favor, informe o nome da categoria."

#     conn = conectar()
#     cursor = conn.cursor()
#
#     try:
#         cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
#         conn.commit()
#         return "Categoria salva com sucesso!"
#     except Exception as e:
#         return f"Erro ao salvar categoria: {str(e)}"
#     finally:
#         conn.close()


@callback(
    Output('feedback-conta', 'children', allow_duplicate=True),
    [Input('btn-salvar-conta', 'n_clicks')],
    [
        State('input-conta', 'value'),
        State('select-tipo-conta', 'value'),
        State('input-dia-fechamento', 'value'),
        State('input-dia-vencimento', 'value'),
        State('input-limite-credito', 'value'),
        State('input-saldo-inicial', 'value'),
    ],
    prevent_initial_call=True,
)
def salvar_conta(
    n_clicks,
    nome,
    tipo,
    dia_fechamento,
    dia_vencimento,
    limite_credito,
    saldo_inicial,
):
    """
    Salvar uma nova conta no banco de dados.
    """
    if not nome:
        return 'Por favor, informe o nome da conta.'

    if not tipo:
        return 'Por favor, selecione o tipo da conta.'

    conn = conectar()
    cursor = conn.cursor()

    try:
        if tipo == 'cartao':
            # Validações específicas para cartão de crédito
            if not dia_fechamento:
                return 'Por favor, informe o dia de fechamento do cartão.'

            if not dia_vencimento:
                return 'Por favor, informe o dia de vencimento do cartão.'

            if limite_credito is None:
                return 'Por favor, informe o limite do cartão.'

            cursor.execute(
                """INSERT INTO contas 
                   (nome, tipo, dia_fechamento, dia_vencimento, limite_credito, saldo) 
                   VALUES (?, ?, ?, ?, ?, 0.0)""",
                (nome, tipo, dia_fechamento, dia_vencimento, limite_credito),
            )
        else:
            # Para outros tipos de conta, só é necessário o saldo inicial
            saldo = saldo_inicial if saldo_inicial is not None else 0.0

            cursor.execute(
                'INSERT INTO contas (nome, tipo, saldo) VALUES (?, ?, ?)',
                (nome, tipo, saldo),
            )

        conn.commit()
        return 'Conta salva com sucesso!'
    except Exception as e:
        return f'Erro ao salvar conta: {str(e)}'
    finally:
        conn.close()


@callback(
    Output('feedback-pagamento', 'children', allow_duplicate=True),
    [Input('btn-salvar-pagamento', 'n_clicks')],
    [State('input-pagamento', 'value')],
    prevent_initial_call=True,
)
def salvar_pagamento(n_clicks, tipo):
    """
    Salvar um novo tipo de pagamento no banco de dados.
    """
    if not tipo:
        return 'Por favor, informe o tipo de pagamento.'

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO pagamentos (tipo) VALUES (?)', (tipo,))
        conn.commit()
        return 'Tipo de pagamento salvo com sucesso!'
    except Exception as e:
        return f'Erro ao salvar tipo de pagamento: {str(e)}'
    finally:
        conn.close()


@callback(
    Output('feedback-responsavel', 'children', allow_duplicate=True),
    [Input('btn-salvar-responsavel', 'n_clicks')],
    [State('input-responsavel', 'value')],
    prevent_initial_call=True,
)
def salvar_responsavel(n_clicks, nome):
    """
    Salvar um novo responsável no banco de dados.
    """
    if not nome:
        return 'Por favor, informe o nome do responsável.'

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO responsaveis (nome) VALUES (?)', (nome,))
        conn.commit()
        return 'Responsável salvo com sucesso!'
    except Exception as e:
        return f'Erro ao salvar responsável: {str(e)}'
    finally:
        conn.close()
