#!/usr/bin/python3
from ansible.module_utils.basic import AnsibleModule
import json
import requests
import logging

# 🔹 Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.133:3000/api"
SEMAPHORE_TOKEN = "ybv3vzutqwya30hg2rn_q5xgobvloclj2_u8x8k4kos="
PROJECT_ID = 1

# Configuratie van logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_inventory(inventory_data):
    """ Maakt de inventory aan in Semaphore en retourneert de ID """
    logging.debug(f"Probeer inventory aan te maken met de data: {inventory_data}")
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
    logging.debug(f"Inventory aanmaak response: {response.status_code}, {response.text}")
    
    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        logging.error(f"Fout bij aanmaken van inventory: {response.status_code}, {response.text}")
    return None

def create_environment(variable_data):
    """ Maakt een environment aan in Semaphore en retourneert de ID """
    logging.debug(f"Probeer environment aan te maken met de data: {variable_data}")
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/environment"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "name": "Backup Environment",
        "project_id": PROJECT_ID,
        "password": "string",
        "json": json.dumps(variable_data),
        "env": "{}",
        "secrets": []
    }

    response = requests.post(url, headers=headers, json=payload)
    logging.debug(f"Environment aanmaak response: {response.status_code}, {response.text}")
    
    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        logging.error(f"Fout bij aanmaken van environment: {response.status_code}, {response.text}")
    return None

def create_template(inventory_id, environment_id):
    """ Maakt een template aan in Semaphore """
    logging.debug(f"Probeer template aan te maken met inventory_id: {inventory_id} en environment_id: {environment_id}")
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "project_id": PROJECT_ID,
        "inventory_id": inventory_id,
        "repository_id": 1,
        "environment_id": environment_id,
        "name": "backup",
        "playbook": "playbook.yml",
        "allow_override_args_in_task": False,
        "limit": "",
        "suppress_success_alerts": True,
        "app": "ansible",
        "git_branch": "main"
    }

    response = requests.post(url, headers=headers, json=payload)
    logging.debug(f"Template aanmaak response: {response.status_code}, {response.text}")
    
    if response.status_code in [200, 201]:
        return True
    else:
        logging.error(f"Fout bij aanmaken van template: {response.status_code}, {response.text}")
    return False

def run_semaphore(inventory_vars, environment_vars):
    """ Verwerkt de data en maakt resources aan in Semaphore """
    logging.debug("Start met aanmaken van resources in Semaphore")
    
    # 1. Maak de inventory aan in Semaphore
    inventory_id = create_inventory(inventory_vars)
    if not inventory_id:
        raise Exception("Fout bij aanmaken van inventory!")
    
    # 2. Maak de environment aan in Semaphore
    environment_id = create_environment(environment_vars)
    if not environment_id:
        raise Exception("Fout bij aanmaken van environment!")

    # 3. Maak de template aan in Semaphore
    if not create_template(inventory_id, environment_id):
        raise Exception("Fout bij aanmaken van template!")

    logging.debug("Semaphore resources succesvol aangemaakt!")
    return "Semaphore resources succesvol aangemaakt!"

def main():
    module = AnsibleModule(
        argument_spec={
            'inventory': {'type': 'list', 'required': True},
            'environment': {'type': 'dict', 'required': True}
        }
    )

    inventory_vars = module.params['inventory']
    environment_vars = module.params['environment']

    try:
        result = run_semaphore(inventory_vars, environment_vars)
        module.exit_json(changed=True, msg=result)

    except Exception as e:
        logging.error(f"Fout: {str(e)}")
        module.fail_json(msg=f"Fout: {str(e)}")

if __name__ == '__main__':
    main()
