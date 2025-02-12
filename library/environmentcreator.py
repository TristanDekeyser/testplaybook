#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import json

# 🔹 Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.133:3000/api"
SEMAPHORE_TOKEN = "owozuup-zne7p-stkhhs3hdfr6efiyk1rh8okh_70bu="
PROJECT_ID = 1  # Pas dit aan naar je project ID

def send_failed_variables(module, failed_variables):
    """Stuurt mislukte variabelen naar Semaphore"""
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/environment"
    headers = {
        "Authorization": f"Bearer {SEMAPHORE_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "id": 1,
        "name": "Mislukte Variabelen",
        "project_id": PROJECT_ID,
        "password": "string",
        "json": json.dumps({"failed_variables": failed_variables}),
        "env": "{}",
        "secrets": []
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        module.exit_json(changed=True, msg="✅ Variable group succesvol aangemaakt in Semaphore!")
    else:
        module.fail_json(msg=f"❌ Error {response.status_code}: {response.text}")

def main():
    module = AnsibleModule(
        argument_spec={
            "mislukte_variabelen": {"type": "list", "required": True},
        },
        supports_check_mode=True
    )

    failed_vars = module.params["mislukte_variabelen"]

    if not failed_vars:
        module.exit_json(changed=False, msg="ℹ️ Geen mislukte variabelen gevonden.")
    else:
        send_failed_variables(module, failed_vars)

if __name__ == '__main__':
    main()
