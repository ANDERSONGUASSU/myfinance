"""
Este módulo define os callbacks para as funcionalidades de transações.
"""

from dash import callback, Output, Input, State, html, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from models.database import conectar
from controllers.cadastro.categorias import listar_categorias
from controllers.cadastro.responsaveis import listar_responsaveis
from controllers.cadastro.contas import listar_contas
from controllers.cadastro.pagamentos import listar_pagamentos


def eh_feriado(data):
    """
    Verifica se a data é um feriado nacional brasileiro.
    Implementa os feriados nacionais fixos mais comuns.

    :param data: Objeto datetime
    :return: True se for feriado, False caso contrário
    """
    # Feriados nacionais fixos
    feriados_fixos = [
        (1, 1),   # Ano Novo (1º de janeiro)
        (4, 21),  # Tiradentes (21 de abril)
        (5, 1),   # Dia do Trabalho (1º de maio)
        (9, 7),   # Independência (7 de setembro)
        (10, 12),  # Nossa Senhora Aparecida (12 de outubro)
        (11, 2),  # Finados (2 de novembro)
        (11, 15),  # Proclamação da República (15 de novembro)
        (12, 25),  # Natal (25 de dezembro)
    ]

    # Verifica se a data corresponde a algum feriado fixo
    if (data.month, data.day) in feriados_fixos:
        return True

    return False


def proximo_dia_util(data):
    """
    Retorna o próximo dia útil a partir da data fornecida.
    Considera finais de semana e feriados nacionais fixos.

    :param data: Objeto datetime
    :return: Objeto datetime representando o próximo dia útil
    """
    # Se a data já for um dia útil (não é fim de semana nem feriado), retorna a própria data
    if data.weekday() < 5 and not eh_feriado(data):
        return data

    # Adiciona um dia e verifica novamente
    proximo_dia = data + timedelta(days=1)
    return proximo_dia_util(proximo_dia)  # Chamada recursiva até encontrar um dia útil


def calcular_data_vencimento(data_compra_str: str, dia_fechamento: int, dia_vencimento: int) -> str:
    """
    Calcula a data de vencimento da fatura do cartão com base na data da compra,
    no dia de fechamento e no dia de vencimento.

    Se a data de vencimento calculada não for um dia útil (fim de semana ou feriado),
    a data é ajustada para o próximo dia útil.

    :param data_compra_str: Data da compra no formato 'YYYY-MM-DD'
    :param dia_fechamento: Dia do mês em que a fatura fecha (1-31)
    :param dia_vencimento: Dia do mês em que a fatura vence (1-31)
    :return: Data de vencimento no formato 'YYYY-MM-DD'
    """
    data_compra = datetime.strptime(data_compra_str, '%Y-%m-%d')

    if data_compra.day > dia_fechamento:
        # Compra entra na fatura do mês seguinte
        data_fechamento = data_compra.replace(day=1) + relativedelta(months=1, day=dia_fechamento)
        data_vencimento = data_fechamento + relativedelta(day=dia_vencimento)
        # Se o dia de vencimento é menor que o dia de fechamento, avança mais um mês
        if dia_vencimento < dia_fechamento:
            data_vencimento = data_vencimento + relativedelta(months=1)
    else:
        # Compra entra na fatura do mês atual
        data_fechamento = data_compra.replace(day=1) + relativedelta(day=dia_fechamento)
        data_vencimento = data_fechamento + relativedelta(day=dia_vencimento)
        # Se o dia de vencimento é menor que o dia de fechamento, avança mais um mês
        if dia_vencimento < dia_fechamento:
            data_vencimento = data_vencimento + relativedelta(months=1)

    # Ajustar para o próximo dia útil, se necessário
    data_vencimento = proximo_dia_util(data_vencimento)

    return data_vencimento.strftime('%Y-%m-%d')


@callback(
    [
        Output('transacao-conta', 'options'),
        Output('transacao-categoria', 'options'),
        Output('transacao-responsavel', 'options'),
        Output('transacao-pagamento', 'options')
    ],
    [Input('tabs', 'value')]
)
def carregar_opcoes_formulario(tab):
    """
    Carrega as opções para os dropdowns do formulário de transações.
    """
    if tab != 'transacoes':
        raise PreventUpdate

    # Contas
    resultado_contas = listar_contas()
    opcoes_contas = []
    if resultado_contas['success']:
        # Formato correto para Dash Dropdown: apenas label e value
        opcoes_contas = [{'label': f"{conta['nome']} ({conta['tipo']})",
                          'value': conta['id']} for conta in resultado_contas['contas']]

    # Categorias
    resultado_categorias = listar_categorias()
    opcoes_categorias = []
    if resultado_categorias['success']:
        opcoes_categorias = [{'label': cat['nome'], 'value': cat['id']} for cat in resultado_categorias['categorias']]

    # Responsáveis
    resultado_responsaveis = listar_responsaveis()
    opcoes_responsaveis = []
    if resultado_responsaveis['success']:
        opcoes_responsaveis = [{'label': resp['nome'], 'value': resp['id']} for resp in resultado_responsaveis['responsaveis']]

    # Formas de Pagamento
    resultado_pagamentos = listar_pagamentos()
    opcoes_pagamentos = []
    if resultado_pagamentos['success']:
        opcoes_pagamentos = [{'label': pag['tipo'], 'value': pag['id']} for pag in resultado_pagamentos['pagamentos']]

    return opcoes_contas, opcoes_categorias, opcoes_responsaveis, opcoes_pagamentos


# Callback para obter o tipo da conta selecionada
@callback(
    Output('transacao-conta-tipo', 'data'),
    [Input('transacao-conta', 'value')],
    prevent_initial_call=True
)
def obter_tipo_conta(conta_id):
    """
    Obtém o tipo da conta selecionada para uso em outros callbacks.
    """
    if not conta_id:
        return None

    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT tipo FROM contas WHERE id = ?", (conta_id,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        return None
    except sqlite3.Error:
        return None
    finally:
        conn.close()


# Callback para mostrar opções de parcelamento quando cartão de crédito é selecionado
@callback(
    Output('div-parcelamento', 'style'),
    [Input('transacao-conta-tipo', 'data')],
    prevent_initial_call=True
)
def mostrar_parcelamento(tipo_conta):
    """
    Mostra as opções de parcelamento quando a conta é do tipo cartão de crédito.
    """
    if not tipo_conta:
        return {"display": "none"}

    # Se for cartão de crédito, mostrar opções de parcelamento
    if tipo_conta == 'cartao':
        return {"display": "block"}

    return {"display": "none"}


# Callback para habilitar/desabilitar campo de parcelas
@callback(
    Output('transacao-parcelas', 'disabled'),
    [Input('transacao-parcelamento-opcao', 'value')],
    prevent_initial_call=True
)
def habilitar_campo_parcelas(opcao_parcelamento):
    """
    Habilita o campo de número de parcelas quando a opção de parcelamento é selecionada.
    """
    if opcao_parcelamento == 'parcelado':
        return False
    return True


# Callback para mostrar opções de recorrência
@callback(
    Output('div-recorrencia', 'style'),
    [Input('transacao-recorrente-opcao', 'value')],
    prevent_initial_call=True
)
def mostrar_recorrencia(opcao_recorrencia):
    """
    Mostra as opções de recorrência quando a opção de transação recorrente é selecionada.
    """
    if opcao_recorrencia == 'sim':
        return {"display": "block"}
    return {"display": "none"}


# Callback para atualizar o texto de ocorrências conforme a frequência
@callback(
    Output('texto-ocorrencias', 'children'),
    [Input('transacao-frequencia', 'value')],
    prevent_initial_call=True
)
def atualizar_texto_ocorrencias(frequencia):
    """
    Atualiza o texto que acompanha o campo de ocorrências conforme a frequência selecionada.
    """
    if not frequencia:
        return "meses"

    textos = {
        "semanal": "semanas",
        "mensal": "meses",
        "trimestral": "trimestres",
        "semestral": "semestres",
        "anual": "anos"
    }

    return textos.get(frequencia, "meses")


@callback(
    Output('lista-transacoes', 'children'),
    [
        Input('tabs', 'value'),
        Input('btn-atualizar-transacoes', 'n_clicks'),
        Input('btn-salvar-transacao', 'n_clicks')
    ]
)
def carregar_transacoes_recentes(tab, n_atualizar, n_salvar):
    """
    Carrega as transações recentes.
    """
    if tab != 'transacoes':
        raise PreventUpdate

    try:
        conn = conectar()
        cursor = conn.cursor()

        # Buscar transações com informações das tabelas relacionadas
        query = """
        SELECT
            t.id,
            t.data,
            t.data_vencimento,
            t.valor,
            t.tipo,
            t.descricao,
            c.nome as conta,
            c.tipo as tipo_conta,
            cat.nome as categoria,
            r.nome as responsavel,
            p.tipo as forma_pagamento,
            t.status,
            CASE WHEN par.id IS NOT NULL THEN 'Sim' ELSE 'Não' END as parcelada,
            CASE WHEN rec.id IS NOT NULL THEN rec.frequencia ELSE 'Não' END as recorrente
        FROM transacoes t
        LEFT JOIN contas c ON t.conta_id = c.id
        LEFT JOIN categorias cat ON t.categoria_id = cat.id
        LEFT JOIN responsaveis r ON t.responsavel_id = r.id
        LEFT JOIN pagamentos p ON t.pagamento_id = p.id
        LEFT JOIN parcelamentos par ON t.parcelamento_id = par.id
        LEFT JOIN recorrencias rec ON rec.transacao_id = t.id
        ORDER BY t.data DESC
        LIMIT 20
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        colunas = [
            {"name": "ID", "id": "id"},
            {"name": "Data", "id": "data"},
            {"name": "Valor", "id": "valor", "type": "numeric", "format": {"specifier": ",.2f"}},
            {"name": "Tipo", "id": "tipo"},
            {"name": "Descrição", "id": "descricao"},
            {"name": "Conta", "id": "conta"},
            {"name": "Categoria", "id": "categoria"},
            {"name": "Responsável", "id": "responsavel"},
            {"name": "Pagamento", "id": "forma_pagamento"},
            {"name": "Status", "id": "status"},
            {"name": "Parcelada", "id": "parcelada"},
            {"name": "Recorrência", "id": "recorrente"}
        ]

        dados = []
        tooltip_data = []

        for row in rows:
            # Determinar qual data exibir - para cartões de crédito, mostrar data de vencimento se disponível
            data_exibir = row[1]  # data padrão
            if row[7] == 'cartao' and row[2]:  # tipo_conta == 'cartao' e data_vencimento existe
                data_exibir = row[2]  # exibir data_vencimento

            # Preparar dados para tooltip
            tooltip_row = {}
            if row[7] == 'cartao' and row[2]:
                tooltip_row['data'] = {'value': f"Data da transação: {row[1]}\nData de vencimento: {row[2] or 'N/A'}"}
            tooltip_data.append(tooltip_row)

            dados.append({
                "id": row[0],
                "data": data_exibir,
                "valor": row[3],
                "tipo": row[4].capitalize() if row[4] else "",
                "descricao": row[5],
                "conta": row[6] or "",
                "categoria": row[8] or "",
                "responsavel": row[9] or "",
                "forma_pagamento": row[10] or "",
                "status": row[11].capitalize() if row[11] else "",
                "parcelada": row[12] or "Não",
                "recorrente": row[13].capitalize() if row[13] else "Não"
            })

        # Se não houver dados, exibir mensagem
        if not dados:
            return html.Div(dbc.Alert("Nenhuma transação encontrada", color="warning"))

        return dash_table.DataTable(
            id='tabela-transacoes',
            columns=colunas,
            data=dados,
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
            ],
            page_size=10,
            page_action='native',
            sort_action='native',
            tooltip_data=tooltip_data,
            tooltip_duration=None,
        )

    except sqlite3.Error as e:
        return html.Div(dbc.Alert(f"Erro ao carregar transações: {e}", color="danger"))
    finally:
        conn.close()


@callback(
    [Output('transacao-feedback', 'children'),
     Output('transacao-descricao', 'value'),
     Output('transacao-valor', 'value')],
    [Input('btn-salvar-transacao', 'n_clicks')],
    [State('transacao-valor', 'value'),
     State('transacao-data', 'date'),
     State('transacao-descricao', 'value'),
     State('transacao-conta', 'value'),
     State('transacao-categoria', 'value'),
     State('transacao-responsavel', 'value'),
     State('transacao-pagamento', 'value'),
     State('transacao-tipo', 'value'),
     State('transacao-conta-tipo', 'data'),
     State('transacao-parcelamento-opcao', 'value'),
     State('transacao-parcelas', 'value'),
     State('transacao-recorrente-opcao', 'value'),
     State('transacao-frequencia', 'value'),
     State('transacao-ocorrencias', 'value')],
    prevent_initial_call=True
)
def salvar_transacao(n_clicks, valor, data, descricao, conta_id, categoria_id,
                     responsavel_id, pagamento_id, tipo, tipo_conta,
                     opcao_parcelamento, num_parcelas, opcao_recorrente,
                     frequencia, ocorrencias):
    """
    Salva uma nova transação, incluindo parcelamento e recorrência se aplicável.
    """
    if n_clicks is None:
        raise PreventUpdate

    # Validação básica
    if not valor or valor <= 0:
        return dbc.Alert("Por favor, informe um valor válido.", color="danger"), no_update, no_update

    if not data:
        return dbc.Alert("Por favor, informe uma data.", color="danger"), no_update, no_update

    if not tipo:
        return dbc.Alert("Por favor, selecione o tipo da transação (receita ou despesa).", color="danger"), no_update, no_update

    try:
        conn = conectar()
        cursor = conn.cursor()

        # Formatar valor para despesa (negativo)
        valor_original = valor
        if tipo == 'despesa' and valor > 0:
            valor = -valor

        # Verificar informações da conta (para cálculo de data de vencimento)
        data_vencimento = None
        if conta_id and tipo_conta == 'cartao':
            # Consultar dia de fechamento e vencimento do cartão
            cursor.execute("""
                SELECT dia_fechamento, dia_vencimento
                FROM contas
                WHERE id = ? AND tipo = 'cartao'
            """, (conta_id,))
            info_cartao = cursor.fetchone()

            if info_cartao and info_cartao[0] and info_cartao[1]:
                dia_fechamento = info_cartao[0]
                dia_vencimento = info_cartao[1]

                # Usar a função auxiliar para calcular a data de vencimento
                data_vencimento = calcular_data_vencimento(data, dia_fechamento, dia_vencimento)

        # Se for parcelamento
        parcelamento_id = None
        if tipo_conta == 'cartao' and opcao_parcelamento == 'parcelado' and num_parcelas and num_parcelas >= 2:
            # Inserir no parcelamento
            cursor.execute(
                """
                INSERT INTO parcelamentos 
                (descricao, valor_total, parcelas, data_compra, data_vencimento, conta_id, categoria_id, responsavel_id, pagamento_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (descricao, valor_original, num_parcelas, data, data_vencimento, conta_id, categoria_id, responsavel_id, pagamento_id)
            )
            parcelamento_id = cursor.lastrowid

            # Calcular valor da parcela
            valor_parcela = valor_original / num_parcelas
            if tipo == 'despesa':
                valor_parcela = -valor_parcela

            # Criar transações para cada parcela
            data_obj = datetime.strptime(data, '%Y-%m-%d')

            for i in range(num_parcelas):
                # Calcular data da parcela
                data_parcela = data_obj + relativedelta(months=i)
                descricao_parcela = f"{descricao} ({i + 1}/{num_parcelas})"

                # Calcular data de vencimento para cada parcela
                parcela_vencimento = None
                if data_vencimento:
                    # Para parcelas futuras, precisamos calcular o vencimento correto
                    # baseado na data da parcela (que já está incrementada por mês)
                    data_parcela_str = data_parcela.strftime('%Y-%m-%d')

                    # Consultar dia de fechamento e vencimento do cartão novamente
                    cursor.execute("""
                        SELECT dia_fechamento, dia_vencimento 
                        FROM contas 
                        WHERE id = ? AND tipo = 'cartao'
                    """, (conta_id,))
                    info_cartao = cursor.fetchone()

                    if info_cartao and info_cartao[0] and info_cartao[1]:
                        dia_fechamento = info_cartao[0]
                        dia_vencimento = info_cartao[1]

                        # Usar a função auxiliar para calcular a data de vencimento da parcela
                        parcela_vencimento = calcular_data_vencimento(data_parcela_str, dia_fechamento, dia_vencimento)

                # Inserir transação da parcela
                cursor.execute(
                    """
                    INSERT INTO transacoes 
                    (data, valor, tipo, descricao, conta_id, categoria_id, responsavel_id, 
                     pagamento_id, status, parcelamento_id, data_vencimento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (data_parcela.strftime('%Y-%m-%d'), valor_parcela, tipo, descricao_parcela,
                     conta_id, categoria_id, responsavel_id, pagamento_id, 'pendente', parcelamento_id, parcela_vencimento)
                )
        # Se for recorrente
        elif opcao_recorrente == 'sim' and frequencia and ocorrencias and ocorrencias >= 1:
            # Calcular próxima execução baseada na frequência
            data_obj = datetime.strptime(data, '%Y-%m-%d')

            # Funções para calcular incremento de data conforme a frequência
            def calcular_data_semanal(i):
                return data_obj + timedelta(days=7 * i)

            def calcular_data_mensal(i):
                return data_obj + relativedelta(months=i)

            def calcular_data_trimestral(i):
                return data_obj + relativedelta(months=3 * i)

            def calcular_data_semestral(i):
                return data_obj + relativedelta(months=6 * i)

            def calcular_data_anual(i):
                return data_obj + relativedelta(years=i)

            # Selecionar a função de incremento baseada na frequência
            if frequencia == 'semanal':
                data_incremento = calcular_data_semanal
            elif frequencia == 'mensal':
                data_incremento = calcular_data_mensal
            elif frequencia == 'trimestral':
                data_incremento = calcular_data_trimestral
            elif frequencia == 'semestral':
                data_incremento = calcular_data_semestral
            elif frequencia == 'anual':
                data_incremento = calcular_data_anual
            else:
                data_incremento = calcular_data_mensal  # padrão mensal

            # Inserir a primeira transação e registrar recorrência
            cursor.execute(
                """
                INSERT INTO transacoes 
                (data, valor, tipo, descricao, conta_id, categoria_id, responsavel_id, pagamento_id, status, data_vencimento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (data, valor, tipo, descricao, conta_id, categoria_id, responsavel_id, pagamento_id, 'pendente', data_vencimento)
            )

            primeira_transacao_id = cursor.lastrowid

            # Calcular data final com base no número de ocorrências e frequência
            data_fim = data_incremento(ocorrencias - 1)  # -1 porque já criamos a primeira
            data_fim_str = data_fim.strftime('%Y-%m-%d')

            # Registrar a recorrência
            cursor.execute(
                """
                INSERT INTO recorrencias 
                (transacao_id, frequencia, data_inicio, data_fim, proxima_execucao, ocorrencias)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (primeira_transacao_id, frequencia, data, data_fim_str,
                 data_incremento(1).strftime('%Y-%m-%d'), ocorrencias)
            )

            # Criar todas as transações futuras
            for i in range(1, ocorrencias):  # Começamos de 1 porque já criamos a primeira (i=0)
                data_futura = data_incremento(i)

                # Calcular data de vencimento para cada transação recorrente
                recorrencia_vencimento = None
                if data_vencimento and tipo_conta == 'cartao':
                    data_fut_obj = data_futura.strftime('%Y-%m-%d')

                    # Consultar dia de fechamento e vencimento do cartão novamente
                    cursor.execute("""
                        SELECT dia_fechamento, dia_vencimento 
                        FROM contas 
                        WHERE id = ? AND tipo = 'cartao'
                    """, (conta_id,))
                    info_cartao = cursor.fetchone()

                    if info_cartao and info_cartao[0] and info_cartao[1]:
                        dia_fechamento = info_cartao[0]
                        dia_vencimento = info_cartao[1]

                        # Usar a função auxiliar para calcular a data de vencimento da transação recorrente
                        recorrencia_vencimento = calcular_data_vencimento(data_fut_obj, dia_fechamento, dia_vencimento)

                # Descrição para transações recorrentes
                descricao_recorrente = f"{descricao} ({i + 1}/{ocorrencias})"

                # Inserir transação recorrente
                cursor.execute(
                    """
                    INSERT INTO transacoes 
                    (data, valor, tipo, descricao, conta_id, categoria_id, responsavel_id, pagamento_id, status, data_vencimento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (data_futura.strftime('%Y-%m-%d'), valor, tipo, descricao_recorrente,
                     conta_id, categoria_id, responsavel_id, pagamento_id, 'pendente', recorrencia_vencimento)
                )

                # Atualizar saldo da conta - considerando apenas transações não parceladas
                if conta_id:
                    cursor.execute("UPDATE contas SET saldo = saldo + ? WHERE id = ?", (valor, conta_id))
        else:
            # Transação normal (não parcelada e não recorrente)
            cursor.execute(
                """
                INSERT INTO transacoes 
                (data, valor, tipo, descricao, conta_id, categoria_id, responsavel_id, pagamento_id, status, data_vencimento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (data, valor, tipo, descricao, conta_id, categoria_id, responsavel_id, pagamento_id, 'pendente', data_vencimento)
            )

            # Atualizar saldo da conta, se não for parcelado
            # (no caso de parcelamento, só atualizamos o saldo quando a parcela for paga)
            if conta_id:
                cursor.execute("UPDATE contas SET saldo = saldo + ? WHERE id = ?", (valor, conta_id))

        conn.commit()

        mensagem = "Transação cadastrada com sucesso!"
        if tipo_conta == 'cartao' and opcao_parcelamento == 'parcelado' and num_parcelas and num_parcelas >= 2:
            mensagem += f" Parcelamento em {num_parcelas}x criado."
        if opcao_recorrente == 'sim' and ocorrencias:
            prazo = ""
            if frequencia == 'semanal':
                prazo = f"por {ocorrencias} semanas"
            elif frequencia == 'mensal':
                prazo = f"por {ocorrencias} meses"
            elif frequencia == 'trimestral':
                prazo = f"por {ocorrencias} trimestres"
            elif frequencia == 'semestral':
                prazo = f"por {ocorrencias} semestres"
            elif frequencia == 'anual':
                prazo = f"por {ocorrencias} anos"

            mensagem += f" Criadas {ocorrencias} transações com recorrência {frequencia} {prazo}."

        return dbc.Alert(mensagem, color="success"), "", None

    except sqlite3.Error as e:
        return dbc.Alert(f"Erro ao cadastrar transação: {e}", color="danger"), descricao, valor_original

    finally:
        conn.close()
