import os

from pymlokit.platforms.clearml_api import creds_valid, download_url_bytes, get_model_url
from pymlokit.utils.arg_utils import generate_header


def run(credential: str, platform: str, api_url: str, model_id: str) -> None:
    print(generate_header("download-model", platform))

    if not api_url or not model_id:
        print("")
        print("[-] ERROR: Missing required command argument: /api-url:... or /model-id:...")
        print("")
        return

    print("")
    print(f"[*] INFO: Performing download-model module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    if not creds_valid(credential, api_url):
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print("")

    print(f"[*] INFO: Getting download URL for model {model_id}")
    url = get_model_url(credential, api_url, model_id)
    if not url:
        print(f"[-] ERROR: Could not find download URL for model {model_id} (or model does not exist)")
        print("")
        return

    print(f"[*] INFO: Found URL: {url}")
    
    # Try to download
    try:
        content = download_url_bytes(url)
    except Exception as e:
        print(f"[-] ERROR: Failed to download from URL: {e}")
        print("    (Note: ClearML may store models on S3/GS/Azure/File. PyMLOKit currently supports direct HTTP download for ClearML models, or requires specific storage credentials for cloud buckets which are not passed here.)")
        print("")
        return

    # Determine filename
    filename = url.split("?")[0].split("/")[-1] or f"{model_id}.model"
    out_path = os.path.join(os.getcwd(), filename)

    print(f"[*] INFO: Downloading to {out_path}")
    with open(out_path, "wb") as f:
        f.write(content)

    print(f"[+] SUCCESS: Downloaded model to {out_path}")
    print("")
