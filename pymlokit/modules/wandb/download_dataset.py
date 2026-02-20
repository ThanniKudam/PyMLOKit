import os

from pymlokit.platforms.wandb_api import creds_valid, download_artifact
from pymlokit.utils.arg_utils import generate_header


def run(credential: str, platform: str, project: str, dataset_id: str) -> None:
    print(generate_header("download-dataset", platform))

    if not project or not dataset_id:
        print("")
        print("[-] ERROR: Missing required command argument: /project:... or /dataset-id:...")
        print("    (Format: entity/project or just project. Dataset ID is artifact name)")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing download-dataset module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    entity = ""
    proj_name = project
    if "/" in project:
        parts = project.split("/", 1)
        entity = parts[0]
        proj_name = parts[1]

    # dataset_id is usually "name:version" or just "name" (latest)
    artifact_name = dataset_id
    version = "latest"
    if ":" in dataset_id:
        parts = dataset_id.split(":", 1)
        artifact_name = parts[0]
        version = parts[1]

    print(f"[*] INFO: Downloading artifact {artifact_name}:{version} from {project}")
    try:
        path = download_artifact(credential, entity, proj_name, artifact_name, version)
        print(f"[+] SUCCESS: Downloaded artifact to {path}")
    except Exception as e:
        print(f"[-] ERROR: Failed to download artifact: {e}")
        print("")
