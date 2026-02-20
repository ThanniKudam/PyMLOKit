from pymlokit.platforms.clearml_api import creds_valid, list_datasets
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, api_url: str, project_id: str = "") -> None:
    print(generate_header("list-datasets", platform))

    if not api_url:
        print("")
        print("[-] ERROR: Missing required command argument: /api-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-datasets module for {platform}")
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
        print(f"[*] INFO: Listing datasets (data_processing tasks) for project {project_id}")
    else:
        print(f"[*] INFO: Listing all datasets (data_processing tasks)")
    print("")

    datasets = list_datasets(credential, api_url, project_id)
    if not datasets:
        print("[-] INFO: No datasets found.")
        print("")
        return

    # We select relevant columns for display
    display = []
    for d in datasets:
        display.append({
            "Name": d.get("name", ""),
            "ID": d.get("id", ""),
            "Project": d.get("project", ""),
            "Type": d.get("type", ""),
            "Status": d.get("status", ""),
            "Created": d.get("created", ""),
        })

    print_table(display)
    print("")
