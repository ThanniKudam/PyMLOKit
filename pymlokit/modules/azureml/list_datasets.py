from pymlokit.platforms.azureml_api import creds_valid, list_datasets
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, subscription_id: str, region: str, resource_group: str, workspace: str) -> None:
     print(generate_header("list-datasets", platform))
 
     if not subscription_id or not region or not resource_group or not workspace:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing list-datasets module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     datasets = list_datasets(credential, subscription_id, region, resource_group, workspace)
     print_table(
         ["File Name", "ID", "State", "File Type", "Datastore Name"],
         [[d["file_name"], d["id"], d["state"], d["data_type"], d["datastore_name"]] for d in datasets],
     )
     print("")
 
