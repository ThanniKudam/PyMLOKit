import os
from pathlib import Path

from pymlokit.modules.sagemaker._aws import boto3_clients
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
from pymlokit.utils.table import print_table
 
 
def _parse_s3_url(s3_url: str) -> tuple[str, str]:
     s = s3_url.strip()
     if not s.startswith("s3://"):
         raise ValueError("Invalid S3 URL")
     rest = s[5:]
     bucket, _, key = rest.partition("/")
     return bucket, key
 
 
def run(credential: str, platform: str, region: str, model_id: str) -> None:
     print(generate_header("download-model", platform))
 
     if not region or not model_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing download-model module for {platform}")
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
 
     print(f"[*] INFO: Listing prefix where files will be downloaded: {prefix}")
     print("")
 
     objects = s3.list_objects_v2(Bucket=bucket, Prefix=prefix).get("Contents", [])
     out_dir = Path(os.getcwd()) / f"MLOKit-{generate_random_name()}"
     out_dir.mkdir(parents=True, exist_ok=True)
 
     for obj in objects:
         k = obj.get("Key")
         if not k or k.endswith("/"):
             continue
         rel = k[len(prefix) :] if k.startswith(prefix) else k
         out_path = out_dir / Path(rel)
         out_path.parent.mkdir(parents=True, exist_ok=True)
         body = s3.get_object(Bucket=bucket, Key=k)["Body"].read()
         out_path.write_bytes(body)
         print(f"[+] SUCCESS: {rel} written to: {out_path}")
         print("")
 
