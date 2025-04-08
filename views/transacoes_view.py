"""
Este módulo define a interface de usuário para a inserção de transações.
Ele inclui campos para valor, data, descrição, conta, categoria, responsável e forma de pagamento.
"""

from dash import html, dcc
from datetime import date

import dash_bootstrap_components as dbc


def transacoes_layout():
    """
    Layout da página de inserção de transações.
    """
    return html.Div([
        # Componente para armazenar o tipo da conta selecionada
        dcc.Store(id='transacao-conta-tipo'),

        dbc.Row([
            # Formulário de nova transação
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Nova Transação", className="mb-0")),
                    dbc.CardBody([
                        # Tipo de Transação (Receita/Despesa) - no topo para definir contexto
                        dbc.Row([
                            dbc.Col([
                                html.Label("Tipo de Transação", className="fw-bold mb-2"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Receita", "value": "receita"},
                                        {"label": "Despesa", "value": "despesa"},
                                    ],
                                    value="despesa",  # Valor padrão
                                    id="transacao-tipo",
                                    inline=True,
                                    className="mb-3"
                                ),
                            ]),
                        ]),

                        # Valor e Data
                        dbc.Row([
                            dbc.Col([
                                html.Label("Valor", className="fw-bold"),
                                dbc.InputGroup([
                                    dbc.InputGroupText("R$"),
                                    dbc.Input(
                                        id="transacao-valor",
                                        placeholder="0,00",
                                        type="number",
                                        step="0.01",
                                        min=0,
                                        className="text-end"
                                    ),
                                ], className="mb-3"),
                            ], md=6),
                            dbc.Col([
                                html.Label("Data", className="fw-bold"),
                                dcc.DatePickerSingle(
                                    id="transacao-data",
                                    display_format="DD/MM/YYYY",
                                    date=date.today(),
                                    className="mb-3 w-100"
                                ),
                            ], md=6),
                        ]),

                        # Descrição
                        dbc.Row([
                            dbc.Col([
                                html.Label("Descrição", className="fw-bold"),
                                dbc.Input(
                                    id="transacao-descricao",
                                    placeholder="Descrição da transação",
                                    className="mb-3"
                                ),
                            ]),
                        ]),

                        # Conta e Categoria
                        dbc.Row([
                            dbc.Col([
                                html.Label("Conta", className="fw-bold"),
                                dcc.Dropdown(
                                    id="transacao-conta",
                                    placeholder="Selecione uma conta",
                                    className="mb-3"
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Label("Categoria", className="fw-bold"),
                                dcc.Dropdown(
                                    id="transacao-categoria",
                                    placeholder="Selecione uma categoria",
                                    className="mb-3"
                                ),
                            ], md=6),
                        ]),

                        # Opções de parcelamento (visível apenas para cartões de crédito)
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Parcelamento", className="fw-bold"),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "À vista", "value": "avista"},
                                            {"label": "Parcelado", "value": "parcelado"},
                                        ],
                                        value="avista",
                                        id="transacao-parcelamento-opcao",
                                        className="mb-3"
                                    ),
                                ], md=6),
                                dbc.Col([
                                    html.Label("Número de Parcelas", className="fw-bold"),
                                    dbc.Input(
                                        id="transacao-parcelas",
                                        type="number",
                                        min=2,
                                        max=24,
                                        value=2,
                                        placeholder="Nº de parcelas",
                                        className="mb-3",
                                        disabled=True
                                    ),
                                ], md=6),
                            ]),
                        ], id="div-parcelamento", style={"display": "none"}),

                        # Opção de Transação Recorrente
                        dbc.Row([
                            dbc.Col([
                                html.Label("Transação Recorrente?", className="fw-bold"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Não", "value": "nao"},
                                        {"label": "Sim", "value": "sim"},
                                    ],
                                    value="nao",
                                    id="transacao-recorrente-opcao",
                                    inline=True,
                                    className="mb-3"
                                ),
                            ]),
                        ]),

                        # Opções de recorrência (visível apenas quando recorrente = sim)
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Frequência", className="fw-bold"),
                                    dcc.Dropdown(
                                        id="transacao-frequencia",
                                        options=[
                                            {"label": "Semanal", "value": "semanal"},
                                            {"label": "Mensal", "value": "mensal"},
                                            {"label": "Trimestral", "value": "trimestral"},
                                            {"label": "Semestral", "value": "semestral"},
                                            {"label": "Anual", "value": "anual"},
                                        ],
                                        value="mensal",
                                        placeholder="Selecione a frequência",
                                        className="mb-3"
                                    ),
                                ], md=6),
                                dbc.Col([
                                    html.Label("Número de Ocorrências", className="fw-bold"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="transacao-ocorrencias",
                                            type="number",
                                            min=1,
                                            max=99,
                                            value=12,
                                            placeholder="Quantas vezes a transação se repetirá",
                                            className="mb-3"
                                        ),
                                        dbc.InputGroupText(
                                            html.Span(id="texto-ocorrencias", children="meses"),
                                        ),
                                    ], className="mb-3"),
                                    html.Small(
                                        "Deixe em branco para repetir indefinidamente",
                                        className="text-muted d-block mb-3"
                                    ),
                                ], md=6),
                            ]),
                        ], id="div-recorrencia", style={"display": "none"}),

                        # Responsável e Forma de Pagamento
                        dbc.Row([
                            dbc.Col([
                                html.Label("Responsável", className="fw-bold"),
                                dcc.Dropdown(
                                    id="transacao-responsavel",
                                    placeholder="Selecione um responsável",
                                    className="mb-3"
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Label("Forma de Pagamento", className="fw-bold"),
                                dcc.Dropdown(
                                    id="transacao-pagamento",
                                    placeholder="Selecione uma forma de pagamento",
                                    className="mb-3"
                                ),
                            ], md=6),
                        ]),

                        # Botão de ação e feedback
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Salvar Transação",
                                    id="btn-salvar-transacao",
                                    color="success",
                                    className="w-100 mt-2"
                                ),
                                html.Div(id="transacao-feedback", className="mt-3"),
                            ]),
                        ]),
                    ]),
                ], className="mb-4"),
            ], md=6),

            # Lista de transações recentes
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Transações Recentes", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id="lista-transacoes", className="mb-3"),
                        dbc.Button(
                            "Atualizar Lista",
                            id="btn-atualizar-transacoes",
                            color="secondary",
                            className="mt-2"
                        ),
                    ]),
                ]),
            ], md=6),
        ]),
    ], className="p-3")
