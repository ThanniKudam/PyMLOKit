from pymlokit.platforms.clearml_api import creds_valid, list_models
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, api_url: str, project_id: str = "") -> None:
    print(generate_header("list-models", platform))

    if not api_url:
        print("")
        print("[-] ERROR: Missing required command argument: /api-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-models module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    if project_id:
        print(f"[*] INFO: Listing models for project {project_id}")
    else:
        print(f"[*] INFO: Listing all models")
    print("")

    models = list_models(credential, api_url, project_id)
    if not models:
        print("[-] INFO: No models found.")
        print("")
        return

    # We select relevant columns for display
    display = []
    for m in models:
        display.append({
            "Name": m.get("name", ""),
            "ID": m.get("id", ""),
            "Project": m.get("project", ""),
            "Framework": m.get("framework", ""),
            "Created": m.get("created", ""),
        })

    print_table(display)
    print("")
