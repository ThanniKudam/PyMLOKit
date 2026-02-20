import os
 
from pymlokit.platforms.azureml_api import creds_valid, download_blob, get_dataset, get_datastore
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
 
 
def run(
     credential: str,
     platform: str,
     subscription_id: str,
     region: str,
     resource_group: str,
     workspace: str,
     dataset_id: str,
 ) -> None:
     print(generate_header("download-dataset", platform))
 
     if not subscription_id or not region or not resource_group or not workspace or not dataset_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing download-datasets module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     print(f"[*] INFO: Getting Azure file path for dataset with ID: {dataset_id}")
     print("")
 
     dataset = get_dataset(credential, subscription_id, region, resource_group, workspace, dataset_id)
     if not dataset:
         return
 
     azure_file_path = str(dataset.get("azure_file_path", "") or "")
     print(azure_file_path)
     print("")
 
     parts = azure_file_path.split("/")
     if len(parts) < 5:
         return
     storage_account = parts[2]
     storage_container = parts[3]
     relative_path = "/".join(parts[4:])
 
     print("[*] INFO: Storage Account: ")
     print(storage_account)
     print("")
     print("[*] INFO: Storage Container: ")
     print(storage_container)
     print("")
     print("[*] INFO: Storage Relative Path: ")
     print(relative_path)
     print("")
     print("[*] INFO: Datastore Name: ")
     print(str(dataset.get("datastore_name", "") or ""))
     print("")
 
     datastore = get_datastore(credential, subscription_id, region, resource_group, workspace, str(dataset.get("datastore_name", "") or ""))
     if not datastore:
         return
 
     content = download_blob(datastore["account_name"], datastore["credential"], storage_container, relative_path)
     if not content:
         return
 
     file_out = f"MLOKit-{generate_random_name()}"
     out_path = os.path.join(os.getcwd(), file_out)
     with open(out_path, "wb") as f:
         f.write(content)
 
     print("")
     print(f"[+] SUCCESS: Dataset written to: {out_path}")
     print("")
     print("")
 
