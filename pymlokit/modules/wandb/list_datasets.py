from pymlokit.platforms.wandb_api import creds_valid, list_datasets
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, project: str) -> None:
    print(generate_header("list-datasets", platform))

    if not project:
        print("")
        print("[-] ERROR: Missing required command argument: /project:...")
        print("    (Format: entity/project or just project if default entity)")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-datasets module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    print(f"[*] INFO: Listing datasets (Artifacts type='dataset') for project {project}")
    print("")

    entity = ""
    proj_name = project
    if "/" in project:
        parts = project.split("/", 1)
        entity = parts[0]
        proj_name = parts[1]

    try:
        datasets = list_datasets(credential, entity, proj_name)
        if not datasets:
            print("[-] INFO: No datasets found.")
            print("    (Note: Ensure the project exists and contains artifacts of type 'dataset'.")
            print("     If the project is in a team/organization, use 'entity/project' format.)")
            print("")
            return

        display = []
        for d in datasets:
            display.append({
                "Name": d.get("name", ""),
                "ID": d.get("id", ""),
                "Description": d.get("description", "") or "",
                "Created": d.get("created_at", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list datasets: {e}")
        print("")
