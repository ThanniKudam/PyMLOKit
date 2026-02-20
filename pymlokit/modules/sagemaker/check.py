from pymlokit.modules.sagemaker._aws import boto3_clients
from pymlokit.utils.arg_utils import generate_header
 
 
def run(credential: str, platform: str, region: str) -> None:
     print(generate_header("check", platform))
 
     if not region:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing check module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     sm, _ = boto3_clients(credential, region)
     try:
         sm.list_models(MaxResults=1)
     except Exception:
         print("[-] ERROR: Credentials are invalid")
         print("")
         return
 
     print("[+] SUCCESS: Credentials are valid")
     print("")
 
