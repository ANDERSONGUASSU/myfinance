"""
Este módulo define os componentes de interface para o cadastro e listagem de tipos de pagamento.
"""

from dash import html, dash_table
import dash_bootstrap_components as dbc


def cadastro_pagamento():
    """
    Componente para cadastro de tipos de pagamento.
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Novo Tipo de Pagamento", className="mb-0")),
        dbc.CardBody([
            dbc.Input(id='input-pagamento', placeholder='Ex: Pix, Boleto', className="mb-2"),
            dbc.Button("Salvar", id='btn-salvar-pagamento', color='success', className='mt-2'),
            html.Div(id='feedback-pagamento', className='mt-2')
        ])
    ], className="mb-3")


def tabela_pagamentos():
    """
    Componente para exibição de tipos de pagamento cadastrados.
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Tipos de Pagamento Cadastrados", className="mb-0")),
        dbc.CardBody([
            html.Div(id='div-tabela-pagamentos', children=[
                dash_table.DataTable(
                    id='tabela-pagamentos',
                    columns=[
                        {"name": "ID", "id": "id"},
                        {"name": "Tipo", "id": "tipo"},
                        {"name": "Ações", "id": "acoes", "presentation": "markdown"}
                    ],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    page_size=5,
                    page_action='native',
                    sort_action='native',
                )
            ]),
            dbc.Button(
                "Atualizar Lista",
                id='btn-atualizar-pagamentos',
                color='secondary',
                className='mt-3'
            )
        ])
    ])
