#!/usr/bin/python3
import json
from ansible.module_utils.basic import AnsibleModule

def main():
    # Definieer de AnsibleModule met eventuele parameters
    module = AnsibleModule(
        argument_spec={
            'hostvars_json': {'type': 'str', 'required': True}
        }
    )

    try:
        # Laad de hostvars uit de input JSON
        hostvars = json.loads(module.params['hostvars_json'])

        # Hier filteren we alleen de benodigde hostvariabelen
        # In dit geval, halen we een paar specifieke variabelen uit, zoals 'semaphore_vars'
        filtered_vars = {}
        for host, vars in hostvars.items():
            if 'semaphore_vars' in vars:
                filtered_vars[host] = vars['semaphore_vars']
        
        # Stuur de gefilterde variabelen terug
        module.exit_json(changed=False, filtered_vars=filtered_vars)

    except Exception as e:
        # Foutafhandelingsblok voor onverwachte fouten
        module.fail_json(msg=f"Er is een onverwachte fout opgetreden: {str(e)}")

if __name__ == '__main__':
    main()
