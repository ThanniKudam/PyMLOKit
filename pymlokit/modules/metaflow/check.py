from pymlokit.platforms.metaflow_api import creds_valid
from pymlokit.utils.arg_utils import generate_header


def run(credential: str, platform: str, service_url: str) -> None:
    print(generate_header("check", platform))

    if not service_url:
        print("")
        print("[-] ERROR: Missing required command argument: /service-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing check module for {platform}")
    print("")
    print("[*] INFO: Checking service connectivity")
    print("")

    if not creds_valid(service_url):
        print("[-] ERROR: Could not connect to Metaflow Service (or invalid response).")
        print("")
        return

    print("[+] SUCCESS: Service is reachable.")
    print("")
