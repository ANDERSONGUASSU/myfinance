"""
Este módulo define os callbacks para o cadastro, edição e exclusão de responsáveis.
"""

from dash import callback, Output, Input, State, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from controllers.cadastro.responsaveis import (
    listar_responsaveis as controller_listar_responsaveis,
    excluir_responsavel as controller_excluir_responsavel,
    editar_responsavel as controller_editar_responsavel,
)


@callback(
    Output('div-tabela-responsaveis', 'children', allow_duplicate=True),
    [
        Input('btn-atualizar-responsaveis', 'n_clicks'),
        Input('btn-salvar-responsavel', 'n_clicks'),
        Input('btn-salvar-editar-responsavel', 'n_clicks'),
        Input('btn-excluir-responsavel', 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def atualizar_responsaveis(n_atualizar, n_salvar, n_editar, n_excluir):
    """
    Atualiza a tabela de responsáveis.
    """
    resultado = controller_listar_responsaveis()
    if not resultado['success']:
        return html.Div(
            dbc.Alert(
                f"Erro ao carregar responsáveis: {resultado.get('message')}",
                color='danger',
            )
        )

    from dash import dash_table

    responsaveis = resultado['responsaveis']
    for resp in responsaveis:
        resp['acoes'] = 'Editar | Excluir'

    return dash_table.DataTable(
        id='tabela-responsaveis',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Nome', 'id': 'nome'},
            {'name': 'Ações', 'id': 'acoes', 'type': 'text'},
        ],
        data=responsaveis,
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
        row_selectable='single',
        cell_selectable=True,
    )


@callback(
    [
        Output('modal-editar-responsavel', 'is_open', allow_duplicate=True),
        Output('input-editar-responsavel', 'value', allow_duplicate=True),
        Output('item-id-responsavel', 'data', allow_duplicate=True),
    ],
    [Input('tabela-responsaveis', 'active_cell')],
    [State('tabela-responsaveis', 'data')],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_celula(active_cell, data):
    """
    Abre o modal de edição de responsável quando uma célula da tabela é clicada.
    """
    if active_cell is None:
        raise PreventUpdate

    row_idx = active_cell['row']
    col_id = active_cell['column_id']

    if col_id != 'acoes':
        raise PreventUpdate

    responsavel = data[row_idx]
    return True, responsavel['nome'], {'id': responsavel['id']}


@callback(
    [
        Output('modal-editar-responsavel', 'is_open', allow_duplicate=True),
        Output('input-editar-responsavel', 'value', allow_duplicate=True),
        Output('item-id-responsavel', 'data', allow_duplicate=True),
    ],
    [Input('btn-editar-responsavel', 'n_clicks')],
    [
        State('tabela-responsaveis', 'selected_rows'),
        State('tabela-responsaveis', 'data'),
    ],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_botao(n_clicks, selected_rows, data):
    """
    Abre o modal de edição de responsável quando o botão Editar é clicado.
    """
    if n_clicks is None or not selected_rows:
        raise PreventUpdate

    row_idx = selected_rows[0]
    responsavel = data[row_idx]
    return True, responsavel['nome'], {'id': responsavel['id']}


@callback(
    [
        Output(
            'feedback-editar-responsavel', 'children', allow_duplicate=True
        ),
        Output('modal-editar-responsavel', 'is_open', allow_duplicate=True),
    ],
    [Input('btn-salvar-editar-responsavel', 'n_clicks')],
    [
        State('input-editar-responsavel', 'value'),
        State('item-id-responsavel', 'data'),
    ],
    prevent_initial_call=True,
)
def salvar_edicao_responsavel(n_clicks, novo_nome, item_id):
    """
    Salva a edição de um responsável.
    """
    if n_clicks is None:
        raise PreventUpdate

    if not item_id or 'id' not in item_id:
        return (
            dbc.Alert('ID do responsável não encontrado.', color='danger'),
            no_update,
        )

    if not novo_nome or not novo_nome.strip():
        return (
            dbc.Alert(
                'Por favor, informe o nome do responsável.', color='danger'
            ),
            no_update,
        )

    resultado = controller_editar_responsavel(item_id['id'], novo_nome)

    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success'), False
    else:
        return dbc.Alert(resultado['message'], color='danger'), no_update


@callback(
    Output('modal-editar-responsavel', 'is_open', allow_duplicate=True),
    [Input('btn-cancelar-editar-responsavel', 'n_clicks')],
    prevent_initial_call=True,
)
def cancelar_edicao(n_clicks):
    """
    Fecha o modal de edição quando o botão Cancelar é clicado.
    """
    if n_clicks is None:
        raise PreventUpdate
    return False


@callback(
    Output('feedback-responsavel', 'children', allow_duplicate=True),
    [Input('btn-excluir-responsavel', 'n_clicks')],
    [
        State('tabela-responsaveis', 'selected_rows'),
        State('tabela-responsaveis', 'data'),
    ],
    prevent_initial_call=True,
)
def excluir_responsavel(n_clicks, selected_rows, data):
    """
    Exclui um responsável selecionado.
    """
    if n_clicks is None:
        raise PreventUpdate

    if not selected_rows:
        return dbc.Alert(
            'Por favor, selecione um responsável para excluir.',
            color='warning',
        )

    row_idx = selected_rows[0]
    responsavel = data[row_idx]
    responsavel_id = responsavel['id']

    resultado = controller_excluir_responsavel(responsavel_id)

    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success')
    else:
        return dbc.Alert(resultado['message'], color='danger')
