from __future__ import annotations

import sys
from pymlokit.utils.arg_utils import APPROVED_MODULES, help_me, parse_arguments


def _get_opt(options: dict[str, str], key: str) -> str:
    return options.get(key, "")


def _dispatch(
    module: str,
    platform: str,
    credential: str,
    options: dict[str, str],
) -> None:
    platform_l = platform.lower()
    module_l = module.lower()

    if platform_l == "azureml":
        if module_l == "check":
            from pymlokit.modules.azureml.check import run

            run(credential, platform_l)
            return
        if module_l == "list-projects":
            from pymlokit.modules.azureml.list_projects import run

            run(credential, platform_l, _get_opt(options, "subscription-id"))
            return
        if module_l == "list-models":
            from pymlokit.modules.azureml.list_models import run

            run(
                credential,
                platform_l,
                _get_opt(options, "subscription-id"),
                _get_opt(options, "region"),
                _get_opt(options, "resource-group"),
                _get_opt(options, "workspace"),
            )
            return
        if module_l == "list-datasets":
            from pymlokit.modules.azureml.list_datasets import run

            run(
                credential,
                platform_l,
                _get_opt(options, "subscription-id"),
                _get_opt(options, "region"),
                _get_opt(options, "resource-group"),
                _get_opt(options, "workspace"),
            )
            return
        if module_l == "download-model":
            from pymlokit.modules.azureml.download_model import run

            run(
                credential,
                platform_l,
                _get_opt(options, "subscription-id"),
                _get_opt(options, "region"),
                _get_opt(options, "resource-group"),
                _get_opt(options, "workspace"),
                _get_opt(options, "model-id"),
            )
            return
        if module_l == "download-dataset":
            from pymlokit.modules.azureml.download_dataset import run

            run(
                credential,
                platform_l,
                _get_opt(options, "subscription-id"),
                _get_opt(options, "region"),
                _get_opt(options, "resource-group"),
                _get_opt(options, "workspace"),
                _get_opt(options, "dataset-id"),
            )
            return
        if module_l == "poison-model":
            from pymlokit.modules.azureml.poison_model import run

            run(
                credential,
                platform_l,
                _get_opt(options, "subscription-id"),
                _get_opt(options, "region"),
                _get_opt(options, "resource-group"),
                _get_opt(options, "workspace"),
                _get_opt(options, "model-id"),
                _get_opt(options, "source-dir"),
            )
            return

    if platform_l == "bigml":
        if module_l == "check":
            from pymlokit.modules.bigml.check import run

            run(credential, platform_l)
            return
        if module_l == "list-projects":
            from pymlokit.modules.bigml.list_projects import run

            run(credential, platform_l)
            return
        if module_l == "list-models":
            from pymlokit.modules.bigml.list_models import run

            run(credential, platform_l)
            return
        if module_l == "list-datasets":
            from pymlokit.modules.bigml.list_datasets import run

            run(credential, platform_l)
            return
        if module_l == "download-model":
            from pymlokit.modules.bigml.download_model import run

            run(credential, platform_l, _get_opt(options, "model-id"))
            return
        if module_l == "download-dataset":
            from pymlokit.modules.bigml.download_dataset import run

            run(credential, platform_l, _get_opt(options, "dataset-id"))
            return

    if platform_l == "vertexai":
        if module_l == "check":
            from pymlokit.modules.vertexai.check import run

            run(credential, platform_l)
            return
        if module_l == "list-projects":
            from pymlokit.modules.vertexai.list_projects import run

            run(credential, platform_l)
            return
        if module_l == "list-models":
            from pymlokit.modules.vertexai.list_models import run

            run(credential, platform_l, _get_opt(options, "project"))
            return
        if module_l == "list-datasets":
            from pymlokit.modules.vertexai.list_datasets import run

            run(credential, platform_l, _get_opt(options, "project"))
            return
        if module_l == "download-model":
            from pymlokit.modules.vertexai.download_model import run

            run(credential, platform_l, _get_opt(options, "project"), _get_opt(options, "model-id"))
            return
        if module_l == "download-dataset":
            from pymlokit.modules.vertexai.download_dataset import run

            run(credential, platform_l, _get_opt(options, "project"), _get_opt(options, "dataset-id"))
            return

    if platform_l == "mlflow":
        if module_l == "check":
            from pymlokit.modules.mlflow.check import run

            run(credential, platform_l, _get_opt(options, "url"))
            return
        if module_l == "list-models":
            from pymlokit.modules.mlflow.list_models import run

            run(credential, platform_l, _get_opt(options, "url"))
            return
        if module_l == "download-model":
            from pymlokit.modules.mlflow.download_model import run

            run(credential, platform_l, _get_opt(options, "url"), _get_opt(options, "model-id"))
            return

    if platform_l == "sagemaker":
        if module_l == "check":
            from pymlokit.modules.sagemaker.check import run

            run(credential, platform_l, _get_opt(options, "region"))
            return
        if module_l == "list-models":
            from pymlokit.modules.sagemaker.list_models import run

            run(credential, platform_l, _get_opt(options, "region"))
            return
        if module_l == "list-notebooks":
            from pymlokit.modules.sagemaker.list_notebooks import run

            run(credential, platform_l, _get_opt(options, "region"))
            return
        if module_l == "download-model":
            from pymlokit.modules.sagemaker.download_model import run

            run(credential, platform_l, _get_opt(options, "region"), _get_opt(options, "model-id"))
            return
        if module_l == "poison-model":
            from pymlokit.modules.sagemaker.poison_model import run

            run(
                credential,
                platform_l,
                _get_opt(options, "region"),
                _get_opt(options, "model-id"),
                _get_opt(options, "source-dir"),
            )
            return
        if module_l == "add-notebook-trigger":
            from pymlokit.modules.sagemaker.add_notebook_trigger import run

            run(
                credential,
                platform_l,
                _get_opt(options, "region"),
                _get_opt(options, "notebook-name"),
                _get_opt(options, "script"),
            )
            return

    if platform_l == "palantir":
        if module_l == "check":
            from pymlokit.modules.palantir.check import run

            run(credential, platform_l)
            return
        if module_l == "list-datasets":
            from pymlokit.modules.palantir.list_datasets import run

            run(credential, platform_l)
            return
        if module_l == "download-dataset":
            from pymlokit.modules.palantir.download_dataset import run

            run(credential, platform_l, _get_opt(options, "dataset-id"))
            return
        if module_l == "upload-dataset":
            from pymlokit.modules.palantir.upload_dataset import run

            run(credential, platform_l, _get_opt(options, "dataset-name"), _get_opt(options, "source-dir"))
            return

    if platform_l == "clearml":
        if module_l == "check":
            from pymlokit.modules.clearml.check import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return
        if module_l == "list-projects":
            from pymlokit.modules.clearml.list_projects import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return
        if module_l == "list-models":
            from pymlokit.modules.clearml.list_models import run

            run(credential, platform_l, _get_opt(options, "api-url"), _get_opt(options, "project-id"))
            return
        if module_l == "list-datasets":
            from pymlokit.modules.clearml.list_datasets import run

            run(credential, platform_l, _get_opt(options, "api-url"), _get_opt(options, "project-id"))
            return
        if module_l == "download-model":
            from pymlokit.modules.clearml.download_model import run

            run(credential, platform_l, _get_opt(options, "api-url"), _get_opt(options, "model-id"))
            return

    if platform_l == "wandb":
        if module_l == "check":
            from pymlokit.modules.wandb.check import run

            run(credential, platform_l)
            return
        if module_l == "list-projects":
            from pymlokit.modules.wandb.list_projects import run

            run(credential, platform_l)
            return
        if module_l == "list-models":
            from pymlokit.modules.wandb.list_models import run

            run(credential, platform_l, _get_opt(options, "project"))
            return
        if module_l == "list-datasets":
            from pymlokit.modules.wandb.list_datasets import run

            run(credential, platform_l, _get_opt(options, "project"))
            return
        if module_l == "download-model":
            from pymlokit.modules.wandb.download_model import run

            run(credential, platform_l, _get_opt(options, "project"), _get_opt(options, "model-id"))
            return
        if module_l == "download-dataset":
            from pymlokit.modules.wandb.download_dataset import run

            run(credential, platform_l, _get_opt(options, "project"), _get_opt(options, "dataset-id"))
            return

    if platform_l == "metaflow":
        if module_l == "check":
            from pymlokit.modules.metaflow.check import run

            run(credential, platform_l, _get_opt(options, "service-url"))
            return
        if module_l == "list-projects":
            from pymlokit.modules.metaflow.list_projects import run

            run(credential, platform_l, _get_opt(options, "service-url"))
            return
        if module_l == "list-models":
            from pymlokit.modules.metaflow.list_models import run

            run(credential, platform_l, _get_opt(options, "service-url"), _get_opt(options, "project"))
            return

    if platform_l == "zenml":
        if module_l == "check":
            from pymlokit.modules.zenml.check import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return
        if module_l == "list-projects":
            from pymlokit.modules.zenml.list_projects import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return

    if platform_l == "kubeflow":
        if module_l == "check":
            from pymlokit.modules.kubeflow.check import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return
        if module_l == "list-projects":
            from pymlokit.modules.kubeflow.list_projects import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return
        if module_l == "list-models":
            from pymlokit.modules.kubeflow.list_models import run

            run(credential, platform_l, _get_opt(options, "api-url"))
            return

    print("")
    print(f"[-] ERROR: That module is not supported for {platform_l}. Please see README")
    print("")


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        help_me()
        return

    if argv[0] in ("-h", "--help", "/h", "/help", "help"):
        help_me()
        return

    module = argv[0].lower()
    options = parse_arguments(argv[1:])

    if "help" in options:
        help_me()
        return

    if module not in APPROVED_MODULES:
        print("")
        print("[-] ERROR: Invalid module given. Use pymlokit --help to see approved modules.")
        return

    if "platform" not in options:
        print("")
        print("[-] ERROR: Must supply a platform. Use pymlokit --help for syntax.")
        return
    if "credential" not in options:
        print("")
        print("[-] ERROR: Must supply both a module and credential. Use pymlokit --help for syntax.")
        return

    try:
        _dispatch(module, options["platform"], options["credential"], options)
    except Exception as ex:
        print("")
        print(f"[-] ERROR : {ex}")
