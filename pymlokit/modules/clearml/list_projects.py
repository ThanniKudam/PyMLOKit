from pymlokit.platforms.clearml_api import creds_valid, list_projects
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, api_url: str) -> None:
    print(generate_header("list-projects", platform))

    if not api_url:
        print("")
        print("[-] ERROR: Missing required command argument: /api-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-projects module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    print(f"[*] INFO: Listing projects in {platform}")
    print("")

    projects = list_projects(credential, api_url)
    if not projects:
        print("[-] INFO: No projects found.")
        print("")
        return

    # We select relevant columns for display
    display = []
    for p in projects:
        display.append({
            "Name": p.get("name", ""),
            "ID": p.get("id", ""),
            "Created": p.get("created", ""),
            "Last Update": p.get("last_update", ""),
        })

    print_table(display)
    print("")
