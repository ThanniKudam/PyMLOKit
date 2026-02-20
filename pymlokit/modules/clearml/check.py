from pymlokit.platforms.clearml_api import creds_valid
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
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")
