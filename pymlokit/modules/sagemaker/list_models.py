from datetime import datetime
 
from pymlokit.modules.sagemaker._aws import boto3_clients
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def run(credential: str, platform: str, region: str) -> None:
     print(generate_header("list-models", platform))
 
     if not region:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing list-models module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     sm, _ = boto3_clients(credential, region)
 
     models = []
     next_token = None
     while True:
         kwargs = {"MaxResults": 100}
         if next_token:
             kwargs["NextToken"] = next_token
         resp = sm.list_models(**kwargs)
         if not models:
             print("[+] SUCCESS: Credentials are valid")
             print("")
         for m in resp.get("Models", []):
             models.append(
                 [
                     m.get("ModelName", ""),
                     (m.get("CreationTime") or "").strftime("%m/%d/%Y") if hasattr(m.get("CreationTime"), "strftime") else "",
                     m.get("ModelArn", ""),
                 ]
             )
         next_token = resp.get("NextToken")
         if not next_token:
             break
 
     print_table(["Model Name", "Creation Date", "Model ARN"], models)
     print("")
 
