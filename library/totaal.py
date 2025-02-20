import requests
import yaml
import json
from ansible.module_utils.basic import AnsibleModule

# Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.160:3000/api"
SEMAPHORE_TOKEN = "tuwnyelwoulicyww1e87zznnnaq7w6pkoadjh-z3uz8="
PROJECT_ID = 1

HEADERS = {
    "Authorization": f"Bearer {SEMAPHORE_TOKEN}",
    "Content-Type": "application/json"
}

def get_last_playbook_name(module):
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/tasks"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200 and response.json():
        return response.json()[0].get("tpl_playbook")
    module.fail_json(msg=f"Fout bij ophalen playbook: {response.text}")

def create_inventory(module, hosts):
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/inventory"
    inventory_yaml = yaml.dump({"all": {"children": {"machines": {"hosts": hosts}}}}, default_flow_style=False)

    payload = {
        "name": "Backup Inventory",
        "project_id": PROJECT_ID,
        "inventory": inventory_yaml,
        "ssh_key_id": 1,
        "become_key_id": 2,
        "type": "static-yaml"
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        return response.json().get("id")
    module.fail_json(msg=f"Fout bij aanmaken inventory: {response.text}")

def create_environment(module, failed_vars):
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/environment"
    payload = {
        "name": "Mislukte Variabelen",
        "project_id": PROJECT_ID,
        "json": json.dumps({"failed_variables": failed_vars}),
        "env": "{}",
        "secrets": []
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        return response.json().get("id")
    module.fail_json(msg=f"Fout bij aanmaken environment: {response.text}")

def create_template(module, inventory_id, environment_id, playbook_name):
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates"
    payload = {
        "project_id": PROJECT_ID,
        "inventory_id": inventory_id,
        "repository_id": 1,
        "environment_id": environment_id,
        "name": "Backup Template",
        "playbook": playbook_name,
        "allow_override_args_in_task": False,
        "limit": "",
        "suppress_success_alerts": True,
        "app": "ansible",
        "git_branch": "main"
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        return True
    module.fail_json(msg=f"Fout bij aanmaken template: {response.text}")

def main():
    module = AnsibleModule(
        argument_spec={
            'mislukte_hosts': {'type': 'list', 'required': True},
            'mislukte_variabelen': {'type': 'list', 'required': True},
        },
        supports_check_mode=True
    )

    failed_hosts = module.params['mislukte_hosts']
    failed_vars = module.params['mislukte_variabelen']
    playbook_name = get_last_playbook_name(module)

    if not playbook_name:
        module.fail_json(msg="Geen playbook naam gevonden!")

    inventory_id = 2 if not failed_hosts else create_inventory(module, failed_hosts)
    environment_id = 1 if not failed_vars else create_environment(module, failed_vars)

    if create_template(module, inventory_id, environment_id, playbook_name):
        module.exit_json(changed=True, msg="Semaphore resources succesvol aangemaakt!")

if __name__ == '__main__':
    main()
