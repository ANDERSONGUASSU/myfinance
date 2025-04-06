"""
Este módulo define os callbacks para o cadastro e gerenciamento de categorias.
"""

from dash import callback, Input, Output, State
import dash_bootstrap_components as dbc
from controllers.cadastro.categorias import (
    cadastrar_categoria as controller_cadastrar_categoria,
    listar_categorias as controller_listar_categorias,
    excluir_categoria as controller_excluir_categoria,
    editar_categoria as controller_editar_categoria,
)

# Callback para salvar uma nova categoria
@callback(
    [
        Output('feedback-categoria', 'children', allow_duplicate=True),
        Output('input-categoria', 'value', allow_duplicate=True),
    ],
    [Input('btn-salvar-categoria', 'n_clicks')],
    [State('input-categoria', 'value')],
    prevent_initial_call=True,
)
def salvar_categoria(n_clicks, nome):
    """
    Callback para salvar uma nova categoria.
    """
    if n_clicks is None:
        return [None, '']

    if nome is None or not nome.strip():
        return [
            dbc.Alert(
                'O nome da categoria não pode ser vazio.', color='danger'
            ),
            nome,
        ]

    resultado = controller_cadastrar_categoria(nome)
    if resultado['success']:
        return [dbc.Alert(resultado['message'], color='success'), '']
    else:
        return [dbc.Alert(resultado['message'], color='danger'), nome]


# Callback para atualizar a lista de categorias
@callback(
    Output('tabela-categorias', 'data'),
    [
        Input('btn-listar-categorias', 'n_clicks'),
        Input('btn-salvar-categoria', 'n_clicks'),
        Input('modal-editar-categoria', 'is_open'),
        Input('btn-excluir-categoria', 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def atualizar_categorias(
    n_clicks_atualizar, n_clicks_salvar, modal_aberto, n_clicks_excluir
):
    """
    Callback para atualizar a lista de categorias.
    Atualiza quando o botão é clicado ou quando uma categoria é salva/editada.
    """
    resultado = controller_listar_categorias()
    if resultado['success']:
        categorias = resultado['categorias']
        # Simplificamos os botões para usar apenas texto, já que HTML não é bem suportado
        for cat in categorias:
            cat[
                'acoes'
            ] = 'Editar | Excluir'  # Usando string literal em vez de f-string
        return categorias
    else:
        return []


# Callback para excluir uma categoria
@callback(
    [Output('feedback-categoria', 'children', allow_duplicate=True)],
    [Input('btn-excluir-categoria', 'n_clicks')],
    [
        State('tabela-categorias', 'selected_rows'),
        State('tabela-categorias', 'data'),
    ],
    prevent_initial_call=True,
)
def excluir_categoria(n_clicks, selected_rows, data):
    """
    Callback para excluir uma categoria.
    """
    if n_clicks is None:
        return [dbc.Alert('Nenhuma categoria selecionada.', color='warning')]

    if not selected_rows or len(selected_rows) == 0:
        return [dbc.Alert('Nenhuma categoria selecionada.', color='warning')]

    row_idx = selected_rows[0]
    if row_idx >= len(data):
        return [dbc.Alert('Seleção inválida.', color='warning')]

    categoria_id = data[row_idx]['id']
    resultado = controller_excluir_categoria(categoria_id)

    if resultado['success']:
        return [dbc.Alert(resultado['message'], color='success')]
    else:
        return [dbc.Alert(resultado['message'], color='danger')]


# Callback para abrir o modal de edição quando uma célula da tabela é clicada
@callback(
    [
        Output('modal-editar-categoria', 'is_open'),
        Output('input-editar-categoria', 'value'),
        Output('item-id-categoria', 'data'),
    ],
    [Input('tabela-categorias', 'active_cell')],
    [
        State('tabela-categorias', 'data'),
        State('modal-editar-categoria', 'is_open'),
    ],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_celula(active_cell, data, is_open):
    """
    Callback para abrir o modal de edição quando uma célula da tabela é clicada.
    """
    if active_cell is None:
        return is_open, '', None

    row = active_cell['row']
    if row >= len(data):
        return is_open, '', None

    categoria = data[row]
    return not is_open, categoria['nome'], categoria['id']


# Callback para abrir o modal de edição quando o botão Editar é clicado
@callback(
    [
        Output('modal-editar-categoria', 'is_open', allow_duplicate=True),
        Output('input-editar-categoria', 'value', allow_duplicate=True),
        Output('item-id-categoria', 'data', allow_duplicate=True),
    ],
    [Input('btn-editar-categoria', 'n_clicks')],
    [
        State('tabela-categorias', 'selected_rows'),
        State('tabela-categorias', 'data'),
        State('modal-editar-categoria', 'is_open'),
    ],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_botao(n_clicks, selected_rows, data, is_open):
    """
    Callback para abrir o modal de edição quando o botão é clicado.
    """
    if n_clicks is None:
        return is_open, '', None

    if not selected_rows or len(selected_rows) == 0:
        return is_open, '', None

    row_idx = selected_rows[0]
    if row_idx >= len(data):
        return is_open, '', None

    categoria = data[row_idx]
    return True, categoria['nome'], categoria['id']


# Callback para salvar edição de categoria
@callback(
    [
        Output('feedback-editar-categoria', 'children', allow_duplicate=True),
        Output('modal-editar-categoria', 'is_open', allow_duplicate=True),
    ],
    [Input('btn-salvar-editar-categoria', 'n_clicks')],
    [
        State('input-editar-categoria', 'value'),
        State('item-id-categoria', 'data'),
    ],
    prevent_initial_call=True,
)
def salvar_edicao_categoria(n_clicks, novo_nome, categoria_id):
    """
    Callback para salvar a edição de uma categoria.
    """
    if n_clicks is None:
        return None, False

    if categoria_id is None:
        return (
            dbc.Alert('Erro: categoria não selecionada.', color='danger'),
            False,
        )

    if novo_nome is None or not novo_nome.strip():
        return (
            dbc.Alert(
                'O nome da categoria não pode ser vazio.', color='danger'
            ),
            False,
        )

    resultado = controller_editar_categoria(categoria_id, novo_nome)
    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success'), False
    else:
        return dbc.Alert(resultado['message'], color='danger'), True


# Callback para cancelar edição
@callback(
    Output('modal-editar-categoria', 'is_open', allow_duplicate=True),
    [Input('btn-cancelar-editar-categoria', 'n_clicks')],
    prevent_initial_call=True,
)
def cancelar_edicao(n_clicks):
    """
    Callback para fechar o modal ao cancelar a edição.
    """
    return False
