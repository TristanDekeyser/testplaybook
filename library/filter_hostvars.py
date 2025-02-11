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

    for host, vars_dict in hostvars.items():
        # Behoud alleen de variabelen die NIET standaard in Ansible zitten
        custom_vars = {k: v for k, v in vars_dict.items() if not k.startswith("ansible_", "changed")}
        filtered_vars[host] = custom_vars

    module.exit_json(changed=False, filtered_data=filtered_vars)

if __name__ == '__main__':
    main()
