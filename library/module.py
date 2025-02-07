#!/usr/bin/python3
import subprocess
from ansible.module_utils.basic import AnsibleModule

def main():
    # Definieer de AnsibleModule met eventuele parameters
    module = AnsibleModule(argument_spec={})

    try:
        # Voer het 'ls' commando uit en vang de uitvoer op
        result = subprocess.run(['ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Controleer of het commando succesvol was
        if result.returncode == 0:
            response = {
                "message": "De ls opdracht is geslaagd.",
                "output": result.stdout.strip()  # Verwijder extra nieuwe regels
            }
            module.exit_json(changed=False, result=response)
        else:
            # Als er een fout is bij het uitvoeren van de 'ls' opdracht
            response = {
                "message": "Er is een fout opgetreden bij het uitvoeren van 'ls'.",
                "error": result.stderr.strip()
            }
            module.fail_json(msg="Fout bij het uitvoeren van 'ls'.", result=response)

    except Exception as e:
        # Foutafhandelingsblok voor onverwachte fouten
        module.fail_json(msg=f"Er is een onverwachte fout opgetreden: {str(e)}")

if __name__ == '__main__':
    main()
