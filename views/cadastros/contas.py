"""
Este módulo define os componentes de interface para o cadastro e listagem de contas.
"""

from dash import html, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc


def cadastro_conta():
    """
    Componente para cadastro de contas.
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Nova Conta", className="mb-0")),
        dbc.CardBody([
            dbc.Input(id='input-conta', placeholder='Nome da conta', className="mb-2"),
            dbc.Label("Tipo de Conta:"),
            dbc.Select(
                id='select-tipo-conta',
                options=[
                    {'label': 'Conta Corrente', 'value': 'conta'},
                    {'label': 'Cartão de Crédito', 'value': 'cartao'},
                    {'label': 'Poupança', 'value': 'poupanca'},
                    {'label': 'Carteira', 'value': 'carteira'}
                ],
                value='conta',
                className="mb-3"
            ),

            # Campos especiais para cartão
            html.Div(id='campos-cartao-credito', children=[
                html.Hr(),
                html.H6("Configurações do Cartão de Crédito", className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Dia de Fechamento:"),
                        dbc.Input(id='input-dia-fechamento', type='number', min=1, max=31),
                    ], md=6),
                    dbc.Col([
                        dbc.Label("Dia de Vencimento:"),
                        dbc.Input(id='input-dia-vencimento', type='number', min=1, max=31),
                    ], md=6),
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Limite do Cartão:"),
                        dbc.Input(id='input-limite-credito', type='number', min=0),
                    ]),
                ]),
            ], style={'display': 'none'}),

            # Campo para saldo inicial (outros tipos)
            html.Div(id='campos-outros-tipos', children=[
                html.Hr(),
                dbc.Label("Saldo Inicial:"),
                dbc.Input(id='input-saldo-inicial', type='number'),
            ], style={'display': 'block'}),

            dbc.Button("Salvar", id='btn-salvar-conta', color='success', className='mt-3'),
            html.Div(id='feedback-conta', className='mt-2')
        ])
    ], className="mb-3")


def tabela_contas():
    """
    Componente para exibição de contas cadastradas.
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Contas Cadastradas", className="mb-0")),
        dbc.CardBody([
            html.Div(id='div-tabela-contas', children=[
                dash_table.DataTable(
                    id='tabela-contas',
                    columns=[
                        {"name": "ID", "id": "id"},
                        {"name": "Nome", "id": "nome"},
                        {"name": "Tipo", "id": "tipo"},
                        {"name": "Saldo", "id": "saldo", "type": "numeric", "format": {"specifier": ",.2f"}},
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
                id='btn-atualizar-contas',
                color='secondary',
                className='mt-3'
            )
        ])
    ], className="mb-4")


@callback(
    [Output('campos-cartao-credito', 'style'),
     Output('campos-outros-tipos', 'style')],
    [Input('select-tipo-conta', 'value')]
)
def toggle_campos_conta(tipo_conta):
    """
    Callback para mostrar/esconder campos específicos de acordo com o tipo de conta.
    """
    if tipo_conta == 'cartao':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}
