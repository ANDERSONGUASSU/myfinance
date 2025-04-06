"""
Este módulo define os modais para edição de itens cadastrados.
"""

from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc


# Modal para edição de categorias
def modal_editar_categoria():
    """
    Modal para edição de categorias.
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Editar Categoria"),
            dbc.ModalBody([
                dbc.Input(id='input-editar-categoria', placeholder='Nome da categoria'),
                html.Div(id='feedback-editar-categoria', className='mt-2')
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id='btn-cancelar-editar-categoria', className="me-2"),
                dbc.Button("Salvar", id='btn-salvar-editar-categoria', color='success'),
            ]),
        ],
        id='modal-editar-categoria',
        is_open=False,
    )


# Modal para edição de contas
def modal_editar_conta():
    """
    Modal para edição de contas.
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Editar Conta"),
            dbc.ModalBody([
                dbc.Input(id='input-editar-conta', placeholder='Nome da conta', className="mb-2"),
                dbc.Label("Tipo de Conta:"),
                dbc.Select(
                    id='select-editar-tipo-conta',
                    options=[
                        {'label': 'Conta Corrente', 'value': 'conta'},
                        {'label': 'Cartão de Crédito', 'value': 'cartao'},
                        {'label': 'Poupança', 'value': 'poupanca'},
                        {'label': 'Carteira', 'value': 'carteira'}
                    ],
                    className="mb-3"
                ),

                # Campos especiais para cartão
                html.Div(id='campos-editar-cartao-credito', children=[
                    html.Hr(),
                    html.H6("Configurações do Cartão de Crédito", className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Dia de Fechamento:"),
                            dbc.Input(id='input-editar-dia-fechamento', type='number', min=1, max=31),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Dia de Vencimento:"),
                            dbc.Input(id='input-editar-dia-vencimento', type='number', min=1, max=31),
                        ], md=6),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Limite do Cartão:"),
                            dbc.Input(id='input-editar-limite-credito', type='number', min=0),
                        ]),
                    ]),
                ], style={'display': 'none'}),

                # Campo para saldo inicial (outros tipos)
                html.Div(id='campos-editar-outros-tipos', children=[
                    html.Hr(),
                    dbc.Label("Saldo Atual:"),
                    dbc.Input(id='input-editar-saldo', type='number'),
                ], style={'display': 'block'}),

                html.Div(id='feedback-editar-conta', className='mt-2')
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id='btn-cancelar-editar-conta', className="me-2"),
                dbc.Button("Salvar", id='btn-salvar-editar-conta', color='success'),
            ]),
        ],
        id='modal-editar-conta',
        is_open=False,
        size="lg",
    )


# Modal para edição de tipos de pagamento
def modal_editar_pagamento():
    """
    Modal para edição de tipos de pagamento.
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Editar Tipo de Pagamento"),
            dbc.ModalBody([
                dbc.Input(id='input-editar-pagamento', placeholder='Nome do tipo de pagamento'),
                html.Div(id='feedback-editar-pagamento', className='mt-2')
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id='btn-cancelar-editar-pagamento', className="me-2"),
                dbc.Button("Salvar", id='btn-salvar-editar-pagamento', color='success'),
            ]),
        ],
        id='modal-editar-pagamento',
        is_open=False,
    )


# Modal para edição de responsáveis
def modal_editar_responsavel():
    """
    Modal para edição de responsáveis.
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Editar Responsável"),
            dbc.ModalBody([
                dbc.Input(id='input-editar-responsavel', placeholder='Nome do responsável'),
                html.Div(id='feedback-editar-responsavel', className='mt-2')
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id='btn-cancelar-editar-responsavel', className="me-2"),
                dbc.Button("Salvar", id='btn-salvar-editar-responsavel', color='success'),
            ]),
        ],
        id='modal-editar-responsavel',
        is_open=False,
    )

@callback(
    [Output('campos-editar-cartao-credito', 'style'),
     Output('campos-editar-outros-tipos', 'style')],
    [Input('select-editar-tipo-conta', 'value')]
)
def toggle_campos_editar_conta(tipo_conta):
    """
    Callback para mostrar/esconder campos específicos de acordo com o tipo de conta no modal de edição.
    """
    if tipo_conta == 'cartao':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}
