"""
Este módulo define os componentes de interface para o cadastro e listagem de categorias.
"""

from dash import html, dash_table
import dash_bootstrap_components as dbc


def cadastro_categoria():
    """
    Componente para cadastro de categorias.
    """
    return dbc.Card(
        [
            dbc.CardHeader(html.H5('Nova Categoria', className='mb-0')),
            dbc.CardBody(
                [
                    dbc.Input(
                        id='input-categoria',
                        placeholder='Nome da categoria',
                        className='mb-2',
                    ),
                    dbc.Button(
                        'Salvar',
                        id='btn-salvar-categoria',
                        color='success',
                        className='mt-2',
                    ),
                    html.Div(id='feedback-categoria', className='mt-2'),
                ]
            ),
        ],
        className='mb-3',
    )


def tabela_categorias():
    """
    Componente para exibição de categorias cadastradas.
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5('Categorias Cadastradas', className='mb-0')
            ),
            dbc.CardBody(
                [
                    html.Div(
                        id='div-tabela-categorias',
                        children=[
                            dash_table.DataTable(
                                id='tabela-categorias',
                                columns=[
                                    {'name': 'ID', 'id': 'id'},
                                    {'name': 'Nome', 'id': 'nome'},
                                    {
                                        'name': 'Ações',
                                        'id': 'acoes',
                                        # Não usamos presentation markdown mais
                                        'type': 'text',
                                    },
                                ],
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '8px',
                                },
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)',
                                    },
                                    {
                                        'if': {'column_id': 'acoes'},
                                        'color': '#007bff',
                                        'cursor': 'pointer',
                                        'fontWeight': 'bold',
                                    },
                                ],
                                page_size=5,
                                page_action='native',
                                sort_action='native',
                                row_selectable='single',  # Permite seleção de linhas
                                cell_selectable=True,  # Permite clicar nas células
                            )
                        ],
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                'Atualizar Lista',
                                id='btn-listar-categorias',
                                color='secondary',
                                className='me-2',
                            ),
                            dbc.Button(
                                'Editar Selecionada',
                                id='btn-editar-categoria',
                                color='primary',
                                className='me-2',
                            ),
                            dbc.Button(
                                'Excluir Selecionada',
                                id='btn-excluir-categoria',
                                color='danger',
                            ),
                        ],
                        className='mt-3 d-flex',
                    ),
                ]
            ),
        ],
        className='mb-4',
    )
