"""
Este módulo define a interface de usuário para o cadastro de itens.
Ele inclui campos para categorias, contas, tipos de pagamento e responsáveis.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from views.cadastros.categorias import cadastro_categoria, tabela_categorias
from views.cadastros.contas import cadastro_conta, tabela_contas
from views.cadastros.pagamentos import cadastro_pagamento, tabela_pagamentos
from views.cadastros.responsaveis import cadastro_responsavel, tabela_responsaveis
from views.cadastros.modais import (
    modal_editar_categoria,
    modal_editar_conta,
    modal_editar_pagamento,
    modal_editar_responsavel
)


def cadastros_layout():
    """
    Layout da página de cadastro de itens.
    """
    return html.Div([
        html.H3("Cadastrar Itens", className="mb-4"),

        # Modais para edição
        modal_editar_categoria(),
        modal_editar_conta(),
        modal_editar_pagamento(),
        modal_editar_responsavel(),

        # Store para armazenar o ID do item sendo editado
        dcc.Store(id='item-id-categoria'),
        dcc.Store(id='item-id-conta'),
        dcc.Store(id='item-id-pagamento'),
        dcc.Store(id='item-id-responsavel'),

        dbc.Row([
            # Coluna da esquerda - Categorias e Tipos de Pagamento
            dbc.Col([
                # Componentes de Categoria
                cadastro_categoria(),
                tabela_categorias(),

                # Componentes de Tipos de Pagamento
                cadastro_pagamento(),
                tabela_pagamentos(),
            ], md=6, className="px-3"),

            # Coluna da direita - Contas e Responsáveis
            dbc.Col([
                # Componentes de Conta
                cadastro_conta(),
                tabela_contas(),

                # Componentes de Responsável
                cadastro_responsavel(),
                tabela_responsaveis(),
            ], md=6, className="px-3")
        ])
    ], className="container py-4")


# O callback de toggle para os campos do formulário de conta já está definido no arquivo contas.py
# O mesmo vale para o callback de toggle dos campos do modal de edição no arquivo modais.py
