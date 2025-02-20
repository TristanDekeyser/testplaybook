#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import yaml
import os

# Functie om variabelen om te zetten naar het juiste Ansible formaat
def transform_variable_name(original_name):
    """Zet een originele variabelenaam om naar het Ansible formaat, met correcte behandeling van 'client_'."""
    if original_name.startswith("add_oauth_client_"):
        return original_name  # Geen wijziging nodig

    if original_name.startswith("client"):
        return "add_oauth_" + original_name  # Alleen 'client_' vervangen door 'add_oauth_'

    return "add_oauth_client_" + original_name  # Standaard voorvoegsel toevoegen

def rename_variables(data):
    """Herschrijft alle variabelen volgens het Ansible-formaat."""
    renamed_data = {}
    for key, value in data.items():
        new_key = transform_variable_name(key)  # Zet naam om
        renamed_data[new_key] = value
    return renamed_data

def read_and_transform_yaml(file_path):
    """Leest een YAML-bestand en transformeert de variabelen."""
    if not os.path.exists(file_path):
        return None, f"Bestand niet gevonden: {file_path}"
    
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            if not isinstance(data, dict):
                return None, f"Ongeldig YAML-formaat in {file_path}"
            return rename_variables(data), None
    except Exception as e:
        return None, f"Fout bij lezen van {file_path}: {str(e)}"

def main():
    module_args = {
        "file_path": {"type": "str", "required": True}
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    file_path = module.params["file_path"]
    transformed_data, error = read_and_transform_yaml(file_path)

    if error:
        module.fail_json(msg=error)

    module.exit_json(changed=True, transformed_vars=transformed_data)

if __name__ == "__main__":
    main()
