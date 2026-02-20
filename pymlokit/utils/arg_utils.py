from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


def parse_arguments(args: Iterable[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for arg in args:
        parts = arg.split(":", 1)
        key_part = parts[0].lower()
        if not key_part:
            continue
        key = key_part[1:] if key_part[0] in ("/", "-") else key_part
        value = parts[1] if len(parts) == 2 else ""
        result[key] = value
    return result


def generate_header(module: str, platform: str) -> str:
    delim = "=" * 50
    return (
        f"\n{delim}\n"
        f"Module:\t\t{module}\n"
        f"Platform:\t{platform}\n"
        f"Timestamp:\t{datetime.now()}\n"
        f"{delim}\n"
    )


APPROVED_MODULES = {
    "check",
    "list-projects",
    "list-models",
    "list-datasets",
    "download-model",
    "download-dataset",
    "upload-dataset",
    "poison-model",
    "list-notebooks",
    "add-notebook-trigger",
}


def help_me() -> None:
    print("\nPyMLOKit CLI (pymlokit)\n")
    print("Usage:")
    print("  pymlokit <module> /platform:<platform> /credential:<credential> [options...]\n")
    print("Arguments:")
    print("  /platform:<platform>    One of: azureml, bigml, vertexai, mlflow, sagemaker, palantir, clearml, wandb, metaflow, zenml, kubeflow")
    print("  /credential:<value>     Platform-specific credential string\n")
    print("Modules:")
    print("  " + ", ".join(sorted(APPROVED_MODULES)) + "\n")
    print("Help:")
    print("  pymlokit --help")
    print("  pymlokit <module> --help\n")
    print("Examples:")
    print("  pymlokit check /platform:bigml /credential:USERNAME;APIKEY")
    print("  pymlokit list-models /platform:mlflow /credential:USERNAME;PASSWORD /url:http://localhost:5000")
    print("  pymlokit check /platform:clearml /credential:ACCESS_KEY;SECRET_KEY /api-url:https://api.clear.ml")
    print("  pymlokit list-projects /platform:wandb /credential:API_KEY")
    print("  pymlokit list-projects /platform:metaflow /credential:dummy /service-url:http://localhost:8080")
    print("  pymlokit check /platform:zenml /credential:username:password /api-url:http://localhost:8080/api/v1")
    print("")
    print("Common options by platform:")
    print("  azureml:   /subscription-id /region /resource-group /workspace /model-id /dataset-id /source-dir")
    print("  bigml:     /model-id /dataset-id")
    print("  vertexai:  /project /model-id /dataset-id")
    print("  mlflow:    /url /model-id")
    print("  sagemaker: /region /model-id /source-dir /notebook-name /script")
    print("  palantir:  /dataset-id /dataset-name /source-dir")
    print("  clearml:   /api-url /project-id /model-id")
    print("  wandb:     /project /model-id /dataset-id (use entity/project format)")
    print("  metaflow:  /service-url /project (flow_id)")
    print("  zenml:     /api-url")
    print("  kubeflow:  /api-url")
    print("")
    print("Notes:")
    print("  - Argument format follows the original tool: /key:value (or -key:value).")
    print("  - For full details and platform credential formats, see README_PYTHON.md.")
    print("")


@dataclass(frozen=True)
class ParsedCli:
    module: str
    credential: str
    platform: str
    options: dict[str, str]
