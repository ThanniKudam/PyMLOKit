import json
import os
import re
from pathlib import Path

from pymlokit.platforms.palantir_api import download_dataset_csv, get_dataset_details, parse_creds
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
 
 
def _sanitize_name(name: str) -> str:
     return re.sub(r'[<>:"/\\\\|?*]', "_", name)
 
 
def run(credential: str, platform: str, dataset_id: str) -> None:
     print(generate_header("download-dataset", platform))
 
     if not dataset_id:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         print("[*] INFO: Use /dataset-id:[DATASET_RID] to specify the dataset to download")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing download-dataset module for {platform}")
     print("")
 
     print(f"[*] INFO: Downloading dataset with RID {dataset_id} to the current working directory of {os.getcwd()}")
     print("")
 
     print("[*] INFO: Retrieving dataset metadata...")
     metadata_json = get_dataset_details(credential, dataset_id)
 
     dataset_name = "Unknown"
     if metadata_json:
         try:
             doc = json.loads(metadata_json)
             if isinstance(doc, dict) and doc.get("name"):
                 dataset_name = str(doc["name"])
         except Exception:
             dataset_name = "Unknown"
 
     print("[*] INFO: Downloading dataset content as CSV...")
     content = b""
     try:
         content = download_dataset_csv(credential, dataset_id)
     except Exception:
         content = b""
 
     out_dir = Path(os.getcwd()) / f"MLOKit-{generate_random_name()}"
     out_dir.mkdir(parents=True, exist_ok=True)
 
     if content:
         csv_name = f"{_sanitize_name(dataset_name)}.csv" if dataset_name != "Unknown" else "dataset.csv"
         csv_path = out_dir / csv_name
         csv_path.write_bytes(content)
         print(f"[+] SUCCESS: Dataset written to: {csv_path}")
         print(f"[*] INFO: File size: {len(content) / 1024.0:.2f} KB")
         print(f"[*] INFO: Dataset RID: {dataset_id}")
         print("")
 
         if metadata_json:
             meta_path = out_dir / "metadata.json"
             meta_path.write_text(metadata_json, encoding="utf-8")
             print(f"[+] SUCCESS: Dataset metadata written to: {meta_path}")
             print("")
         return
 
     print("[-] ERROR: Failed to download dataset content. The dataset may be empty or access may be restricted.")
     print("")
 
     if metadata_json:
         print("[*] INFO: Saving dataset metadata as fallback...")
         meta_path = out_dir / "metadata.json"
         meta_path.write_text(metadata_json, encoding="utf-8")
         print(f"[+] SUCCESS: Dataset metadata written to: {meta_path}")
         print(f"[*] INFO: Dataset RID: {dataset_id}")
         print("")
 
