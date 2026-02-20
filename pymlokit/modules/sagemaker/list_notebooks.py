from pymlokit.modules.sagemaker._aws import boto3_clients
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, region: str) -> None:
     print(generate_header("list-notebooks", platform))
 
     if not region:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing list-notebooks module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     sm, _ = boto3_clients(credential, region)
 
     rows = []
     next_token = None
     while True:
         kwargs = {"MaxResults": 100}
         if next_token:
             kwargs["NextToken"] = next_token
         resp = sm.list_notebook_instances(**kwargs)
         if not rows:
             print("[+] SUCCESS: Credentials are valid")
             print("")
         for n in resp.get("NotebookInstances", []):
             rows.append(
                 [
                     n.get("NotebookInstanceName", ""),
                     (n.get("CreationTime") or "").strftime("%m/%d/%Y") if hasattr(n.get("CreationTime"), "strftime") else "",
                     n.get("NotebookInstanceStatus", ""),
                     n.get("NotebookInstanceLifecycleConfigName", ""),
                 ]
             )
         next_token = resp.get("NextToken")
         if not next_token:
             break
 
     print_table(["Notebook Name", "Creation Date", "Notebook Status", "Notebook Lifecycle Config"], rows)
     print("")
 
