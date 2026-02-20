import os
 
from pymlokit.platforms.bigml_api import creds_valid, download_dataset_bytes
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
 
 
def run(credential: str, platform: str, dataset_id: str) -> None:
     print(generate_header("download-dataset", platform))
 
     if not dataset_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing download-dataset module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     print(f"[*] INFO: Downloading dataset with ID {dataset_id} to the current working directory of {os.getcwd()}")
     print("")
 
     content = download_dataset_bytes(credential, dataset_id)
     if not content:
         return
 
     file_name = f"MLOKit-{generate_random_name()}"
     with open(file_name, "wb") as f:
         f.write(content)
 
     print(f"[+] SUCCESS: Dataset written to: {os.path.join(os.getcwd(), file_name)}")
     print("")
 
