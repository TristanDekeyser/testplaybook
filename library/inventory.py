import requests
import yaml
from ansible.module_utils.basic import AnsibleModule

# Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.133:3000/api"
SEMAPHORE_TOKEN = "owozuup-zne7p-stkhhs3hdfr6efiyk1rh8okh_70bu="  # Voeg hier je token in
PROJECT_ID = 1

def get_last_playbook_name(module):
    """Haalt de naam van het laatste playbook op uit de Semaphore taak"""
    headers = {
        "Authorization": f"Bearer {SEMAPHORE_TOKEN}",
        "Content-Type": "application/json"
    }

    # Verkrijg de lijst van taken van de Semaphore API
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}"
    response = requests.get(url + "/tasks", headers=headers)

    if response.status_code == 200:
        tasks = response.json()
        if tasks:
            # Haal de laatste taak op (meestal de eerste in de lijst)
            latest_task = tasks[0]
            tpl_playbook = latest_task.get("tpl_playbook")

            if tpl_playbook:
                print(f"De naam van het laatste playbook is: {tpl_playbook}")
                return tpl_playbook
            else:
                error_msg = "Er is geen playbook naam gevonden in de laatste taak."
                module.fail_json(msg=error_msg)
                return None
        else:
            error_msg = "Geen taken gevonden!"
            module.fail_json(msg=error_msg)
            return None
    else:
        error_msg = f"Fout bij het ophalen van taken: {response.status_code}"
        module.fail_json(msg=error_msg)
        return None

def create_inventory(module, inventory_data):
    """ Maakt de inventory aan in Semaphore en retourneert de ID """
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/inventory"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    
    # Format de inventory_data naar een statisch YAML-formaat
    inventory_yaml = {
        "all": {
            "children": {
                "machines": {
                    "hosts": inventory_data["hosts"]
                }
            }
        }
    }

    # Converteer de dictionary naar YAML-formaat (inclusief juiste inspringingen)
    inventory_string = yaml.dump(inventory_yaml, default_flow_style=False, allow_unicode=True)

    payload = {
        "name": "Backup Inventory",
        "project_id": PROJECT_ID,
        "inventory": inventory_string,  # Gebruik de YAML-string hier
        "ssh_key_id": 2, 
        "become_key_id": 4, 
        "type": "static-yaml"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        # Log de volledige responsinhoud om gedetailleerde foutinformatie te krijgen
        error_msg = f"Fout bij aanmaken van inventory: {response.status_code} - {response.text}"
        module.fail_json(msg=error_msg)  # Toont gedetailleerde foutinformatie
        return None
    
def create_template(module, inventory_id, playbook_name):
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "project_id": PROJECT_ID,
        "inventory_id": inventory_id,
        "repository_id": 1,
        "environment_id": 2,
        "name": "backup",
        "playbook": playbook_name,
        "allow_override_args_in_task": False,
        "limit": "",
        "suppress_success_alerts": True,
        "app": "ansible",
        "git_branch": "main"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        return True
    else:
        # Log de volledige responsinhoud om gedetailleerde foutinformatie te krijgen
        error_msg = f"Fout bij het aanmaken van template: {response.status_code} - {response.text}"
        module.fail_json(msg=error_msg)  # Gebruik fail_json om gedetailleerde foutinformatie terug te geven
        return False

def main():
    module = AnsibleModule(
        argument_spec={
            'mislukte_hosts': {'type': 'list', 'required': True},
        },
        supports_check_mode=True
    )

    try:
        # Verkrijg de mislukte hosts van de invoer
        mislukte_hosts = module.params['mislukte_hosts']
        playbook_name = get_last_playbook_name(module)

        if not playbook_name:
            module.fail_json(msg="Geen playbook naam gevonden in de laatste taak!")

        # Maak een inventory met de mislukte hosts
        inventory_data = {"hosts": mislukte_hosts}
        inventory_id = create_inventory(module, inventory_data)
        if not inventory_id:
            module.fail_json(msg="Fout bij aanmaken van inventory!")

        # Maak het template met het playbook
        if not create_template(module, inventory_id, playbook_name):
            module.fail_json(msg="Fout bij aanmaken van template!")

        module.exit_json(changed=True, msg="Semaphore resources succesvol aangemaakt!")

    except Exception as e:
        module.fail_json(msg=f"Fout: {str(e)}")

if __name__ == '__main__':
    main()
