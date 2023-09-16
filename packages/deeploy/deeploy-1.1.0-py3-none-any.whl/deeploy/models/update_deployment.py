from typing import Any, Dict, Optional

from pydantic import BaseModel


class UpdateDeployment(BaseModel):
    """Class that contains the options for updating a model"""  # noqa

    deployment_id: Optional[str]
    repository_id: Optional[str]
    status: Optional[str]
    branch_name: Optional[str]
    commit: Optional[str]
    commit_message: Optional[str]
    contract_path: Optional[str]
    deployment_backend: Optional[str]
    model_type: Optional[Any]
    model_serverless: Optional[bool] = False
    model_instance_type: Optional[str]
    model_cpu_limit: Optional[float]
    model_cpu_request: Optional[float]
    model_mem_limit: Optional[int]
    model_mem_request: Optional[int]
    explainer_type: Optional[Any]
    explainer_serverless: Optional[bool] = False
    explainer_instance_type: Optional[str]
    explainer_cpu_limit: Optional[float]
    explainer_cpu_request: Optional[float]
    explainer_mem_limit: Optional[int]
    explainer_mem_request: Optional[int]
    transformer_type: Optional[Any]
    transformer_serverless: Optional[bool] = False
    transformer_instance_type: Optional[str]
    transformer_cpu_limit: Optional[float]
    transformer_cpu_request: Optional[float]
    transformer_mem_limit: Optional[int]
    transformer_mem_request: Optional[int]

    def to_request_body(self) -> Dict:
        request_body = {
            "id": self.deployment_id,
            "repositoryId": self.repository_id,
            "status": self.status,
            "branchName": self.branch_name,
            "commit": self.commit,
            "commitMessage": self.commit_message,
            "contractPath": self.contract_path,
            "deploymentBackend": self.deployment_backend,
            "modelType": self.model_type,
            "modelServerless": self.model_serverless,
            "modelInstanceType": self.model_instance_type,
            "modelCpuLimit": self.model_cpu_limit,
            "modelCpuRequest": self.model_cpu_request,
            "modelMemLimit": self.model_mem_limit,
            "modelMemRequest": self.model_mem_request,
            "explainerType": self.explainer_type,
            "explainerServerless": self.explainer_serverless,
            "explainerInstanceType": self.explainer_instance_type,
            "explainerCpuLimit": self.explainer_cpu_limit,
            "explainerCpuRequest": self.explainer_cpu_request,
            "explainerMemLimit": self.explainer_mem_limit,
            "explainerMemRequest": self.explainer_mem_request,
            "transformerType": self.transformer_type,
            "transformerServerless": self.transformer_serverless,
            "transformerInstanceType": self.transformer_instance_type,
            "transformerCpuLimit": self.transformer_cpu_limit,
            "transformerCpuRequest": self.transformer_cpu_request,
            "transformerMemLimit": self.transformer_mem_limit,
            "transformerMemRequest": self.transformer_mem_request,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        return {k: v for k, v in request_body.items() if v is not None and v != {}}


class UpdateDeploymentMetadata(BaseModel):
    """Class that contains the options for updating a model that doesn't require restarting pods"""  # noqa

    deployment_id: Optional[str]
    name: Optional[str]
    description: Optional[str]
    owner_id: Optional[str]
    has_example_input: Optional[bool]
    example_input: Optional[dict]
    example_output: Optional[Any]
    input_tensor_size: Optional[str]
    output_tensor_size: Optional[str]
    kserve_id: Optional[str]
    public_url: Optional[str]
    status: Optional[str]
    stateConfig: Optional[dict]
    tags: Optional[dict]

    def to_request_body(self) -> Dict:
        request_body = {
            "id": self.deployment_id,
            "name": self.name,
            "ownerId": self.owner_id,
            "description": self.description,
            "hasExampleInput": self.has_example_input,
            "exampleInput": self.example_input,
            "exampleOutput": self.example_output,
            "inputTensorSize": self.input_tensor_size,
            "outputTensorSize": self.output_tensor_size,
            "kserveId": self.kserve_id,
            "publicURL": self.public_url,
            "status": self.status,
            "stateConfig": self.stateConfig,
            "tags": self.tags,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        return {k: v for k, v in request_body.items() if v is not None and v != {}}
