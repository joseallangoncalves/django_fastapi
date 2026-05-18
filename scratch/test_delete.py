import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
from core import api_client

# Try logging in
print("Logging in user...")
login_res = api_client.login_usuario("jose@gmail.com", "senha123")
if not login_res.get("success"):
    print("Login failed:", login_res)
    sys.exit(1)

token = login_res["data"]["access_token"]
print("Login successful! Token acquired.")

# Get contracts list to find a contract to delete
contracts_res = api_client.obter_contratos(token)
if not contracts_res.get("success"):
    print("Failed to fetch contracts:", contracts_res)
    sys.exit(1)

contracts = contracts_res["data"]
print(f"Found {len(contracts)} contracts.")
if not contracts:
    print("No contracts found to test deletion.")
    sys.exit(0)

# Try deleting the first contract
target_id = contracts[0]["id"]
print(f"Attempting to delete contract with ID: {target_id}")
delete_res = api_client.excluir_contrato(target_id, token)
print("Delete result:", delete_res)
