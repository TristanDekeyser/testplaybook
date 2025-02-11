#!/usr/bin/python3
import json
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec={
            'hostvars': {'type': 'dict', 'required': True}
        }
    )

    hostvars = module.params['hostvars']
    filtered_vars = {}

    exclude_keys = [
        "inventory_file", "inventory_dir", "inventory_hostname",
        "inventory_hostname_short", "group_names", "playbook_dir",
        "groups", "omit", "command_result", "semaphore_vars", "changed", "failed"
    ]

    for host, vars_dict in hostvars.items():
        # Alleen de gewenste variabelen behouden
        custom_vars = {k: v for k, v in vars_dict.items() if k not in exclude_keys and not k.startswith("ansible_")}

        # Host alleen toevoegen als er variabelen overblijven
        if custom_vars:
            filtered_vars[host] = custom_vars

if __name__ == '__main__':
    main()
