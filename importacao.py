import pandas as pd
import json
from datetime import datetime

# Função para formatar data no padrão ISO 8601
def format_date(date):
    if pd.isnull(date):
        return None
    if isinstance(date, pd.Timestamp):
        return date.isoformat()  # Converte para ISO 8601 automaticamente
    return date  # Se já for uma string, retorna como está

# Carregar a planilha
df = pd.read_excel('dados.xlsx')

#Substitui linhas vazias por null
df = df.where(df.notnull(), None)

# Transformar cada linha da planilha em um dicionário conforme o modelo
def excel_to_json(row):
    return {
        "id": None,
        "contato": [
            {
                "id": row['contato1_id'],
                "tipo_contato": row['contato1_tipo'],
                "descricao": row['contato1_descricao'],
                "data_inclusao": format_date(row['contato1_data_inclusao'])# Adicionei essa linha
            },
            {
                "id": row['contato2_id'],
                "tipo_contato": row['contato2_tipo'],
                "descricao": row['contato2_descricao'],
                "data_inclusao": format_date(row['contato2_data_inclusao'])  # Adicionei essa linha
            }
        ],
        "documento": [
            {
                "id": row['doc1_id'],
                "nro_documento": row['doc1_numero'],
                "data_inclusao": format_date(row['doc1_data_inclusao']),
                "tipo_documento": row['doc1_tipo']
            },
        ],
        "data_nascimento": format_date(row['data_nascimento']),  # Adicionei essa linha
        "nome": row['nome'],
        "nome_social": row['nome_social'],
        "data_inclusao": format_date(row['data_inclusao'])
    }

# Aplicar a transformação para todas as linhas da planilha
json_data = df.apply(excel_to_json, axis=1).tolist()

# Salvar o JSON em um arquivo
with open('pessoas.json', 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)

print("Conversão concluída. Dados salvos em 'pessoas.json'")