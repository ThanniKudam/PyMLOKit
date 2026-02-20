from pymlokit.platforms.kubeflow_api import creds_valid, list_runs
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, api_url: str) -> None:
    print(generate_header("list-models", platform))

    if not api_url:
        print("")
        print("[-] ERROR: Missing required command argument: /api-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-models (runs) module for {platform}")
    print("")
    print("[*] INFO: Checking credentials/connectivity")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID or Server unreachable.")
        print("")
        return

    print("[+] SUCCESS: Service is reachable.")
    print("")

    print(f"[*] INFO: Listing runs")
    print("")

    try:
        runs = list_runs(credential, api_url)
        if not runs:
            print("[-] INFO: No runs found.")
            print("")
            return

        display = []
        for r in runs:
            display.append({
                "Run ID": r.get("id", ""),
                "Name": r.get("name", ""),
                "Created": r.get("created_at", ""),
                "Status": r.get("status", ""),
                "Pipeline ID": r.get("pipeline_spec", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list runs: {e}")
        print("")
