import os
from pathlib import Path

from pymlokit.platforms.mlflow_api import (
     creds_valid,
     download_artifact,
     get_artifact_root_dir,
     list_artifacts_recursive,
     list_models,
 )
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
 
 
def run(credential: str, platform: str, url: str, model_id: str) -> None:
     print(generate_header("download-model", platform))
 
     print("")
     print(f"[*] INFO: Performing download-model module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not url or not model_id:
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     if not creds_valid(credential, url):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     models = list_models(credential, url)
     target = None
     for m in models:
         if str(m.get("name", "")).lower() == model_id.lower():
             target = m
             break
     if not target:
         return
 
     run_id = str(target.get("run_id", "") or "")
     if not run_id:
         return
 
     directory = get_artifact_root_dir(credential, url, run_id)
     artifact_list = list_artifacts_recursive(credential, url, run_id, directory) if directory else []
 
     if artifact_list:
         print_table_header = False
         if not print_table_header:
             print(f"{'Artifact':>60}")
             print("-" * 60)
         for a in artifact_list:
             print(f"{str(a.get('path','')):>60}")
         print("")
         print("")
 
     out_dir = Path(os.getcwd()) / f"MLOKit-{generate_random_name()}"
     out_dir.mkdir(parents=True, exist_ok=True)
 
     for a in artifact_list:
         path = str(a.get("path", "") or "")
         if not path:
             continue
         print("")
         print(f"[*] INFO: Downloading {path}")
         print("")
         content = download_artifact(credential, url, run_id, path)
         out_path = out_dir / Path(path)
         out_path.parent.mkdir(parents=True, exist_ok=True)
         out_path.write_bytes(content)
         print(f"[+] SUCCESS: {path} written to: {out_dir}")
         print("")
 
