"""
Script para atualizar a estrutura do banco de dados.
Este script adiciona novas colunas às tabelas existentes.
"""
from models.database import atualizar_estrutura_banco

if __name__ == "__main__":
    print("Iniciando atualização da estrutura do banco de dados...")
    atualizar_estrutura_banco()
    print("Atualização concluída.")
