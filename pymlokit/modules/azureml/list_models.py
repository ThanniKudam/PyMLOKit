from pymlokit.platforms.azureml_api import creds_valid, list_models
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, subscription_id: str, region: str, resource_group: str, workspace: str) -> None:
     print(generate_header("list-models", platform))
 
     if not subscription_id or not region or not resource_group or not workspace:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing list-models module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     models = list_models(credential, subscription_id, region, resource_group, workspace)
     print_table(
         ["Name", "ID", "Model Type", "Creation Time", "Update Time"],
         [[m["name"], m["id"], m["model_type"], m["created_time"], m["modified_time"]] for m in models],
     )
     print("")
 
