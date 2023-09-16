from deeploy.enums import ModelType

from . import BaseModel


class TritonModel(BaseModel):
    # TODO
    def save(self, local_folder_path: str) -> None:
        return

    def get_model_type(self) -> ModelType:
        return ModelType.TRITON
