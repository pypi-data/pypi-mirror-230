from typing import Any, List, Optional

from pydantic import BaseModel


class CreateVersion(BaseModel):
    """ """

    repository_id: Optional[str]
    branch_name: Optional[str]
    commit: Optional[str]
    commit_message: Optional[str]
    contract_path: Optional[str]
    has_example_input: Optional[bool]
    example_input: Optional[List[Any]]
    example_output: Optional[Any]
    input_tensor_size: Optional[str]
    output_tensor_size: Optional[str]
    model_type: Optional[Any]
    model_serverless: Optional[bool] = False
    explainer_type: Optional[Any]
    explainer_serverless: Optional[bool] = False
    transformer_type: Optional[Any]
    transformer_serverless: Optional[bool] = False
