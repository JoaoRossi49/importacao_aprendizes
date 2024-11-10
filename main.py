import jwt
import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# Variáveis de ambiente
BASE_URL = "http://localhost:8000"
TOKEN_URL = f"{BASE_URL}/token/"
REFRESH_TOKEN_URL = f"{BASE_URL}/token/refresh/"
ACCESS_TOKEN = None
REFRESH_TOKEN = None

# Função para obter a data atual com fuso horário
def CurrentDateWithTimezone():
    return datetime.now().isoformat()

def format_date_to_ddmmyyyy(date_str):
    try:
        # Primeiro tenta ler com hora
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
    except ValueError:
        try:
            # Caso falhe, tenta ler sem hora
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return None  # Retorna None se o formato for inválido
    
# Função para validar CPF (você pode implementar a validação de CPF aqui)
def validarCPF(cpf):
    return len(str(cpf)) == 11

# Função para atualizar o token de acesso usando o refresh token
def refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN
    response = requests.post(REFRESH_TOKEN_URL, json={"refresh": REFRESH_TOKEN})
    response.raise_for_status()
    ACCESS_TOKEN = response.json()["access"]

# Função para autenticação inicial e obtenção de tokens
def authenticate(username, password):
    global ACCESS_TOKEN, REFRESH_TOKEN
    response = requests.post(TOKEN_URL, json={"username": username, "password": password})
    response.raise_for_status()
    tokens = response.json()
    ACCESS_TOKEN = tokens["access"]
    REFRESH_TOKEN = tokens["refresh"]

# Função para enviar imagem de perfil
def updatePessoaImage(pessoa_id, foto_perfil_path):
    if foto_perfil_path and ACCESS_TOKEN:
        files = {'foto_perfil': open(foto_perfil_path, 'rb')}
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.post(f"{BASE_URL}/api/pessoa/{pessoa_id}/foto", files=files, headers=headers)
        response.raise_for_status()

# Função para verificar e atualizar o token de acesso antes de cada requisição
def get_headers():
    global ACCESS_TOKEN
    # Atualiza o token se faltar menos de 5 minutos para expirar
    token_data = jwt.decode(ACCESS_TOKEN, options={"verify_signature": False})
    expires_at = datetime.fromtimestamp(token_data["exp"])
    if (expires_at - datetime.now()) < timedelta(minutes=5):
        refresh_access_token()
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Autenticação inicial
authenticate("admin", "123")  # Substitua "usuario" e "senha" pelos valores corretos

# Carregar dados do Excel
data = pd.read_excel("dados.xlsx")

# Iterar sobre cada linha da planilha e preparar o payload
for index, row in data.iterrows():

    if pd.notna(row['enviado']):  # Ignora linhas com "SIM" na coluna "Status de envio"
        continue

    formData = {
        "id": str(row['pessoa_id']),
        "endereco": {
            "id": str(row['endereco_id']),
            "logradouro": str(row['logradouro']),
            "numero": str(row['numero']),
            "data_inclusao": CurrentDateWithTimezone(),
            "complemento": str(row['complemento']),
            "cidade": str(row['cidade']),
            "estado": str(row['estado']),
            "pais": str(row['pais']),
            "cep": str(row['cep']),
        },
        "contato": [
            {"id": 1, "tipo_contato": "CELULAR", "descricao": row['celular'], "data_inclusao": CurrentDateWithTimezone()},
            {"id": 2, "tipo_contato": "EMAIL", "descricao": row['email'], "data_inclusao": CurrentDateWithTimezone()},
        ],
        "documento": [
            {"id": 1, "nro_documento": row['cpf'], "data_inclusao": CurrentDateWithTimezone(), "tipo_documento": "CPF"},
            {"id": 2, "nro_documento": row['ra'], "data_inclusao": CurrentDateWithTimezone(), "tipo_documento": "RA"},
        ],
        "nome": str(row['nome']),
        "nome_social": str(row['nome_social']),
        #"foto_perfil": str(row['foto_perfil']),
        "data_nascimento": format_date_to_ddmmyyyy(str(row['data_nascimento'])),
        "sexo": str(row['sexo']),
        "data_inclusao": CurrentDateWithTimezone(),
    }

    matriculaFormData = {
        "id": str(row['matricula_id']),
        "escolaridade_nome": str(row['escolaridade_nome']),
        "turma_nome": str(row['turma_nome']),
        "curso_nome": str(row['curso_nome']),
        "empresa_nome": str(row['empresa_nome']),
        "cbo_nome": str(row['cbo_nome']),
        "data_inclusao": CurrentDateWithTimezone(),
        "salario": str(str(row['salario'])),
        "taxa_administrativa": str(row['taxa_administrativa']),
        "data_inicio_contrato": format_date_to_ddmmyyyy(str(row['data_inicio_contrato'])),
        "data_terminio_contrato": format_date_to_ddmmyyyy(str(row['data_terminio_contrato'])),
        "data_inicio_empresa": format_date_to_ddmmyyyy(str(row['data_inicio_empresa'])),
        "quantidade_meses_contrato": str(row['quantidade_meses_contrato']),
        "data_terminio_empresa": format_date_to_ddmmyyyy(str(row['data_terminio_empresa'])),
        "hora_inicio_expediente": str(row['hora_inicio_expediente']),
        "hora_fim_expediente": str(row['hora_fim_expediente']),
        "dias_da_semana_empresa": row['dias_da_semana_empresa'].split(',') if pd.notna(row['dias_da_semana_empresa']) else [],
        "dias_da_semana_curso": row['dias_da_semana_curso'].split(',') if pd.notna(row['dias_da_semana_curso']) else [],
        "atividades_praticas": str(row['atividades_praticas']),
    }

    # Validação do CPF
    if not validarCPF(formData["documento"][0]["nro_documento"]):
        print(f"CPF inválido para o aprendiz na linha {index + 2}")
        continue

    # Fazer requisição de API
    try:
        headers = get_headers()
        # Verificar se é uma atualização (PUT) ou um novo registro (POST)
        if formData["id"] == "10":
            print('Caiu no Put')
            pessoa_id = formData["id"]
            matricula_id = matriculaFormData["id"]

            # Atualizar pessoa
            responsePessoaPut = requests.put(f"{BASE_URL}/pessoa/{pessoa_id}/", json=formData, headers=headers)
            responsePessoaPut.raise_for_status()

            # Atualizar imagem de perfil, se aplicável
            updatePessoaImage(pessoa_id, formData["foto_perfil"])

            # Atualizar matrícula
            responseMatriculaPut = requests.put(f"{BASE_URL}/estudante/matricula/{matricula_id}/", json=matriculaFormData, headers=headers)
            responseMatriculaPut.raise_for_status()

        else:
            print('Caiu no Post', formData)
            # Criar novo registro de pessoa
            responsePessoa = requests.post(f"{BASE_URL}/pessoa/", json=formData, headers=headers)
            responsePessoa.raise_for_status()
            print(responsePessoa.json())
            pessoa_id = responsePessoa.json().get("id")
            matriculaFormData["pessoa"] = pessoa_id

            # Criar matrícula
            responseMatricula = requests.post(f"{BASE_URL}/api/estudante/matricula/", json=matriculaFormData, headers=headers)
            responseMatricula.raise_for_status()

            # Atualizar imagem de perfil, se aplicável
            #updatePessoaImage(pessoa_id, formData["foto_perfil"])

        # Atualiza o status de envio na planilha
        row['enviado'] = 'SIM'

        print(f"Registro para aprendiz '{formData['nome']}' processado com sucesso.")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao processar aprendiz na linha {index + 2}: {e}")
        try:
            print('Deu ruim talvez')
            #print(f"Response de pessoa: {responsePessoa.json()}")
        except:
            pass

        try:
            print('Deu ruim na matricula talvez')
            #print(f"Response de matrícula: {responseMatricula.json()}")
        except:
            pass

# Salvar as alterações de volta na planilha Excel
data.to_excel("dados_atualizado.xlsx", index=False)