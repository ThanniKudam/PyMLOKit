from pymlokit.platforms.bigml_api import creds_valid, list_datasets
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str) -> None:
     print(generate_header("list-datasets", platform))
 
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
 
     datasets = list_datasets(credential)
     print_table(
         ["Name", "Visibility", "Creation Date", "Dataset ID"],
         [[d["name"], d["visibility"], d["created"], d["id"]] for d in datasets],
     )
     print("")
 
