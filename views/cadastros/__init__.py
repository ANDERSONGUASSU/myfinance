"""
Este pacote contém os componentes de interface para as funcionalidades de cadastro.
"""

from views.cadastros.categorias import cadastro_categoria, tabela_categorias
from views.cadastros.contas import cadastro_conta, tabela_contas
from views.cadastros.pagamentos import cadastro_pagamento, tabela_pagamentos
from views.cadastros.responsaveis import (
    cadastro_responsavel,
    tabela_responsaveis,
)
from views.cadastros.modais import (
    modal_editar_categoria,
    modal_editar_conta,
    modal_editar_pagamento,
    modal_editar_responsavel,
)
