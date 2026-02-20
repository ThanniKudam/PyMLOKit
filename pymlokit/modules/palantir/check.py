from pymlokit.platforms.palantir_api import creds_valid
from pymlokit.utils.arg_utils import generate_header
 
 
def run(credential: str, platform: str) -> None:
     print(generate_header("check", platform))
 
     print("")
     print(f"[*] INFO: Performing check module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if creds_valid(credential):
         print("[+] SUCCESS: Credentials provided are VALID.")
         print("")
     else:
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
 
