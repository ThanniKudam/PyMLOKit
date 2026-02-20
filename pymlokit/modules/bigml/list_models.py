from pymlokit.platforms.bigml_api import creds_valid, list_models
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str) -> None:
     print(generate_header("list-models", platform))
 
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
 
     models = list_models(credential)
     print_table(
         ["Name", "Visibility", "Created By", "Creation Date", "Model ID"],
         [[m["name"], m["visibility"], m["creator"], m["created"], m["id"]] for m in models],
     )
     print("")
 
