#!/usr/bin/python3
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec={})
    response = {"message": "Hallo vanuit mijn custom Ansible module!"}
    module.exit_json(changed=False, result=response)

if __name__ == '__main__':
    main()

