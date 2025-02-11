#!/usr/bin/python3
import json
from ansible.module_utils.basic import AnsibleModule

def main():
    # Definieer de AnsibleModule met de vereiste parameters
    module = AnsibleModule(
        argument_spec={
            'vars_file': {'type': 'str', 'required': True}  # pad naar de vars.yml
        }
    )

    try:
        # Lees de inhoud van het bestand vars.yml (in JSON-indeling)
        with open(module.params['vars_file'], 'r') as f:
            vars_data = json.load(f)

        # Hier filteren we alleen de variabelen die we willen behouden
        filtered_vars = {}

        # Doorloop alle hosts en hun variabelen
        for host, hostvars in vars_data.items():
            for key, value in hostvars.items():
                # Sla alle variabelen op behalve 'ansible' gerelateerde en 'omit'
                if key not in ['ansible_check_mode', 'ansible_config_file', 'ansible_facts', 'ansible_forks', 'ansible_inventory_sources', 'ansible_playbook_python', 'ansible_python_interpreter', 'ansible_run_tags', 'ansible_skip_tags', 'ansible_verbosity', 'ansible_version', 'command_result', 'inventory_dir', 'inventory_file', 'inventory_hostname', 'inventory_hostname_short', 'group_names', 'groups', 'semaphore_vars', 'omit']:
                    filtered_vars[key] = value

        # Resultaat terugsturen met alleen de gewenste variabelen
        module.exit_json(changed=False, filtered_vars=filtered_vars)

    except Exception as e:
        # Foutafhandelingsblok voor onverwachte fouten
        module.fail_json(msg=f"Er is een onverwachte fout opgetreden: {str(e)}")

if __name__ == '__main__':
    main()
