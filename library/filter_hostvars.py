#!/usr/bin/python3
import yaml
from ansible.module_utils.basic import AnsibleModule

def main():
    # Definieer de AnsibleModule met eventuele parameters
    module = AnsibleModule(
        argument_spec={
            'vars_file': {'type': 'str', 'required': True}
        }
    )

    try:
        # Lees de inhoud van de vars.yml file
        with open(module.params['vars_file'], 'r') as f:
            vars_data = yaml.safe_load(f)

        # Hier sturen we de inhoud van de vars.yml terug
        module.exit_json(changed=False, vars_data=vars_data)

    except Exception as e:
        # Foutafhandelingsblok voor onverwachte fouten
        module.fail_json(msg=f"Er is een onverwachte fout opgetreden: {str(e)}")

if __name__ == '__main__':
    main()
