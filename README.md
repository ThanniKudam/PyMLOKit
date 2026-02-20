# PyMLOKit

**PyMLOKit** is a comprehensive, open-source **MLOps Attack Toolkit** written in Python. It is designed to help security researchers and red teamers assess the security posture of MLOps environments by interacting with their APIs to enumerate resources, verify credentials, and simulate attack paths (e.g., model theft, poisoning, data exfiltration).

## Credits & Origins

This project is a **Python port and extension** of the original [MLOKit](https://github.com/xforcered/MLOKit) tool, which was written in C#.

**Huge thanks to the original author:**
*   **h4wkst3r** ([@h4wkst3r on X](https://x.com/h4wkst3r?lang=en))

While the original tool pioneered the concept of an MLOps attack toolkit for platforms like AzureML and SageMaker, **PyMLOKit** extends this capability to a wider ecosystem of modern MLOps platforms commonly used in the industry today.

## Features & Supported Platforms

PyMLOKit supports a unified CLI interface for interacting with **11+ MLOps platforms**.

### Original Platforms (from MLOKit)
*   **Azure Machine Learning** (`azureml`)
*   **Amazon SageMaker** (`sagemaker`)
*   **Google Vertex AI** (`vertexai`)
*   **MLFlow** (`mlflow`)
*   **BigML** (`bigml`)
*   **Palantir Foundry** (`palantir`)

### New Platforms (Exclusive to PyMLOKit)
*   **Weights & Biases** (`wandb`) - *Added in this edition*
*   **ClearML** (`clearml`) - *Added in this edition*
*   **ZenML** (`zenml`) - *Added in this edition*
*   **Metaflow** (`metaflow`) - *Added in this edition*
*   **Kubeflow Pipelines** (`kubeflow`) - *Added in this edition*

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/PyMLOKit.git
cd PyMLOKit

# Install dependencies and the tool in editable mode
pip install -e .

# Verify installation
pymlokit --help
```

## Usage

The CLI follows a consistent syntax across all platforms:

```bash
pymlokit <module> /platform:<platform_name> /credential:<auth_string> [options...]
```

### Available Modules
*   `check`: Verify if credentials are valid.
*   `list-projects`: Enumerate projects, workspaces, or experiments.
*   `list-models`: List registered models and artifacts.
*   `list-datasets`: List training datasets.
*   `download-model`: Exfiltrate a model artifact.
*   `download-dataset`: Exfiltrate a dataset.
*   `poison-model`: Inject malicious code into model files (supported platforms only).
*   `add-notebook-trigger`: Add malicious lifecycle configurations (SageMaker).

### Platform Arguments Guide

| Platform | Key | Credential Format | Key Options |
| :--- | :--- | :--- | :--- |
| **Azure ML** | `azureml` | CLI Token / SP Secret | `/subscription-id`, `/resource-group`, `/workspace` |
| **SageMaker** | `sagemaker` | `ACCESS;SECRET;SESSION` | `/region`, `/notebook-name` |
| **Vertex AI** | `vertexai` | Path to JSON Key | `/project` |
| **MLFlow** | `mlflow` | `USER;PASS` | `/url` |
| **WandB** | `wandb` | `API_KEY` | `/project` (entity/project) |
| **ClearML** | `clearml` | `ACCESS;SECRET` | `/api-url`, `/project-id` |
| **ZenML** | `zenml` | `USER:PASS` or `TOKEN` | `/api-url` |
| **Metaflow** | `metaflow` | `dummy` (or auth token) | `/service-url` |
| **Kubeflow** | `kubeflow` | `BearerToken` | `/api-url` |

## Examples

### Checking Credentials (WandB)
```bash
pymlokit check /platform:wandb /credential:"YOUR_API_KEY"
```

### Listing Models (ClearML)
```bash
pymlokit list-models /platform:clearml /credential:"ACCESS_KEY;SECRET_KEY" /api-url:"https://api.clear.ml" /project-id:"PROJECT_ID"
```

### Exfiltrating a Model (MLFlow)
```bash
pymlokit download-model /platform:mlflow /credential:"user;password" /url:"http://mlflow-server:5000" /model-id:"models:/MyModel/1"
```

### Enumerating Projects (Metaflow)
```bash
pymlokit list-projects /platform:metaflow /credential:"dummy" /service-url:"http://localhost:8080"
```

PEACE!