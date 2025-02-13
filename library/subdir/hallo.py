from ansible.module_utils.basic import AnsibleModule
import subprocess

def main():
    # Definieer de argumenten die we verwachten
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type='str', required=True)  # Het commando dat we willen uitvoeren
        )
    )

    # Haal het commando op uit de parameters
    command = module.params['command']

    try:
        # Voer het commando uit
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        # Decodeer het resultaat en stuur het terug naar Ansible
        module.exit_json(changed=False, stdout=result.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        # In geval van een fout, stuur een foutmelding terug
        module.fail_json(msg=f"Fout bij uitvoeren van commando: {e.output.decode('utf-8')}")

if __name__ == '__main__':
    main()
