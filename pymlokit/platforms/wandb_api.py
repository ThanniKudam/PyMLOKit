from __future__ import annotations

import os
from typing import Any


def _get_api(credential: str) -> Any:
    try:
        import wandb
    except ImportError:
        # If wandb isn't installed, we can't do anything
        return None
        
    # Set env var for auth as wandb.login() might be interactive or print stuff
    # We use env var instead of wandb.login() to avoid side effects (netrc)
    # and to ensure we use the provided credential strictly.
    os.environ["WANDB_API_KEY"] = credential
    try:
        # We don't use wandb.login() as it tries to write to netrc and check format locally
        # We rely on api.viewer() to validate the key remotely
        return wandb.Api(api_key=credential)
    except Exception as e:
        # This might fail if key is invalid format (though Api usually doesn't validate strictly on init)
        raise RuntimeError(f"WandB API Init Failed: {e}")


def get_current_user(credential: str) -> dict | None:
    try:
        api = _get_api(credential)
        if api is None:
            return None
        
        # Check if viewer is callable (it usually is a method returning a dict-like object)
        viewer = api.viewer
        if callable(viewer):
            viewer = viewer()
            
        # Extract info safely
        # It might be a dict or object
        username = viewer.get("username") if isinstance(viewer, dict) else getattr(viewer, "username", str(viewer))
        entity = viewer.get("entity") if isinstance(viewer, dict) else getattr(viewer, "entity", "")
        
        return {"username": username, "entity": entity}
    except Exception as e:
        print(f"[-] DEBUG: WandB validation failed: {e}")
        return None


def creds_valid(credential: str) -> bool:
    return get_current_user(credential) is not None



def list_projects(credential: str) -> list[dict]:
    api = _get_api(credential)
    out = []
    # api.projects() returns Projects for the default entity
    for p in api.projects():
        out.append({
            "name": p.name,
            "entity": p.entity,
            "url": p.url,
            "id": getattr(p, "id", ""),
        })
    return out


def list_models(credential: str, entity: str, project: str) -> list[dict]:
    api = _get_api(credential)
    out = []
    
    # We look for Artifacts of type 'model'
    path = f"{entity}/{project}" if entity and project else project
    if not path:
        # If no project specified, we can't easily list all models across all projects efficiently
        # But we can try to list for default entity if only entity is missing?
        # api.artifact_versions() requires type and name.
        # api.projects() -> iterate -> artifact_types() -> 'model' -> collections
        return []

    # Get artifact type 'model'
    # If the project doesn't exist or we can't access it, this will likely raise an exception
    # We let it propagate to the caller which handles it
    try:
        atype = api.artifact_type("model", project=path)
        for coll in atype.collections():
            out.append({
                "name": coll.name,
                "id": coll.id,
                "type": "model",
                "description": coll.description,
                "created_at": coll.created_at,
            })
    except Exception as e:
        # If the type "model" is not found in the project, it raises a specific error
        # "Could not find artifact type 'model'" or similar
        # In this case, we just return empty list as expected.
        if "Could not find artifact type" in str(e):
            return []
        raise e
        
    return out


def list_datasets(credential: str, entity: str, project: str) -> list[dict]:
    api = _get_api(credential)
    out = []
    
    path = f"{entity}/{project}" if entity and project else project
    if not path:
        return []

    # Get artifact type 'dataset'
    try:
        atype = api.artifact_type("dataset", project=path)
        for coll in atype.collections():
            out.append({
                "name": coll.name,
                "id": coll.id,
                "type": "dataset",
                "description": coll.description,
                "created_at": coll.created_at,
            })
    except Exception as e:
        # If the type "dataset" is not found in the project, it raises a specific error
        if "Could not find artifact type" in str(e):
            return []
        raise e
        
    return out


def download_artifact(credential: str, entity: str, project: str, artifact_name: str, version: str = "latest") -> str:
    api = _get_api(credential)
    path = f"{entity}/{project}" if entity and project else project
    full_name = f"{path}/{artifact_name}:{version}"
    
    try:
        artifact = api.artifact(full_name)
        path = artifact.download()
        return str(path)
    except Exception as e:
        raise RuntimeError(f"Failed to download artifact {full_name}: {e}")
