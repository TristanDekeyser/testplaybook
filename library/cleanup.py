import requests
import json
import zipfile
import os
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

# Semaphore API Configuratie
SEMAPHORE_URL = "http://192.168.242.160:3000/api"
SEMAPHORE_TOKEN = "tuwnyelwoulicyww1e87zznnnaq7w6pkoadjh-z3uz8="
PROJECT_ID = 1

HEADERS = {
    "Authorization": f"Bearer {SEMAPHORE_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_existing_items(url, module, item_name):
    """Haal alle items op en zoek naar items met een specifieke naam."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        items = response.json()
        matched_items = [item for item in items if item.get("name") == item_name]
        return matched_items
    else:
        module.fail_json(msg=f"Fout bij ophalen van {item_name}: {response.status_code} - {response.text}")
    return []

def save_and_zip_config(all_items):
    """Sla de configuratie op in één bestand en zip het bestand."""
    # Verkrijg de huidige datum en tijd
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Maak een bestandspad om de configuratie op te slaan
    filename = f"/tmp/configurations_{current_time}.json"
    
    # Sla de configuratie op in een JSON-bestand
    with open(filename, 'w') as f:
        json.dump(all_items, f, indent=4)

    # Maak een zip-bestand van het opgeslagen JSON-bestand
    zip_filename = f"/tmp/configurations_{current_time}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(filename, os.path.basename(filename))
    
    # Verwijder het tijdelijke JSON-bestand na het zippen
    os.remove(filename)

    print(f"Configuratie opgeslagen en gecomprimeerd als {zip_filename}")
    return zip_filename

def delete_oldest_items(url, module, items, number_to_delete=2):
    """Verwijder de oudste items (met de laagste ID's)."""
    if len(items) > number_to_delete:
        # Sorteer op ID om de oudste te krijgen
        sorted_items = sorted(items, key=lambda x: x.get("id"))
        items_to_delete = sorted_items[:number_to_delete]

        for item in items_to_delete:
            delete_url = f"{url}/{item['id']}"
            response = requests.delete(delete_url, headers=HEADERS)
            if response.status_code in [200, 204]:
                print(f"Item {item['name']} met ID {item['id']} succesvol verwijderd.")
            else:
                module.fail_json(msg=f"Fout bij verwijderen van item {item['name']} met ID {item['id']}: {response.status_code} - {response.text}")
        
        return items_to_delete
    else:
        print(f"Er zijn minder dan {number_to_delete} items met de naam gevonden. Geen items verwijderd.")
    return []

def main():
    module = AnsibleModule(argument_spec={}, supports_check_mode=True)

    try:
        # Haal de items op voor templates, inventory en environment
        template_items = get_existing_items(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates", module, "Backup Template")
        inventory_items = get_existing_items(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/inventory", module, "Backup Inventory")
        environment_items = get_existing_items(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/environment", module, "Mislukte Variabelen")

        # Verwijder de oudste items als er meer dan 10 zijn
        deleted_template_items = delete_oldest_items(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/templates", module, template_items)
        deleted_inventory_items = delete_oldest_items(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/inventory", module, inventory_items)
        deleted_environment_items = delete_oldest_items(f"{SEMAPHORE_URL}/project/{PROJECT_ID}/environment", module, environment_items)

        # Maak een enkele JSON met alle verwijderde items
        all_items = {
            "templates": deleted_template_items,
            "inventory": deleted_inventory_items,
            "environment": deleted_environment_items
        }

        # Sla alles op in één bestand en zip het
        zip_filename = save_and_zip_config(all_items)

        # Geef een bericht terug met het zipbestand
        module.exit_json(changed=True, msg="Cleanup voltooid.", details={
            "zip_filename": zip_filename
        })

    except Exception as e:
        module.fail_json(msg=f"Fout: {str(e)}")

if __name__ == "__main__":
    main()
