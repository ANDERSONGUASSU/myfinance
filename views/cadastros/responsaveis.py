"""
Este módulo define os componentes de interface para o cadastro e listagem de responsáveis.
"""

from dash import html, dash_table
import dash_bootstrap_components as dbc


def cadastro_responsavel():
    """
    Componente para cadastro de responsáveis.
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Novo Responsável", className="mb-0")),
        dbc.CardBody([
            dbc.Input(id='input-responsavel', placeholder='Nome do responsável', className="mb-2"),
            dbc.Button("Salvar", id='btn-salvar-responsavel', color='success', className='mt-2'),
            html.Div(id='feedback-responsavel', className='mt-2')
        ])
    ], className="mb-3")


def tabela_responsaveis():
    """
    Componente para exibição de responsáveis cadastrados.
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Responsáveis Cadastrados", className="mb-0")),
        dbc.CardBody([
            html.Div(id='div-tabela-responsaveis', children=[
                dash_table.DataTable(
                    id='tabela-responsaveis',
                    columns=[
                        {"name": "ID", "id": "id"},
                        {"name": "Nome", "id": "nome"},
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
                id='btn-atualizar-responsaveis',
                color='secondary',
                className='mt-3'
            )
        ])
    ])
