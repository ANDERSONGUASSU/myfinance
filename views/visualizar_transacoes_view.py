"""
Este módulo define o layout da página de visualização de transações,
com filtros, tabela de transações e opções para editar/excluir.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import datetime


def get_current_year_month():
    """Retorna o ano e mês atual"""
    now = datetime.datetime.now()
    return now.year, now.month


def get_layout():
    """
    Retorna o layout da página de visualização de transações.
    """
    ano_atual, mes_atual = get_current_year_month()

    return html.Div([
        # Título
        html.H3("Visualizar Transações", className="mb-4"),

        # Filtros
        dbc.Card([
            dbc.CardHeader("Filtros", className="bg-primary text-white"),
            dbc.CardBody([
                dbc.Row([
                    # Filtro de Período
                    dbc.Col([
                        html.Label("Período"),
                        dbc.RadioItems(
                            id="filtro-periodo",
                            options=[
                                {"label": "Mês específico", "value": "mes"},
                                {"label": "Ano inteiro", "value": "ano"},
                                {"label": "Todos", "value": "todos"}
                            ],
                            value="mes",
                            inline=True,
                            className="mb-2"
                        ),
                    ], width=12, lg=4),

                    # Seleção de Mês
                    dbc.Col([
                        html.Label("Mês"),
                        dcc.Dropdown(
                            id="filtro-mes",
                            options=[
                                {"label": "Janeiro", "value": 1},
                                {"label": "Fevereiro", "value": 2},
                                {"label": "Março", "value": 3},
                                {"label": "Abril", "value": 4},
                                {"label": "Maio", "value": 5},
                                {"label": "Junho", "value": 6},
                                {"label": "Julho", "value": 7},
                                {"label": "Agosto", "value": 8},
                                {"label": "Setembro", "value": 9},
                                {"label": "Outubro", "value": 10},
                                {"label": "Novembro", "value": 11},
                                {"label": "Dezembro", "value": 12}
                            ],
                            value=mes_atual,
                            clearable=False,
                            className="mb-2"
                        ),
                    ], width=6, lg=4),

                    # Seleção de Ano
                    dbc.Col([
                        html.Label("Ano"),
                        dcc.Dropdown(
                            id="filtro-ano",
                            options=[
                                {"label": str(year), "value": year} for year in range(ano_atual - 5, ano_atual + 2)
                            ],
                            value=ano_atual,
                            clearable=False,
                            className="mb-2"
                        ),
                    ], width=6, lg=4),
                ]),

                dbc.Row([
                    # Filtros adicionais
                    dbc.Col([
                        html.Label("Conta"),
                        dcc.Dropdown(
                            id="filtro-conta",
                            options=[],
                            placeholder="Todas as contas",
                            className="mb-2"
                        ),
                    ], width=12, md=6, lg=3),

                    dbc.Col([
                        html.Label("Categoria"),
                        dcc.Dropdown(
                            id="filtro-categoria",
                            options=[],
                            placeholder="Todas as categorias",
                            className="mb-2"
                        ),
                    ], width=12, md=6, lg=3),

                    dbc.Col([
                        html.Label("Tipo"),
                        dcc.Dropdown(
                            id="filtro-tipo",
                            options=[
                                {"label": "Todas", "value": "todas"},
                                {"label": "Receitas", "value": "receita"},
                                {"label": "Despesas", "value": "despesa"}
                            ],
                            value="todas",
                            clearable=False,
                            className="mb-2"
                        ),
                    ], width=12, md=6, lg=3),

                    dbc.Col([
                        html.Label("Status"),
                        dcc.Dropdown(
                            id="filtro-status",
                            options=[
                                {"label": "Todos", "value": "todos"},
                                {"label": "Pendentes", "value": "pendente"},
                                {"label": "Pagos", "value": "pago"},
                                {"label": "Cancelados", "value": "cancelado"}
                            ],
                            value="todos",
                            clearable=False,
                            className="mb-2"
                        ),
                    ], width=12, md=6, lg=3),
                ]),

                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Aplicar Filtros",
                            id="btn-aplicar-filtros",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Limpar Filtros",
                            id="btn-limpar-filtros",
                            color="secondary"
                        ),
                    ], width=12, className="d-flex justify-content-end mt-3")
                ])
            ])
        ], className="mb-4"),

        # Tabela de transações
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col(html.H5("Transações", className="m-0"), width="auto"),
                    dbc.Col([
                        dbc.Badge(id="badge-total-receitas", color="success", className="me-1"),
                        dbc.Badge(id="badge-total-despesas", color="danger", className="me-1"),
                        dbc.Badge(id="badge-saldo-periodo", color="primary")
                    ], width="auto", className="ms-auto")
                ], className="d-flex align-items-center")
            ]),
            dbc.CardBody([
                html.Div(id="tabela-visualizar-transacoes", className="table-responsive")
            ])
        ]),

        # Modal de confirmação para exclusão
        dbc.Modal([
            dbc.ModalHeader("Confirmar Exclusão"),
            dbc.ModalBody("Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita."),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="btn-cancelar-exclusao", className="me-2", color="secondary"),
                dbc.Button("Excluir", id="btn-confirmar-exclusao", color="danger")
            ])
        ], id="modal-confirmar-exclusao"),

        # Modal para editar transação
        dbc.Modal([
            dbc.ModalHeader("Editar Transação"),
            dbc.ModalBody([
                # Form para edição
                dbc.Form([
                    dbc.Row([
                        # ID oculto da transação
                        dcc.Store(id="editar-transacao-id"),

                        # Tipo de transação (Receita/Despesa)
                        dbc.Col([
                            html.Label("Tipo"),
                            dbc.RadioItems(
                                id="editar-transacao-tipo",
                                options=[
                                    {"label": "Receita", "value": "receita"},
                                    {"label": "Despesa", "value": "despesa"}
                                ],
                                inline=True,
                                className="mb-3"
                            )
                        ], width=12),

                        # Valor
                        dbc.Col([
                            html.Label("Valor"),
                            dbc.InputGroup([
                                dbc.InputGroupText("R$"),
                                dbc.Input(id="editar-transacao-valor", type="number", min=0, step=0.01)
                            ], className="mb-3")
                        ], width=12, md=6),

                        # Data
                        dbc.Col([
                            html.Label("Data"),
                            dcc.DatePickerSingle(
                                id="editar-transacao-data",
                                display_format="DD/MM/YYYY",
                                className="mb-3 w-100"
                            )
                        ], width=12, md=6),

                        # Descrição
                        dbc.Col([
                            html.Label("Descrição"),
                            dbc.Input(id="editar-transacao-descricao", type="text", className="mb-3")
                        ], width=12),

                        # Conta
                        dbc.Col([
                            html.Label("Conta"),
                            dcc.Dropdown(id="editar-transacao-conta", options=[], className="mb-3")
                        ], width=12, md=6),

                        # Categoria
                        dbc.Col([
                            html.Label("Categoria"),
                            dcc.Dropdown(id="editar-transacao-categoria", options=[], className="mb-3")
                        ], width=12, md=6),

                        # Responsável
                        dbc.Col([
                            html.Label("Responsável"),
                            dcc.Dropdown(id="editar-transacao-responsavel", options=[], className="mb-3")
                        ], width=12, md=6),

                        # Forma de Pagamento
                        dbc.Col([
                            html.Label("Forma de Pagamento"),
                            dcc.Dropdown(id="editar-transacao-pagamento", options=[], className="mb-3")
                        ], width=12, md=6),

                        # Status
                        dbc.Col([
                            html.Label("Status"),
                            dcc.Dropdown(
                                id="editar-transacao-status",
                                options=[
                                    {"label": "Pendente", "value": "pendente"},
                                    {"label": "Pago", "value": "pago"},
                                    {"label": "Cancelado", "value": "cancelado"}
                                ],
                                className="mb-3"
                            )
                        ], width=12)
                    ])
                ])
            ]),
            dbc.ModalFooter([
                html.Div(id="editar-transacao-feedback", className="me-auto"),
                dbc.Button("Cancelar", id="btn-cancelar-edicao", className="me-2", color="secondary"),
                dbc.Button("Salvar", id="btn-salvar-edicao", color="primary")
            ])
        ], id="modal-editar-transacao", size="lg"),

        # Store para ID da transação a ser excluída
        dcc.Store(id="transacao-excluir-id")
    ])
