#!/bin/bash

PROJECT_NAME=${1:-Projeto Dash MVC}

echo "🔧 Inicializando projeto: $PROJECT_NAME..."

# Cria estrutura
mkdir -p controllers models views assets tests

# Cria virtualenv
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Detecta SO e ativa o venv
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    echo "❌ Sistema operacional não suportado automaticamente. Ative o ambiente manualmente."
fi

# Cria requirements.txt
echo "📝 Gerando requirements.txt..."
cat <<EOL > requirements.txt
attrs==25.3.0
beautifulsoup4==4.13.3
blinker==1.9.0
certifi==2025.1.31
cffi==1.17.1
charset-normalizer==3.4.1
click==8.1.8
contourpy==1.3.1
cryptography==44.0.2
cycler==0.12.1
dash==3.0.2
dash-bootstrap-components==2.0.0
dash-testing-stub==0.0.2
dill==0.3.9
Flask==3.0.3
fonttools==4.57.0
greenlet==3.1.1
h11==0.14.0
idna==3.10
importlib_metadata==8.6.1
iniconfig==2.1.0
itsdangerous==2.2.0
Jinja2==3.1.6
kiwisolver==1.4.8
lark-parser==0.12.0
lxml==5.3.1
MarkupSafe==3.0.2
matplotlib==3.10.1
multiprocess==0.70.17
narwhals==1.33.0
nest-asyncio==1.6.0
numpy==2.2.4
outcome==1.3.0.post0
packaging==24.2
pandas==2.2.3
pandas-stubs==2.2.3.250308
percy==2.0.2
pillow==11.1.0
plotly==6.0.1
pluggy==1.5.0
psutil==7.0.0
pycparser==2.22
pyOpenSSL==25.0.0
pyparsing==3.2.3
PySocks==1.7.1
pytest==8.3.5
pytest-dash==2.1.2
python-dateutil==2.9.0.post0
pytz==2025.2
requests==2.32.3
retrying==1.3.4
ruamel.yaml==0.18.10
ruamel.yaml.clib==0.2.12
selenium==4.2.0
setuptools==78.1.0
six==1.17.0
sniffio==1.3.1
sortedcontainers==2.4.0
soupsieve==2.6
SQLAlchemy==2.0.40
trio==0.29.0
trio-websocket==0.12.2
types-pytz==2025.2.0.20250326
typing_extensions==4.13.0
tzdata==2025.2
urllib3==1.26.20
urllib3-secure-extra==0.1.0
waitress==3.0.2
websocket-client==1.8.0
Werkzeug==3.0.6
wsproto==1.2.0
zipp==3.21.0
python-dotenv==1.0.1
EOL

# Instala dependências
echo "📦 Instalando bibliotecas..."
pip install -r requirements.txt

# Cria app.py com dotenv e app.run
echo "🚀 Criando app.py..."
cat <<EOL > app.py
import os
from dotenv import load_dotenv
load_dotenv()

import dash
from dash import html
import dash_bootstrap_components as dbc
from controllers import home_controller

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    html.H1("Bem-vindo ao Projeto Dash MVC"),
    home_controller.layout()
])

if __name__ == '__main__':
    app.run(debug=True)
EOL

# Cria controllers
touch controllers/__init__.py
cat <<EOL > controllers/home_controller.py
from dash import html

def layout():
    return html.Div([
        html.P("Página inicial do controller.")
    ])
EOL

# Models
touch models/__init__.py
cat <<EOL > models/dummy_model.py
def get_dummy_data():
    return {"msg": "dados mockados"}
EOL

# Views
touch views/__init__.py
cat <<EOL > views/home_view.py
# Aqui você pode criar componentes visuais separados
EOL

# Testes
cat <<EOL > tests/test_dummy.py
def test_exemplo():
    assert 2 + 2 == 4
EOL

# .env
cat <<EOL > .env
DEBUG=True
PORT=8050
EOL

# README
cat <<EOL > README.md
# $PROJECT_NAME

Projeto estruturado com Dash e padrão MVC.

## Instruções

Ativar o ambiente:

\`\`\`bash
source venv/bin/activate  # ou venv\\Scripts\\activate no Windows
\`\`\`

Rodar o app:

\`\`\`bash
python app.py
\`\`\`
EOL

# Git
echo "📁 Inicializando Git..."
git init

echo "📄 Criando .gitignore via npx..."
npx gitignore python

echo "✅ Projeto configurado com sucesso!"
echo "➡️ Execute: source venv/bin/activate && python app.py"
