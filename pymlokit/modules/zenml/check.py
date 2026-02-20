from pymlokit.platforms.zenml_api import creds_valid
from pymlokit.utils.arg_utils import generate_header


def run(credential: str, platform: str, api_url: str) -> None:
    print(generate_header("check", platform))

    if not api_url:
        print("")
        print("[-] ERROR: Missing required command argument: /api-url:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing check module for {platform}")
    print("")
    print("[*] INFO: Checking credentials/connectivity")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID or Server unreachable.")
        print("")
        return

    print("[+] SUCCESS: Service is reachable and credentials (if any) are valid.")
    print("")
