from pymlokit.platforms.vertexai_api import creds_valid, list_datasets, list_regions
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, project: str) -> None:
     print(generate_header("list-datasets", platform))
 
     if not project:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     print(f"[*] INFO: Listing regions for the {project} project")
     print("")
     regions = list_regions(credential, project)
     for r in regions:
         print(r)
 
     rows = []
     for r in regions:
         for d in list_datasets(credential, r, project):
             rows.append([d["display_name"], d["id"], d["create_time"], d["update_time"], d["region"], d["uri"]])
 
     print_table(["Name", "Dataset ID", "Creation Date", "Update Date", "Region", "File Path"], rows)
     print("")
 
