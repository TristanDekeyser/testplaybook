import requests
from ansible.module_utils.basic import AnsibleModule

# Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.133:3000/api"
SEMAPHORE_TOKEN = "owozuup-zne7p-stkhhs3hdfr6efiyk1rh8okh_70bu="
PROJECT_ID = 1

HEADERS = {
    "Authorization": f"Bearer {SEMAPHORE_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_existing_items(url, module, item_name):
    """Haal alle items op en zoek naar een specifieke naam."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        items = response.json()
        for item in items:
            if item.get("name") == item_name:
                return item.get("id")
    else:
        module.fail_json(msg=f"Fout bij ophalen van {item_name}: {response.status_code} - {response.text}")
    return None

def delete_item(url, module, item_name):
    """Verwijdert een item als het bestaat."""
    item_id = get_existing_items(url, module, item_name)
    if item_id:
        delete_url = f"{url}/{item_id}"
        response = requests.delete(delete_url, headers=HEADERS)
        if response.status_code in [200, 204]:
            return f"{item_name} succesvol verwijderd."
        else:
            module.fail_json(msg=f"Fout bij verwijderen van {item_name}: {response.status_code} - {response.text}")
    return f"{item_name} niet gevonden, geen actie nodig."

def main():
    module = AnsibleModule(argument_spec={}, supports_check_mode=True)

    try:
        template_result = delete_item(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates", module, "Backup Template")
        inventory_result = delete_item(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/inventory", module, "Backup Inventory")
        environment_result = delete_item(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/environment", module, "Mislukte Variabelen")

        module.exit_json(changed=True, msg="Cleanup voltooid.", details={
            "template": template_result,
            "inventory": inventory_result,
            "environment": environment_result
        })

    except Exception as e:
        module.fail_json(msg=f"Fout: {str(e)}")

if __name__ == "__main__":
    main()
