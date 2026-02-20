from pymlokit.platforms.metaflow_api import creds_valid, list_flows
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table


def run(credential: str, platform: str, service_url: str) -> None:
    print(generate_header("list-projects", platform))

    if not service_url:
        print("")
        print("[-] ERROR: Missing required command argument: /service-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing list-projects (flows) module for {platform}")
    print("")
    print("[*] INFO: Checking service connectivity")
    print("")

    if not creds_valid(service_url):
        print("[-] ERROR: Could not connect to Metaflow Service.")
        print("")
        return

    print("[+] SUCCESS: Service is reachable.")
    print("")

    print(f"[*] INFO: Listing flows")
    print("")

    try:
        flows = list_flows(service_url)
        if not flows:
            print("[-] INFO: No flows found.")
            print("")
            return

        display = []
        for f in flows:
            display.append({
                "Flow ID": f.get("id", ""),
                "Created At": f.get("created_at", ""),
            })

        print_table(display)
        print("")
    except Exception as e:
        print(f"[-] ERROR: Failed to list flows: {e}")
        print("")
