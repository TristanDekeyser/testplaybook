from ansible.module_utils.basic import AnsibleModule
import requests
import yaml  # Zorg ervoor dat PyYAML is geïnstalleerd: pip install pyyaml

# Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.133:3000/api"
SEMAPHORE_TOKEN = "owozuup-zne7p-stkhhs3hdfr6efiyk1rh8okh_70bu="
PROJECT_ID = 1

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
        "ssh_key_id": 2,  # Controleer of je de juiste SSH key ID hebt
        "become_key_id": 4,  # Controleer of je de juiste become key ID hebt
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
    
def create_template(inventory_id, environment_id):
    url = f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates"
    headers = {"Authorization": f"Bearer {SEMAPHORE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "project_id": PROJECT_ID,
        "inventory_id": inventory_id,
        "repository_id": 1,
        "environment_id": 2,
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
        mislukte_hosts = module.params['mislukte_hosts']

        # Maak een inventory met de mislukte hosts
        inventory_data = {"hosts": mislukte_hosts}
        inventory_id = create_inventory(module, inventory_data)
        if not inventory_id:
            module.fail_json(msg="Fout bij aanmaken van inventory!")

        if not create_template(inventory_id):
            module.fail_json(msg="Fout bij aanmaken van template!")

        module.exit_json(changed=True, msg="Semaphore resources succesvol aangemaakt!")

    except Exception as e:
        module.fail_json(msg=f"Fout: {str(e)}")

if __name__ == '__main__':
    main()
