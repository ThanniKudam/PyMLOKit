import os
 
from pymlokit.platforms.vertexai_api import (
     creds_valid,
     download_media_link,
     get_media_link,
     list_datasets,
     list_regions,
     parse_gs_uri,
 )
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
 
 
def run(credential: str, platform: str, project: str, dataset_id: str) -> None:
     print(generate_header("download-dataset", platform))
 
     if not project or not dataset_id:
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
 
     print(f"[*] INFO: Getting all regions for the {project} project")
     print("")
     regions = list_regions(credential, project)
 
     target = None
     for r in regions:
         for d in list_datasets(credential, r, project):
             if str(d.get("id", "")).lower() == dataset_id.lower():
                 target = d
                 break
         if target:
             break
 
     if not target:
         return
 
     bucket, obj = parse_gs_uri(str(target.get("uri", "") or ""))
     print(f"[*] INFO: Getting mediaLink for gs://{bucket}/{obj}")
     print("")
     media_link = get_media_link(credential, bucket, obj)
     if not media_link:
         return
 
     content = download_media_link(credential, media_link)
     file_name = f"MLOKit-{generate_random_name()}"
     out_path = os.path.join(os.getcwd(), file_name)
     with open(out_path, "wb") as f:
         f.write(content)
 
     print(f"[+] SUCCESS: Dataset written to: {out_path}")
     print("")
 
