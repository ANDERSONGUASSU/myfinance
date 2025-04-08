"""
Este módulo define os callbacks para a aba de visualização de transações.
"""

from dash import callback, Output, Input, State, html, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc
from controllers.visualizar_transacoes import listar_transacoes, obter_transacao, editar_transacao, excluir_transacao
from controllers.cadastro.categorias import listar_categorias
from controllers.cadastro.responsaveis import listar_responsaveis
from controllers.cadastro.contas import listar_contas
from controllers.cadastro.pagamentos import listar_pagamentos
import locale
from datetime import datetime

# Configurar formatação de moeda para R$
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# Callback para habilitar/desabilitar filtros de acordo com a seleção de período
@callback(
    [Output('filtro-mes', 'disabled'),
     Output('filtro-ano', 'disabled')],
    [Input('filtro-periodo', 'value')],
    prevent_initial_call=True
)
def atualizar_filtros_periodo(periodo):
    """
    Atualiza o estado de habilitação dos filtros de mês e ano de acordo com o período selecionado.
    """
    if periodo == 'mes':
        return False, False
    elif periodo == 'ano':
        return True, False
    else:  # 'todos'
        return True, True


# Callback para carregar opções para os filtros de conta e categoria
@callback(
    [Output('filtro-conta', 'options'),
     Output('filtro-categoria', 'options')],
    [Input('tabs', 'value')]
)
def carregar_opcoes_filtros(tab):
    """
    Carrega as opções para os dropdowns de filtro.
    """
    if tab != 'visualizar-transacoes':
        raise PreventUpdate

    # Contas
    resultado_contas = listar_contas()
    opcoes_contas = []
    if resultado_contas['success']:
        opcoes_contas = [{'label': f"{conta['nome']} ({conta['tipo']})",
                          'value': conta['id']} for conta in resultado_contas['contas']]

    # Categorias
    resultado_categorias = listar_categorias()
    opcoes_categorias = []
    if resultado_categorias['success']:
        opcoes_categorias = [{'label': cat['nome'], 'value': cat['id']}
                             for cat in resultado_categorias['categorias']]

    return opcoes_contas, opcoes_categorias


# Callback para carregar transações baseadas nos filtros
@callback(
    [Output('tabela-visualizar-transacoes', 'children'),
     Output('badge-total-receitas', 'children'),
     Output('badge-total-despesas', 'children'),
     Output('badge-saldo-periodo', 'children')],
    [Input('tabs', 'value'),
     Input('btn-aplicar-filtros', 'n_clicks')],
    [State('filtro-periodo', 'value'),
     State('filtro-mes', 'value'),
     State('filtro-ano', 'value'),
     State('filtro-conta', 'value'),
     State('filtro-categoria', 'value'),
     State('filtro-tipo', 'value'),
     State('filtro-status', 'value')],
    prevent_initial_call=True
)
def carregar_transacoes(tab, n_clicks, periodo, mes, ano, conta_id, categoria_id, tipo, status):
    """
    Carrega as transações com base nos filtros selecionados.
    """
    if tab != 'visualizar-transacoes':
        raise PreventUpdate

    # Construir filtros
    filtros = {
        'periodo': periodo,
        'mes': mes,
        'ano': ano,
        'conta_id': conta_id,
        'categoria_id': categoria_id,
        'tipo': tipo,
        'status': status
    }

    # Carregar transações
    resultado = listar_transacoes(filtros)

    if not resultado['success']:
        return html.Div(dbc.Alert(f"Erro ao carregar transações: {resultado.get('error')}", color="danger")), "", "", ""

    transacoes = resultado['transacoes']
    total_receitas = resultado['total_receitas']
    total_despesas = resultado['total_despesas']
    saldo = resultado['saldo']

    # Se não houver dados, exibir mensagem
    if not transacoes:
        return html.Div(dbc.Alert("Nenhuma transação encontrada para os filtros selecionados.", color="warning")), \
            "Receitas: R$ 0,00", "Despesas: R$ 0,00", "Saldo: R$ 0,00"

    # Preparar dados para a tabela
    columns = [
        {"name": "ID", "id": "id"},
        {"name": "Data", "id": "data"},
        {"name": "Valor", "id": "valor", "type": "numeric", "format": {"specifier": ",.2f"}},
        {"name": "Tipo", "id": "tipo"},
        {"name": "Descrição", "id": "descricao"},
        {"name": "Conta", "id": "conta"},
        {"name": "Categoria", "id": "categoria"},
        {"name": "Status", "id": "status"}
    ]

    data = []
    for t in transacoes:
        data.append({
            "id": t['id'],
            "data": t['data'],
            "valor": t['valor'],
            "tipo": t['tipo'],
            "descricao": t['descricao'],
            "conta": t['conta'],
            "categoria": t['categoria'],
            "status": t['status']
        })

    # Criar tabela com botões de ação abaixo
    tabela_e_botoes = html.Div([
        dash_table.DataTable(
            id='tabela-transacoes-filtrada',
            columns=columns,
            data=data,
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
                    'if': {'filter_query': '{tipo} = "Receita"'},
                    'backgroundColor': 'rgba(0, 200, 0, 0.1)',
                },
                {
                    'if': {'filter_query': '{tipo} = "Despesa"'},
                    'backgroundColor': 'rgba(200, 0, 0, 0.1)',
                },
                {
                    'if': {'filter_query': '{status} = "Cancelado"'},
                    'textDecoration': 'line-through',
                    'opacity': 0.6
                }
            ],
            page_size=15,
            page_action='native',
            sort_action='native',
            row_selectable='single'
        ),

        # Botões de ação abaixo da tabela
        html.Div([
            dbc.Button("Editar Selecionada",
                       id="btn-editar-transacao-selecionada",
                       color="primary",
                       className="me-2"),
            dbc.Button("Excluir Selecionada",
                       id="btn-excluir-transacao-selecionada",
                       color="danger")
        ], className="mt-3 d-flex")
    ])

    # Formatar totais para exibição nos badges
    total_receitas_fmt = f"Receitas: R$ {total_receitas:,.2f}".replace('.', ',')
    total_despesas_fmt = f"Despesas: R$ {total_despesas:,.2f}".replace('.', ',')
    saldo_fmt = f"Saldo: R$ {saldo:,.2f}".replace('.', ',')

    return tabela_e_botoes, total_receitas_fmt, total_despesas_fmt, saldo_fmt


# Callback para resetar os filtros
@callback(
    [Output('filtro-periodo', 'value'),
     Output('filtro-mes', 'value'),
     Output('filtro-ano', 'value'),
     Output('filtro-conta', 'value'),
     Output('filtro-categoria', 'value'),
     Output('filtro-tipo', 'value'),
     Output('filtro-status', 'value')],
    [Input('btn-limpar-filtros', 'n_clicks')],
    prevent_initial_call=True
)
def limpar_filtros(n_clicks):
    """
    Reseta todos os filtros para seus valores padrão.
    """
    if n_clicks is None:
        raise PreventUpdate

    # Obter o mês e ano atuais
    now = datetime.now()

    return 'mes', now.month, now.year, None, None, 'todas', 'todos'


# Callback para abrir o modal de edição quando o botão "Editar Selecionada" é clicado
@callback(
    [Output('modal-editar-transacao', 'is_open'),
     Output('editar-transacao-id', 'data')],
    [Input('btn-editar-transacao-selecionada', 'n_clicks')],
    [State('tabela-transacoes-filtrada', 'selected_rows'),
     State('tabela-transacoes-filtrada', 'data')],
    prevent_initial_call=True
)
def abrir_modal_editar_transacao(n_clicks, selected_rows, data):
    """
    Abre o modal de edição quando o botão "Editar Selecionada" é clicado.
    """
    if n_clicks is None:
        raise PreventUpdate

    # Se não houver linha selecionada, mostrar mensagem de aviso
    if not selected_rows:
        # Mostrar alerta sem abrir o modal
        return False, no_update

    row_idx = selected_rows[0]
    transacao_id = data[row_idx]['id']

    return True, transacao_id


# Callback para mostrar mensagem de erro quando não há seleção
@callback(
    Output('tabela-visualizar-transacoes', 'children', allow_duplicate=True),
    [Input('btn-editar-transacao-selecionada', 'n_clicks'),
     Input('btn-excluir-transacao-selecionada', 'n_clicks')],
    [State('tabela-transacoes-filtrada', 'selected_rows'),
     State('tabela-visualizar-transacoes', 'children')],
    prevent_initial_call=True
)
def mostrar_erro_selecao(n_editar, n_excluir, selected_rows, current_table):
    """
    Mostra mensagem de erro se nenhuma linha estiver selecionada ao tentar editar/excluir.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Se não houver linha selecionada, mostrar mensagem de aviso
    if not selected_rows:
        if trigger_id == 'btn-editar-transacao-selecionada':
            mensagem = "Por favor, selecione uma transação para editar."
        else:
            mensagem = "Por favor, selecione uma transação para excluir."

        return html.Div([
            html.Div(dbc.Alert(mensagem, color="warning"), className="mb-2"),
            current_table
        ])

    # Se há uma transação selecionada, não modifica a tabela
    raise PreventUpdate


# Callback para abrir o modal de exclusão quando o botão "Excluir Selecionada" é clicado
@callback(
    [Output('modal-confirmar-exclusao', 'is_open'),
     Output('transacao-excluir-id', 'data')],
    [Input('btn-excluir-transacao-selecionada', 'n_clicks')],
    [State('tabela-transacoes-filtrada', 'selected_rows'),
     State('tabela-transacoes-filtrada', 'data')],
    prevent_initial_call=True
)
def abrir_modal_excluir_transacao(n_clicks, selected_rows, data):
    """
    Abre o modal de confirmação de exclusão quando o botão "Excluir Selecionada" é clicado.
    """
    if n_clicks is None:
        raise PreventUpdate

    # Se não houver linha selecionada, não abrir o modal
    if not selected_rows:
        return False, no_update

    row_idx = selected_rows[0]
    transacao_id = data[row_idx]['id']

    return True, transacao_id


# Callback para carregar dados da transação para edição
@callback(
    [Output('editar-transacao-tipo', 'value'),
     Output('editar-transacao-valor', 'value'),
     Output('editar-transacao-data', 'date'),
     Output('editar-transacao-descricao', 'value'),
     Output('editar-transacao-conta', 'value'),
     Output('editar-transacao-categoria', 'value'),
     Output('editar-transacao-responsavel', 'value'),
     Output('editar-transacao-pagamento', 'value'),
     Output('editar-transacao-status', 'value'),
     Output('editar-transacao-conta', 'options'),
     Output('editar-transacao-categoria', 'options'),
     Output('editar-transacao-responsavel', 'options'),
     Output('editar-transacao-pagamento', 'options')],
    [Input('editar-transacao-id', 'data')],
    prevent_initial_call=True
)
def carregar_dados_edicao(transacao_id):
    """
    Carrega os dados da transação para o formulário de edição.
    """
    if not transacao_id:
        raise PreventUpdate

    # Obter dados da transação
    resultado = obter_transacao(transacao_id)

    if not resultado['success']:
        raise PreventUpdate

    transacao = resultado['transacao']

    # Carregar opções para os dropdowns
    contas = listar_contas()
    opcoes_contas = [{'label': f"{conta['nome']} ({conta['tipo']})",
                      'value': conta['id']} for conta in contas['contas']] if contas['success'] else []

    categorias = listar_categorias()
    opcoes_categorias = [{'label': cat['nome'], 'value': cat['id']}
                         for cat in categorias['categorias']] if categorias['success'] else []

    responsaveis = listar_responsaveis()
    opcoes_responsaveis = [{'label': resp['nome'], 'value': resp['id']}
                           for resp in responsaveis['responsaveis']] if responsaveis['success'] else []

    pagamentos = listar_pagamentos()
    opcoes_pagamentos = [{'label': pag['tipo'], 'value': pag['id']}
                         for pag in pagamentos['pagamentos']] if pagamentos['success'] else []

    return (
        transacao['tipo'],
        transacao['valor'],
        transacao['data'],
        transacao['descricao'],
        transacao['conta_id'],
        transacao['categoria_id'],
        transacao['responsavel_id'],
        transacao['pagamento_id'],
        transacao['status'],
        opcoes_contas,
        opcoes_categorias,
        opcoes_responsaveis,
        opcoes_pagamentos
    )


# Callback para salvar a edição da transação
@callback(
    [Output('editar-transacao-feedback', 'children'),
     Output('btn-aplicar-filtros', 'n_clicks')],
    [Input('btn-salvar-edicao', 'n_clicks')],
    [State('editar-transacao-id', 'data'),
     State('editar-transacao-tipo', 'value'),
     State('editar-transacao-valor', 'value'),
     State('editar-transacao-data', 'date'),
     State('editar-transacao-descricao', 'value'),
     State('editar-transacao-conta', 'value'),
     State('editar-transacao-categoria', 'value'),
     State('editar-transacao-responsavel', 'value'),
     State('editar-transacao-pagamento', 'value'),
     State('editar-transacao-status', 'value'),
     State('btn-aplicar-filtros', 'n_clicks')],
    prevent_initial_call=True
)
def salvar_edicao_transacao(n_clicks, transacao_id, tipo, valor, data, descricao,
                            conta_id, categoria_id, responsavel_id, pagamento_id,
                            status, aplicar_filtros_clicks):
    """
    Salva as alterações na transação.
    """
    if n_clicks is None or not transacao_id:
        raise PreventUpdate

    # Verificar dados obrigatórios
    if not valor or valor <= 0:
        return dbc.Alert("Por favor, informe um valor válido.", color="danger"), no_update

    if not data:
        return dbc.Alert("Por favor, informe uma data.", color="danger"), no_update

    if not tipo:
        return dbc.Alert("Por favor, selecione o tipo da transação.", color="danger"), no_update

    # Preparar dados para atualização
    dados = {
        'tipo': tipo,
        'valor': valor,
        'data': data,
        'descricao': descricao,
        'conta_id': conta_id,
        'categoria_id': categoria_id,
        'responsavel_id': responsavel_id,
        'pagamento_id': pagamento_id,
        'status': status
    }

    # Atualizar a transação
    resultado = editar_transacao(transacao_id, dados)

    if not resultado['success']:
        return dbc.Alert(f"Erro ao atualizar a transação: {resultado.get('error')}", color="danger"), no_update

    # Forçar atualização da tabela incrementando o contador de cliques do botão aplicar filtros
    return dbc.Alert("Transação atualizada com sucesso!", color="success"), aplicar_filtros_clicks + 1


# Callback para fechar o modal de edição
@callback(
    Output('modal-editar-transacao', 'is_open', allow_duplicate=True),
    [Input('btn-cancelar-edicao', 'n_clicks'),
     Input('btn-salvar-edicao', 'n_clicks')],
    prevent_initial_call=True
)
def fechar_modal_edicao(cancelar_clicks, salvar_clicks):
    """
    Fecha o modal de edição quando o usuário clica em cancelar ou salvar.
    """
    if cancelar_clicks is None and salvar_clicks is None:
        raise PreventUpdate

    return False


# Callback para excluir a transação
@callback(
    Output('btn-aplicar-filtros', 'n_clicks', allow_duplicate=True),
    [Input('btn-confirmar-exclusao', 'n_clicks')],
    [State('transacao-excluir-id', 'data'),
     State('btn-aplicar-filtros', 'n_clicks')],
    prevent_initial_call=True
)
def confirmar_exclusao_transacao(n_clicks, transacao_id, aplicar_filtros_clicks):
    """
    Exclui a transação quando o usuário confirma a exclusão.
    """
    if n_clicks is None or not transacao_id:
        raise PreventUpdate

    # Excluir a transação
    excluir_transacao(transacao_id)

    # Forçar atualização da tabela incrementando o contador de cliques do botão aplicar filtros
    return aplicar_filtros_clicks + 1


# Callback para mostrar mensagem de feedback após exclusão
@callback(
    Output('tabela-visualizar-transacoes', 'children', allow_duplicate=True),
    [Input('btn-confirmar-exclusao', 'n_clicks')],
    [State('transacao-excluir-id', 'data'),
     State('tabela-visualizar-transacoes', 'children')],
    prevent_initial_call=True
)
def mostrar_feedback_exclusao(n_clicks, transacao_id, current_table):
    """
    Mostra uma mensagem de feedback após a exclusão de uma transação.
    """
    if n_clicks is None or not transacao_id:
        raise PreventUpdate

    # Mostrar mensagem de sucesso
    return html.Div([
        html.Div(dbc.Alert("Transação excluída com sucesso!", color="success"), className="mb-2"),
        current_table
    ])


# Callback para fechar o modal de confirmação de exclusão
@callback(
    Output('modal-confirmar-exclusao', 'is_open', allow_duplicate=True),
    [Input('btn-cancelar-exclusao', 'n_clicks'),
     Input('btn-confirmar-exclusao', 'n_clicks')],
    prevent_initial_call=True
)
def fechar_modal_exclusao(cancelar_clicks, confirmar_clicks):
    """
    Fecha o modal de confirmação de exclusão quando o usuário clica em cancelar ou confirmar.
    """
    if cancelar_clicks is None and confirmar_clicks is None:
        raise PreventUpdate

    return False
