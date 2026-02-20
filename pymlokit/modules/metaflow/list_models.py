from pymlokit.platforms.metaflow_api import creds_valid, list_runs
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, service_url: str, project: str) -> None:
    print(generate_header("list-models", platform))

    if not service_url or not project:
        print("")
        print("[-] ERROR: Missing required command argument: /service-url:... or /project:...")
        print("    (Project is Flow ID in Metaflow)")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-models (runs) module for {platform}")
    print("")
    print("[*] INFO: Checking service connectivity")
    print("")

    if not creds_valid(service_url):
        print("[-] ERROR: Could not connect to Metaflow Service.")
        print("")
        return

    print("[+] SUCCESS: Service is reachable.")
    print("")

    print(f"[*] INFO: Listing runs for flow {project}")
    print("")

    try:
        runs = list_runs(service_url, project)
        if not runs:
            print("[-] INFO: No runs found.")
            print("")
            return

        display = []
        for r in runs:
            display.append({
                "Run ID": r.get("id", ""),
                "User": r.get("user", ""),
                "Status": r.get("status", ""),
                "Created At": r.get("created_at", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list runs: {e}")
        print("")
