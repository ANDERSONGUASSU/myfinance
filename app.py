"""
Este módulo é o ponto de entrada do aplicativo.
Ele carrega o ambiente, configura o banco de dados e inicia o servidor Dash.
"""

from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from dotenv import load_dotenv
from dash import html, Input, Output
from controllers import home_controller
from controllers import (
    cadastro_controller,
)  # Importação necessária para registrar os callbacks de cadastro
import callbacks  # Importando os callbacks
from models import database
from views.transacoes_view import transacoes_layout
from views.cadastros_view import cadastros_layout

load_dotenv()
db_path = database.DB_PATH

if not Path(db_path).exists():
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database.criar_tabelas()


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = html.Div(
    [html.H1('Bem-vindo ao Projeto Dash MVC'), home_controller.layout()]
)


@app.callback(
    Output('tabs-content', 'children', allow_duplicate=True),
    [Input('tabs', 'value')],
    prevent_initial_call=True,
)
def render_content(tab):
    """Renderiza o conteúdo da tab selecionada."""
    if tab == 'transacoes':
        return transacoes_layout()
    elif tab == 'cadastros':
        return cadastros_layout()


if __name__ == '__main__':
    app.run(debug=True)
