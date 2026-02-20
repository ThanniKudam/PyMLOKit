from pymlokit.platforms.wandb_api import get_current_user
from pymlokit.utils.arg_utils import generate_header


def run(credential: str, platform: str) -> None:
    print(generate_header("check", platform))

    print("")
    print(f"[*] INFO: Performing check module for {platform}")
    print("")
    print("[*] INFO: Checking credentials provided")
    print("")

    user_info = get_current_user(credential)
    
    if user_info is None:
        # We can try to print more detailed error if we want, but for now just fix the "or wandb missing" ambiguity
        try:
            import wandb
        except ImportError:
            print("[-] ERROR: The 'wandb' python library is not installed. Run `pip install wandb`.")
            print("")
            return
            
        print("[-] ERROR: Credentials provided are INVALID. Check the credentials again.")
        print("")
        return

    print("[+] SUCCESS: Credentials provided are VALID.")
    print(f"    Logged in as: {user_info.get('username', 'Unknown')}")
    if user_info.get('entity'):
        print(f"    Entity:       {user_info.get('entity')}")
    print("")
