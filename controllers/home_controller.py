from dash import dcc, html
from views.transacoes_view import transacoes_layout
from views.cadastros_view import cadastros_layout


def layout():
    return html.Div(
        [
            dcc.Tabs(
                id='tabs',
                value='transacoes',
                children=[
                    dcc.Tab(label='Transações', value='transacoes'),
                    dcc.Tab(label='Cadastros', value='cadastros'),
                ],
            ),
            html.Div(id='tabs-content'),
        ]
    )
