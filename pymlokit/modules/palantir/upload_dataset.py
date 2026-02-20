import os
 
from pymlokit.platforms.palantir_api import parse_creds, upload_dataset
from pymlokit.utils.arg_utils import generate_header
 
 
def run(credential: str, platform: str, dataset_name: str, source_dir: str) -> None:
     print(generate_header("upload-dataset", platform))
 
     if not dataset_name or not source_dir:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         print("[*] INFO: Use /dataset-name:[DATASET_NAME] to specify the dataset name")
         print("[*] INFO: Use /source-dir:[LOCAL_FILE_PATH] to specify the local file to upload")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing upload-dataset module for {platform}")
     print("")
 
     if not os.path.isfile(source_dir):
         print(f"[-] ERROR: Source file does not exist: {source_dir}")
         print("")
         return
 
     print(f"[*] INFO: Uploading dataset file: {source_dir}")
     print(f"[*] INFO: Dataset name: {dataset_name}")
     print("")
 
     file_content = open(source_dir, "rb").read()
     print(f"[*] INFO: File size: {len(file_content) / 1024.0:.2f} KB")
     print("")
 
     dataset_rid = upload_dataset(credential, dataset_name, file_content, os.path.basename(source_dir))
     if not dataset_rid:
         print("[-] ERROR: Failed to upload dataset. The upload may have been rejected or there may be insufficient permissions.")
         print("")
         return
 
     print(f"[+] SUCCESS: Dataset uploaded successfully with RID: {dataset_rid}")
     print("")
 
     tenant = parse_creds(credential).tenant
     print(f"[*] INFO: Dataset available at: https://{tenant}/workspace/dataset/{dataset_rid}")
     print("")
 
