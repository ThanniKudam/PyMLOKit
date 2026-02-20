from pymlokit.platforms.azureml_api import creds_valid, list_subscriptions
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str) -> None:
     print(generate_header("check", platform))
 
     print("")
     print(f"[*] INFO: Performing check module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     print("[*] INFO: Listing subscriptions user has acess to")
     print("")
     subs = list_subscriptions(credential)
     print_table(
         ["Name", "Subscription ID", "Status"],
         [[s["display_name"], s["id"], s["state"]] for s in subs],
     )
     print("")
 
