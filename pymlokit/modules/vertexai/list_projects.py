from pymlokit.platforms.vertexai_api import creds_valid, list_projects
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str) -> None:
     print(generate_header("list-projects", platform))
 
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
 
     projects = list_projects(credential)
     print_table(
         ["Name", "Project ID", "Project Number", "Project State", "Creation Date"],
         [[p.name, p.project_id, p.project_number, p.lifecycle_state, p.create_time] for p in projects],
     )
     print("")
 
