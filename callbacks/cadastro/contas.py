"""
Este módulo define os callbacks para o cadastro, edição e exclusão de contas.
"""

from dash import callback, Output, Input, State, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from controllers.cadastro.contas import (
    listar_contas as controller_listar_contas,
    excluir_conta as controller_excluir_conta,
    editar_conta as controller_editar_conta,
    obter_conta as controller_obter_conta,
)


@callback(
    Output('div-tabela-contas', 'children', allow_duplicate=True),
    [
        Input('btn-atualizar-contas', 'n_clicks'),
        Input('btn-salvar-conta', 'n_clicks'),
        Input('btn-salvar-editar-conta', 'n_clicks'),
        Input('btn-excluir-conta', 'n_clicks'),
    ],
    prevent_initial_call=True,
)
def atualizar_contas(n_atualizar, n_salvar, n_editar, n_excluir):
    """
    Atualiza a tabela de contas.
    """
    resultado = controller_listar_contas()
    if not resultado['success']:
        return html.Div(
            dbc.Alert(
                f"Erro ao carregar contas: {resultado.get('message')}",
                color='danger',
            )
        )

    from dash import dash_table

    contas = resultado['contas']
    for conta in contas:
        conta['acoes'] = 'Editar | Excluir'

    return dash_table.DataTable(
        id='tabela-contas',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Nome', 'id': 'nome'},
            {'name': 'Tipo', 'id': 'tipo'},
            {
                'name': 'Saldo',
                'id': 'saldo',
                'type': 'numeric',
                'format': {'specifier': ',.2f'},
            },
            {'name': 'Ações', 'id': 'acoes', 'type': 'text'},
        ],
        data=contas,
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
        Output('modal-editar-conta', 'is_open', allow_duplicate=True),
        Output('input-editar-conta', 'value', allow_duplicate=True),
        Output('select-editar-tipo-conta', 'value', allow_duplicate=True),
        Output('input-editar-saldo', 'value', allow_duplicate=True),
        Output('input-editar-dia-fechamento', 'value', allow_duplicate=True),
        Output('input-editar-dia-vencimento', 'value', allow_duplicate=True),
        Output('input-editar-limite-credito', 'value', allow_duplicate=True),
        Output('campos-editar-cartao-credito', 'style', allow_duplicate=True),
        Output('campos-editar-outros-tipos', 'style', allow_duplicate=True),
        Output('item-id-conta', 'data', allow_duplicate=True),
    ],
    [Input('tabela-contas', 'active_cell')],
    [State('tabela-contas', 'data')],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_celula(active_cell, data):
    """
    Abre o modal de edição de conta quando uma célula da tabela é clicada.
    """
    if active_cell is None:
        raise PreventUpdate

    row_idx = active_cell['row']
    col_id = active_cell['column_id']

    if col_id != 'acoes':
        raise PreventUpdate

    conta_id = data[row_idx]['id']
    resultado = controller_obter_conta(conta_id)

    if not resultado['success']:
        # Não é ideal, mas precisamos retornar algo para todos os outputs
        return (
            False,
            '',
            '',
            None,
            None,
            None,
            None,
            {'display': 'none'},
            {'display': 'none'},
            {},
        )

    conta = resultado['conta']
    tipo = conta['tipo']

    # Definir estilos para mostrar campos específicos
    if tipo == 'cartao':
        estilo_cartao = {'display': 'block'}
        estilo_outros = {'display': 'none'}
    else:
        estilo_cartao = {'display': 'none'}
        estilo_outros = {'display': 'block'}

    return (
        True,
        conta['nome'],
        tipo,
        conta['saldo'],
        conta.get('dia_fechamento', None),
        conta.get('dia_vencimento', None),
        conta.get('limite', None),
        estilo_cartao,
        estilo_outros,
        {'id': conta['id']},
    )


@callback(
    [
        Output('modal-editar-conta', 'is_open', allow_duplicate=True),
        Output('input-editar-conta', 'value', allow_duplicate=True),
        Output('select-editar-tipo-conta', 'value', allow_duplicate=True),
        Output('input-editar-saldo', 'value', allow_duplicate=True),
        Output('input-editar-dia-fechamento', 'value', allow_duplicate=True),
        Output('input-editar-dia-vencimento', 'value', allow_duplicate=True),
        Output('input-editar-limite-credito', 'value', allow_duplicate=True),
        Output('campos-editar-cartao-credito', 'style', allow_duplicate=True),
        Output('campos-editar-outros-tipos', 'style', allow_duplicate=True),
        Output('item-id-conta', 'data', allow_duplicate=True),
    ],
    [Input('btn-editar-conta', 'n_clicks')],
    [State('tabela-contas', 'selected_rows'), State('tabela-contas', 'data')],
    prevent_initial_call=True,
)
def abrir_modal_editar_por_botao(n_clicks, selected_rows, data):
    """
    Abre o modal de edição de conta quando o botão Editar é clicado.
    """
    if n_clicks is None or not selected_rows:
        raise PreventUpdate

    row_idx = selected_rows[0]
    conta_id = data[row_idx]['id']
    resultado = controller_obter_conta(conta_id)

    if not resultado['success']:
        # Não é ideal, mas precisamos retornar algo para todos os outputs
        return (
            False,
            '',
            '',
            None,
            None,
            None,
            None,
            {'display': 'none'},
            {'display': 'none'},
            {},
        )

    conta = resultado['conta']
    tipo = conta['tipo']

    # Definir estilos para mostrar campos específicos
    if tipo == 'cartao':
        estilo_cartao = {'display': 'block'}
        estilo_outros = {'display': 'none'}
    else:
        estilo_cartao = {'display': 'none'}
        estilo_outros = {'display': 'block'}

    return (
        True,
        conta['nome'],
        tipo,
        conta['saldo'],
        conta.get('dia_fechamento', None),
        conta.get('dia_vencimento', None),
        conta.get('limite', None),
        estilo_cartao,
        estilo_outros,
        {'id': conta['id']},
    )


@callback(
    [
        Output('feedback-editar-conta', 'children', allow_duplicate=True),
        Output('modal-editar-conta', 'is_open', allow_duplicate=True),
    ],
    [Input('btn-salvar-editar-conta', 'n_clicks')],
    [
        State('input-editar-conta', 'value'),
        State('select-editar-tipo-conta', 'value'),
        State('input-editar-saldo', 'value'),
        State('input-editar-dia-fechamento', 'value'),
        State('input-editar-dia-vencimento', 'value'),
        State('input-editar-limite-credito', 'value'),
        State('item-id-conta', 'data'),
    ],
    prevent_initial_call=True,
)
def salvar_edicao_conta(
    n_clicks,
    nome,
    tipo,
    saldo,
    dia_fechamento,
    dia_vencimento,
    limite,
    item_id,
):
    """
    Salva a edição de uma conta.
    """
    if n_clicks is None:
        raise PreventUpdate

    if not item_id or 'id' not in item_id:
        return (
            dbc.Alert('ID da conta não encontrado.', color='danger'),
            no_update,
        )

    if not nome or not nome.strip():
        return (
            dbc.Alert('Por favor, informe o nome da conta.', color='danger'),
            no_update,
        )

    resultado = controller_editar_conta(
        item_id['id'],
        nome,
        tipo=tipo,
        saldo=saldo,
        dia_fechamento=dia_fechamento,
        dia_vencimento=dia_vencimento,
        limite=limite,
    )

    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success'), False
    else:
        return dbc.Alert(resultado['message'], color='danger'), no_update


@callback(
    [
        Output('campos-editar-cartao-credito', 'style', allow_duplicate=True),
        Output('campos-editar-outros-tipos', 'style', allow_duplicate=True),
    ],
    [Input('select-editar-tipo-conta', 'value')],
    prevent_initial_call=True,
)
def toggle_campos_editar_conta(tipo_conta):
    """
    Callback para mostrar/esconder campos específicos de acordo com o tipo de conta no modal de edição.
    """
    if tipo_conta == 'cartao':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}


@callback(
    Output('modal-editar-conta', 'is_open', allow_duplicate=True),
    [Input('btn-cancelar-editar-conta', 'n_clicks')],
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
    Output('feedback-conta', 'children'),
    [Input('btn-excluir-conta', 'n_clicks')],
    [State('tabela-contas', 'selected_rows'), State('tabela-contas', 'data')],
    prevent_initial_call=True,
)
def excluir_conta(n_clicks, selected_rows, data):
    """
    Exclui uma conta selecionada.
    """
    if n_clicks is None:
        raise PreventUpdate

    if not selected_rows:
        return dbc.Alert(
            'Por favor, selecione uma conta para excluir.', color='warning'
        )

    row_idx = selected_rows[0]
    conta = data[row_idx]
    conta_id = conta['id']

    resultado = controller_excluir_conta(conta_id)

    if resultado['success']:
        return dbc.Alert(resultado['message'], color='success')
    else:
        return dbc.Alert(resultado['message'], color='danger')
