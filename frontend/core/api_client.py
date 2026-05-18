import httpx
from django.conf import settings

# Base API configurations
FASTAPI_BASE_URL = "http://127.0.0.1:8000"
API_TOKEN = "d73fc831e4add93dc7c8ba237db13d4b"  # System communication token

def _get_headers(token: str | None = None) -> dict:
    headers = {
        "X-API-Token": API_TOKEN,
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def registrar_usuario(nome: str, email: str, senha: str) -> dict:
    url = f"{FASTAPI_BASE_URL}/usuarios/"
    payload = {
        "nome": nome,
        "email": email,
        "senha": senha,
        "cargo": "user"
    }
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=_get_headers(), timeout=10.0)
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                detail = response.json().get("detail", "Erro ao criar usuário")
                return {"success": False, "error": detail}
    except Exception as e:
        return {"success": False, "error": f"Erro de rede: {str(e)}"}

def login_usuario(email: str, senha: str) -> dict:
    url = f"{FASTAPI_BASE_URL}/auth/login"
    payload = {
        "email": email,
        "senha": senha
    }
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=_get_headers(), timeout=10.0)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                detail = response.json().get("detail", "E-mail ou senha incorretos")
                return {"success": False, "error": detail}
    except Exception as e:
        return {"success": False, "error": f"Erro de rede: {str(e)}"}

def logout_usuario(token: str) -> dict:
    url = f"{FASTAPI_BASE_URL}/auth/logout"
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=_get_headers(token), timeout=10.0)
            return {"success": response.status_code == 200}
    except Exception:
        return {"success": False}

def executar_storyteller(tema: str, token: str) -> dict:
    url = f"{FASTAPI_BASE_URL}/skills/storyteller"
    payload = {"tema": tema}
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=_get_headers(token), timeout=30.0)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                detail = response.json().get("detail", "Erro ao executar Storyteller")
                return {"success": False, "error": detail}
    except Exception as e:
        return {"success": False, "error": f"Erro de rede/tempo esgotado: {str(e)}"}

def executar_lecture_extractor(transcricao: str, token: str) -> dict:
    url = f"{FASTAPI_BASE_URL}/skills/lecture_extractor"
    payload = {"transcricao": transcricao}
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=_get_headers(token), timeout=60.0)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                detail = response.json().get("detail", "Erro ao extrair conteúdo da aula")
                return {"success": False, "error": detail}
    except Exception as e:
        return {"success": False, "error": f"Erro de rede/tempo esgotado: {str(e)}"}

def obter_historico(token: str) -> dict:
    url = f"{FASTAPI_BASE_URL}/skills/history"
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=_get_headers(token), timeout=10.0)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": "Erro ao carregar histórico"}
    except Exception as e:
        return {"success": False, "error": str(e)}
