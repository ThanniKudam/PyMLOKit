from pymlokit.platforms.azureml_api import creds_valid, list_workspaces
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, subscription_id: str) -> None:
     print(generate_header("list-projects", platform))
 
     if not subscription_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing list-projects module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     workspaces = list_workspaces(credential, subscription_id)
     print_table(
         ["Name", "Workspace ID", "Region", "Resource Group", "Creation Time"],
         [[w["name"], w["workspace_id"], w["region"], w["resource_group"], w["creation_time"]] for w in workspaces],
     )
     print("")
 
