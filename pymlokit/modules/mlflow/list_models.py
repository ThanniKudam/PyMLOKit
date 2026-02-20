from pymlokit.platforms.mlflow_api import creds_valid, list_models
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, url: str) -> None:
     print(generate_header("list-models", platform))
 
     print("")
     print(f"[*] INFO: Performing list-models module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not url:
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     if not creds_valid(credential, url):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     models = list_models(credential, url)
     print_table(
         ["Name", "Version", "Status", "Description", "Artifact Location"],
         [[m["name"], m["version"], m["status"], m["description"], m["artifact_location"]] for m in models],
     )
     print("")
 
