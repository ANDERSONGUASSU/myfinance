"""
Este módulo define os callbacks para o cadastro, edição e exclusão de tipos de pagamento.
"""

from dash import callback, Output, Input, State, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from controllers.cadastro.pagamentos import (
    listar_pagamentos as controller_listar_pagamentos,
    excluir_pagamento as controller_excluir_pagamento,
    editar_pagamento as controller_editar_pagamento,
)


@callback(
    Output('div-tabela-pagamentos', 'children', allow_duplicate=True),
    [
        Input('btn-atualizar-pagamentos', 'n_clicks'),
        Input('btn-salvar-pagamento', 'n_clicks'),
        Input('btn-salvar-editar-pagamento', 'n_clicks'),
        Input('btn-excluir-pagamento', 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def atualizar_pagamentos(n_atualizar, n_salvar, n_editar, n_excluir):
    """
    Atualiza a tabela de tipos de pagamento.
    """
    resultado = controller_listar_pagamentos()
    if not resultado['success']:
        return html.Div(
            dbc.Alert(
                f"Erro ao carregar tipos de pagamento: {resultado.get('message')}",
                color='danger',
            )
        )

    from dash import dash_table

    pagamentos = resultado['pagamentos']
    for pagamento in pagamentos:
        pagamento['acoes'] = 'Editar | Excluir'

    return dash_table.DataTable(
        id='tabela-pagamentos',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Tipo', 'id': 'tipo'},
            {'name': 'Ações', 'id': 'acoes', 'type': 'text'},
        ],
        data=pagamentos,
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
        Output('modal-editar-pagamento', 'is_open', allow_duplicate=True),
        Output('input-editar-pagamento', 'value', allow_duplicate=True),
        Output('item-id-pagamento', 'data', allow_duplicate=True),
    ],
    [Input('tabela-pagamentos', 'active_cell')],
    [State('tabela-pagamentos', 'data')],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_celula(active_cell, data):
    """
    Abre o modal de edição de tipo de pagamento quando uma célula da tabela é clicada.
    """
    if active_cell is None:
        raise PreventUpdate

    row_idx = active_cell['row']
    col_id = active_cell['column_id']

    if col_id != 'acoes':
        raise PreventUpdate

    pagamento = data[row_idx]
    return True, pagamento['tipo'], {'id': pagamento['id']}


@callback(
    [
        Output('modal-editar-pagamento', 'is_open', allow_duplicate=True),
        Output('input-editar-pagamento', 'value', allow_duplicate=True),
        Output('item-id-pagamento', 'data', allow_duplicate=True),
    ],
    [Input('btn-editar-pagamento', 'n_clicks')],
    [
        State('tabela-pagamentos', 'selected_rows'),
        State('tabela-pagamentos', 'data'),
    ],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_botao(n_clicks, selected_rows, data):
    """
    Abre o modal de edição de tipo de pagamento quando o botão Editar é clicado.
    """
    if n_clicks is None or not selected_rows:
        raise PreventUpdate

    row_idx = selected_rows[0]
    pagamento = data[row_idx]
    return True, pagamento['tipo'], {'id': pagamento['id']}


@callback(
    [
        Output('feedback-editar-pagamento', 'children', allow_duplicate=True),
        Output('modal-editar-pagamento', 'is_open', allow_duplicate=True),
    ],
    [Input('btn-salvar-editar-pagamento', 'n_clicks')],
    [
        State('input-editar-pagamento', 'value'),
        State('item-id-pagamento', 'data'),
    ],
    prevent_initial_call=True,
)
def salvar_edicao_pagamento(n_clicks, novo_tipo, item_id):
    """
    Salva a edição de um tipo de pagamento.
    """
    if n_clicks is None:
        raise PreventUpdate

    if not item_id or 'id' not in item_id:
        return (
            dbc.Alert(
                'ID do tipo de pagamento não encontrado.', color='danger'
            ),
            no_update,
        )

    if not novo_tipo or not novo_tipo.strip():
        return (
            dbc.Alert(
                'Por favor, informe o tipo de pagamento.', color='danger'
            ),
            no_update,
        )

    resultado = controller_editar_pagamento(item_id['id'], novo_tipo)

    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success'), False
    else:
        return dbc.Alert(resultado['message'], color='danger'), no_update


@callback(
    Output('modal-editar-pagamento', 'is_open', allow_duplicate=True),
    [Input('btn-cancelar-editar-pagamento', 'n_clicks')],
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
    Output('feedback-pagamento', 'children', allow_duplicate=True),
    [Input('btn-excluir-pagamento', 'n_clicks')],
    [
        State('tabela-pagamentos', 'selected_rows'),
        State('tabela-pagamentos', 'data'),
    ],
    prevent_initial_call=True,
)
def excluir_pagamento(n_clicks, selected_rows, data):
    """
    Exclui um tipo de pagamento selecionado.
    """
    if n_clicks is None:
        raise PreventUpdate

    if not selected_rows:
        return dbc.Alert(
            'Por favor, selecione um tipo de pagamento para excluir.',
            color='warning',
        )

    row_idx = selected_rows[0]
    pagamento = data[row_idx]
    pagamento_id = pagamento['id']

    resultado = controller_excluir_pagamento(pagamento_id)

    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success')
    else:
        return dbc.Alert(resultado['message'], color='danger')
