from pymlokit.platforms.kubeflow_api import creds_valid, list_pipelines
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
    print(f"[*] INFO: Performing list-projects (pipelines) module for {platform}")
    print("")
    print("[*] INFO: Checking credentials/connectivity")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID or Server unreachable.")
        print("")
        return

    print("[+] SUCCESS: Service is reachable.")
    print("")

    print(f"[*] INFO: Listing pipelines")
    print("")

    try:
        pipelines = list_pipelines(credential, api_url)
        if not pipelines:
            print("[-] INFO: No pipelines found.")
            print("")
            return

        display = []
        for p in pipelines:
            display.append({
                "Name": p.get("name", ""),
                "ID": p.get("id", ""),
                "Created": p.get("created_at", ""),
                "Description": p.get("description", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list pipelines: {e}")
        print("")
