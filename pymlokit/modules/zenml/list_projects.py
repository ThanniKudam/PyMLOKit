from pymlokit.platforms.zenml_api import creds_valid, list_projects
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
    print(f"[*] INFO: Performing list-projects (workspaces) module for {platform}")
    print("")
    print("[*] INFO: Checking credentials/connectivity")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID or Server unreachable.")
        print("")
        return

    print("[+] SUCCESS: Service is reachable.")
    print("")

    print(f"[*] INFO: Listing workspaces (projects)")
    print("")

    try:
        projects = list_projects(credential, api_url)
        if not projects:
            print("[-] INFO: No projects found.")
            print("")
            return

        display = []
        for p in projects:
            display.append({
                "Name": p.get("name", ""),
                "ID": p.get("id", ""),
                "Created": p.get("created", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list projects: {e}")
        print("")
