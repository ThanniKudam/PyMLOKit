from pymlokit.platforms.wandb_api import creds_valid, list_projects
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str) -> None:
    print(generate_header("list-projects", platform))

    print("")
    print(f"[*] INFO: Performing list-projects module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    print(f"[*] INFO: Listing projects for default entity")
    print("")

    try:
        projects = list_projects(credential)
        if not projects:
            print("[-] INFO: No projects found.")
            print("")
            return

        display = []
        for p in projects:
            display.append({
                "Name": p.get("name", ""),
                "Entity": p.get("entity", ""),
                "URL": p.get("url", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list projects: {e}")
        print("")
