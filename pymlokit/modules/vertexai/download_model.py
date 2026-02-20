import os
from pathlib import Path

from pymlokit.platforms.vertexai_api import (
     creds_valid,
     download_media_link,
     export_model,
     get_media_link,
     list_buckets,
     list_models,
     list_objects,
     list_regions,
     parse_gs_uri,
     wait_for_export,
 )
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
 
 
def run(credential: str, platform: str, project: str, model_id: str) -> None:
     print(generate_header("download-model", platform))
 
     if not project or not model_id:
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
         for m in list_models(credential, r, project):
             if str(m.get("id", "")).lower() == model_id.lower():
                 target = m
                 break
         if target:
             break
 
     if not target:
         return
 
     export_fmt = str(target.get("exportable_format", "") or "")
     region = str(target.get("region", "") or "")
 
     print(f"[*] INFO: Getting all buckets for the {project} project")
     print("")
     buckets = list_buckets(credential, project)
 
     artifact_uri = ""
     for b in buckets:
         artifact_uri = export_model(credential, region, project, model_id, b, export_fmt)
         if artifact_uri:
             break
 
     if not artifact_uri:
         return
 
     wait_for_export(15.0)
 
     bucket, prefix = parse_gs_uri(artifact_uri)
     prefix = prefix.strip("/")
     if prefix:
         prefix = prefix + "/"
 
     object_names = list_objects(credential, bucket, prefix)
 
     out_dir = Path(os.getcwd()) / f"MLOKit-{generate_random_name()}"
     out_dir.mkdir(parents=True, exist_ok=True)
 
     for name in object_names:
         if not name or name.endswith("/"):
             continue
         media_link = get_media_link(credential, bucket, name)
         if not media_link:
             continue
         content = download_media_link(credential, media_link)
         rel = name[len(prefix) :] if prefix and name.startswith(prefix) else name
         out_path = out_dir / Path(rel)
         out_path.parent.mkdir(parents=True, exist_ok=True)
         out_path.write_bytes(content)
 
     print(f"[+] SUCCESS: Model written to: {out_dir}")
     print("")
 
