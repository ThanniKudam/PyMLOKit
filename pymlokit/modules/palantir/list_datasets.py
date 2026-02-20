from pymlokit.platforms.palantir_api import list_datasets
from pymlokit.utils.arg_utils import generate_header
from pymlokit.utils.table import print_table
 
 
def _truncate(s: str, max_len: int) -> str:
     return s if len(s) <= max_len else (s[: max_len - 3] + "...")
 
 
def run(credential: str, platform: str) -> None:
     print("")
     print(f"[*] INFO: Performing list-datasets module for {platform}")
     print("")
 
     print(generate_header("list-datasets", platform))
 
     datasets = list_datasets(credential)
     rows = []
     for d in datasets:
         name = _truncate(str(d.get("dataset_name", "") or ""), 38)
         date_created = _truncate(str(d.get("date_created", "") or ""), 23)
         rows.append([name, d.get("type", ""), date_created, d.get("dataset_rid", "")])
 
     print_table(["Name", "Type", "Creation Date", "Dataset RID"], rows)
     print("")
     print(f"[*] INFO: Found {len(datasets)} dataset(s)")
     print("")
 
