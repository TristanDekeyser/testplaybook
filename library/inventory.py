#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import os
import requests
import json
import yaml

# 🔹 Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.133:3000/api"
SEMAPHORE_TOKEN = "owozuup-zne7p-stkhhs3hdfr6efiyk1rh8okh_70bu="
PROJECT_ID = 1

def create_inventory(inventory_data):
    """ Maakt de inventory aan in Semaphore en retourneert de ID """
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/inventory"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "name": "Backup Inventory",
        "project_id": PROJECT_ID,
        "inventory": inventory_data,
        "ssh_key_id": 2,
        "become_key_id": 4,
        "type": "static"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return response.json().get("id")
    return None

def create_template(inventory_id):
    """ Maakt een template aan in Semaphore """
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "project_id": PROJECT_ID,
        "inventory_id": inventory_id,
        "repository_id": 1,
        "environment_id": 1,
        "name": "backup",
        "playbook": "playbook.yml",
        "allow_override_args_in_task": False,
        "limit": "",
        "suppress_success_alerts": True,
        "app": "ansible",
        "git_branch": "main"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

def main():
    module = AnsibleModule(
        argument_spec={
            'mislukte_hosts': {'type': 'list', 'required': True},
        },
        supports_check_mode=True
    )

    try:
        # Verkrijg de mislukte hosts van de invoer
        mislukte_hosts = json.loads(module.params['mislukte_hosts'])

        # Maak een inventory met de mislukte hosts
        inventory_data = {"hosts": mislukte_hosts}
        inventory_id = create_inventory(inventory_data)
        if not inventory_id:
            module.fail_json(msg="Fout bij aanmaken van inventory!")

        # Template aanmaken
        if not create_template(inventory_id):
            module.fail_json(msg="Fout bij aanmaken van template!")

        module.exit_json(changed=True, msg="Semaphore resources succesvol aangemaakt!")

    except Exception as e:
        module.fail_json(msg=f"Fout: {str(e)}")


if __name__ == '__main__':
    main()
