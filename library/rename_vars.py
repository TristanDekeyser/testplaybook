#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import yaml
import os

# Mapping van de originele variabelen naar de gewenste Ansible variabelennamen
VAR_MAPPING = {
    "client_id": "add_oauth_client_clientId",
    "client_name": "add_oauth_client_name",
    "client_secret": "add_oauth_client_clientSecret",
    "company_name": "add_oauth_client_companyName",
    "definition_name": "add_oauth_client_definitionName",
    "extProperties": "add_oauth_client_extProperties",
    "redirect_uri": "add_oauth_client_redirectUri",
    "require_pkce": "add_oauth_client_requirePkce"
}

def rename_variables(data):
    """Zet de originele variabelen om naar de nieuwe namen volgens VAR_MAPPING."""
    renamed_data = {}
    for key, value in data.items():
        new_key = VAR_MAPPING.get(key, key)  # Vervang met nieuwe naam als beschikbaar
        renamed_data[new_key] = value
    return renamed_data

def read_and_transform_yaml(file_path):
    """Leest een YAML-bestand, transformeert de variabelen en geeft ze terug."""
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
