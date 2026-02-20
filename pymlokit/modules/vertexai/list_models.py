from pymlokit.platforms.vertexai_api import creds_valid, list_models, list_regions
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, project: str) -> None:
     print(generate_header("list-models", platform))
 
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
         for m in list_models(credential, r, project):
             rows.append([m["display_name"], m["id"], m["create_time"], m["region"], m["source_type"], m["exportable_format"]])
 
     print_table(["Name", "Model ID", "Creation Date", "Region", "Model Type", "Export Format"], rows)
     print("")
 
