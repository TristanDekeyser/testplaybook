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
        "groups", "omit", "command_result", "semaphore_vars"
    ]

    for host, vars_dict in hostvars.items():
        # Alleen de custom variabelen behouden door de exclude_keys eruit te filteren
        custom_vars = {k: v for k, v in vars_dict.items() if k not in exclude_keys and not k.startswith("ansible_")}
        filtered_vars[host] = custom_vars

    module.exit_json(changed=False, filtered_data=filtered_vars)

if __name__ == '__main__':
    main()
