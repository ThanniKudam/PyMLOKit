from pymlokit.platforms.wandb_api import creds_valid, list_models
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, project: str) -> None:
    print(generate_header("list-models", platform))

    if not project:
        print("")
        print("[-] ERROR: Missing required command argument: /project:...")
        print("    (Format: entity/project or just project if default entity)")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-models module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    print(f"[*] INFO: Listing models (Artifacts type='model') for project {project}")
    print("")

    # Parse entity/project if provided
    entity = ""
    proj_name = project
    if "/" in project:
        parts = project.split("/", 1)
        entity = parts[0]
        proj_name = parts[1]

    try:
        models = list_models(credential, entity, proj_name)
        if not models:
            print("[-] INFO: No models found.")
            print("    (Note: Ensure the project exists and contains artifacts of type 'model'.")
            print("     If the project is in a team/organization, use 'entity/project' format.)")
            print("")
            return

        display = []
        for m in models:
            display.append({
                "Name": m.get("name", ""),
                "ID": m.get("id", ""),
                "Description": m.get("description", "") or "",
                "Created": m.get("created_at", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list models: {e}")
        print("")
