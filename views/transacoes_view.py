"""
Este módulo define a interface de usuário para a inserção de transações.
Ele inclui campos para valor, data, descrição, conta, categoria, responsável e forma de pagamento.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def transacoes_layout():
    """
    Layout da página de inserção de transações.
    """
    return html.Div(
        [
            html.H3('Inserir Transação'),
            dbc.Form(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id='transacao-valor',
                                    placeholder='Valor',
                                    type='number',
                                )
                            ),
                            dbc.Col(dcc.DatePickerSingle(id='transacao-data')),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id='transacao-descricao',
                                    placeholder='Descrição',
                                )
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id='transacao-conta', placeholder='Conta'
                                )
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='transacao-categoria',
                                    placeholder='Categoria',
                                )
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id='transacao-responsavel',
                                    placeholder='Responsável',
                                )
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='transacao-pagamento',
                                    placeholder='Forma de Pagamento',
                                )
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.RadioItems(
                                    options=[
                                        {
                                            'label': 'Receita',
                                            'value': 'receita',
                                        },
                                        {
                                            'label': 'Despesa',
                                            'value': 'despesa',
                                        },
                                    ],
                                    id='transacao-tipo',
                                    inline=True,
                                )
                            ),
                        ]
                    ),
                    html.Br(),
                    dbc.Button(
                        'Salvar Transação',
                        id='btn-salvar-transacao',
                        color='primary',
                    ),
                    html.Div(id='transacao-feedback', className='mt-2'),
                ]
            ),
        ]
    )
