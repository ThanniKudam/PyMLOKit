import os
from pathlib import Path
from urllib.parse import urlparse
 
from pymlokit.platforms.azureml_api import (
     creds_valid,
     download_url_bytes,
     get_asset_prefixes,
     get_content_uris,
     get_model,
 )
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
from pymlokit.utils.table import print_table
 
 
def _file_name_from_url(url: str) -> str:
     p = urlparse(url)
     name = p.path.rsplit("/", 1)[-1]
     return name or "artifact"
 
 
def run(
     credential: str,
     platform: str,
     subscription_id: str,
     region: str,
     resource_group: str,
     workspace: str,
     model_id: str,
 ) -> None:
     print(generate_header("download-model", platform))
 
     if not subscription_id or not region or not resource_group or not workspace or not model_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing download-model module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     if not creds_valid(credential):
         print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
         print("")
         return
 
     print("[+] SUCCESS: Credentials provided are VALID.")
     print("")
 
     model = get_model(credential, subscription_id, region, resource_group, workspace, model_id)
     if not model:
         return
 
     print_table(
         ["Name", "Model ID", "Model Type", "Creation Time", "Update Time"],
         [[model["name"], model_id, model["model_type"], model["created_time"], model["modified_time"]]],
     )
     print("")
 
     asset_id = str(model.get("asset_id", "") or "")
     prefixes = get_asset_prefixes(credential, subscription_id, region, resource_group, workspace, asset_id) if asset_id else []
     content_uris: list[str] = []
     for p in prefixes:
         content_uris.extend(get_content_uris(credential, subscription_id, region, resource_group, workspace, p))
 
     out_dir = Path(os.getcwd()) / f"MLOKit-{generate_random_name()}"
     out_dir.mkdir(parents=True, exist_ok=True)
 
     for u in content_uris:
         file_name = _file_name_from_url(u)
         data = download_url_bytes(u)
         (out_dir / file_name).write_bytes(data)
 
     print(f"[+] SUCCESS: Model written to: {out_dir}")
     print("")
 
