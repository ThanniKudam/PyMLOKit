## Usage 

General syntax:
```bash
pymlokit <module> /platform:<platform> /credential:<credential> [options...]
```

### Examples

**ClearML**
```bash
pymlokit check /platform:clearml /credential:ACCESS_KEY;SECRET_KEY /api-url:https://api.clear.ml
pymlokit list-projects /platform:clearml /credential:ACCESS_KEY;SECRET_KEY /api-url:https://api.clear.ml
pymlokit list-models /platform:clearml /credential:ACCESS_KEY;SECRET_KEY /api-url:https://api.clear.ml /project-id:PROJECT_ID
pymlokit download-model /platform:clearml /credential:ACCESS_KEY;SECRET_KEY /api-url:https://api.clear.ml /model-id:MODEL_ID
```

**Weights & Biases (WandB)**
```bash
# Requires `pip install wandb`
pymlokit check /platform:wandb /credential:API_KEY
pymlokit list-projects /platform:wandb /credential:API_KEY
pymlokit list-models /platform:wandb /credential:API_KEY /project:entity/project_name
pymlokit download-model /platform:wandb /credential:API_KEY /project:entity/project_name /model-id:artifact_name:version
```

**Metaflow**
```bash
pymlokit list-projects /platform:metaflow /credential:dummy /service-url:http://localhost:8080
pymlokit list-models /platform:metaflow /credential:dummy /service-url:http://localhost:8080 /project:FlowName
```

**ZenML**
```bash
pymlokit check /platform:zenml /credential:username:password /api-url:http://localhost:8080/api/v1
pymlokit list-projects /platform:zenml /credential:TOKEN /api-url:http://localhost:8080/api/v1
```

**Kubeflow**
```bash
pymlokit list-projects /platform:kubeflow /credential:BearerToken /api-url:http://kubeflow-gateway/pipeline
pymlokit list-models /platform:kubeflow /credential:BearerToken /api-url:http://kubeflow-gateway/pipeline
```

## Modules

- `check`: Validate credentials and connectivity.
- `list-projects`: List projects/workspaces/flows.
- `list-models`: List models/runs/artifacts.
- `list-datasets`: List datasets (where applicable).
- `download-model`: Download a model artifact.
- `download-dataset`: Download a dataset artifact.
- `poison-model`: (SageMaker/AzureML) Inject code into model artifacts.
- `add-notebook-trigger`: (SageMaker) Add malicious lifecycle config.
- `upload-dataset`: (Palantir) Upload malicious dataset.
