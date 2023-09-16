import inspect
from typing import Any, List

from deeploy.enums import ExplainerType
from deeploy.services.explainers import BaseExplainer


class ExplainerWrapper:
    __explainer_helper: BaseExplainer

    def __init__(self, explainer_object: Any) -> None:
        self.__explainer_helper = self.__get_explainer_helper(explainer_object)
        return

    def save(self, local_folder_path: str) -> None:
        self.__explainer_helper.save(local_folder_path)
        return

    def get_explainer_type(self) -> ExplainerType:
        return self.__explainer_helper.get_explainer_type()

    def __get_explainer_type(self, model_object: Any) -> ExplainerType:
        base_classes = list(
            map(
                lambda x: x.__module__ + "." + x.__name__,
                inspect.getmro(type(model_object)),
            )
        )

        if self.__is_alibi_anchor_text(base_classes):
            return ExplainerType.ANCHOR_TEXT
        if self.__is_alibi_anchor_images(base_classes):
            return ExplainerType.ANCHOR_IMAGES
        if self.__is_alibi_anchor_tabular(base_classes):
            return ExplainerType.ANCHOR_TABULAR
        if self.__is_shap_kernel(base_classes):
            return ExplainerType.SHAP_KERNEL
        if self._is_pdp_or_mace_list(base_classes):
            base_classes_omni = list(
                map(
                    lambda x: x.__module__ + "." + x.__name__,
                    inspect.getmro(type(model_object[0])),
                )
            )
            if len(model_object) > 1:
                base_classes_omni_transformer = list(
                    map(
                        lambda x: x.__module__ + "." + x.__name__,
                        inspect.getmro(type(model_object[1])),
                    )
                )
                if self.__is_omni_tabular_transformer(base_classes_omni_transformer):
                    pass
                else:
                    NotImplementedError("Omni Tabular Transformer is not implemented")

            if self.__is_pdp_tabular(base_classes_omni, model_object[0]):
                return ExplainerType.PDP_TABULAR

            if self.__is_mace_tabular(base_classes_omni, model_object[0]):
                return ExplainerType.MACE_TABULAR

            raise NotImplementedError(
                "This explainer type is not implemented by Deeploy"
            )

        raise NotImplementedError("This explainer type is not implemented by Deeploy")

    def __get_explainer_helper(self, explainer_object) -> BaseExplainer:
        explainer_type = self.__get_explainer_type(explainer_object)

        # only import the helper class when it is needed
        if (
            explainer_type == ExplainerType.ANCHOR_TEXT
            or explainer_type == ExplainerType.ANCHOR_IMAGES
            or explainer_type == ExplainerType.ANCHOR_TABULAR
        ):
            from deeploy.services.explainers.alibi import AlibiExplainer

            return AlibiExplainer(explainer_object)
        if explainer_type == ExplainerType.SHAP_KERNEL:
            from deeploy.services.explainers.shap import SHAPExplainer

            return SHAPExplainer(explainer_object)
        if (
            explainer_type == ExplainerType.PDP_TABULAR
            or explainer_type == ExplainerType.MACE_TABULAR
        ):
            from deeploy.services.explainers.omni_tabular import OmniTabularExplainer

            return OmniTabularExplainer(explainer_object)

    def __is_alibi_anchor_text(self, base_classes: List[str]) -> bool:
        return "alibi.explainers.anchor_text.AnchorText" in base_classes

    def __is_alibi_anchor_images(self, base_classes: List[str]) -> bool:
        return "alibi.explainers.anchor_image.AnchorImage" in base_classes

    def __is_alibi_anchor_tabular(self, base_classes: List[str]) -> bool:
        return "alibi.explainers.anchor_tabular.AnchorTabular" in base_classes

    def __is_shap_kernel(self, base_classes: List[str]) -> bool:
        return "shap.explainers.kernel.KernelExplainer" in base_classes

    def _is_pdp_or_mace_list(self, base_classes: List[str]) -> bool:
        return "builtins.list" in base_classes

    def __is_omni_tabular_transformer(self, base_classes: List[str]) -> bool:
        return "omnixai.preprocessing.tabular.TabularTransform" in base_classes

    def __is_pdp_tabular(self, base_classes: List[str], obj) -> bool:
        return (
            "omnixai.explainers.tabular.auto.TabularExplainer" in base_classes
        ) and ("pdp" in obj.explainer_names)

    def __is_mace_tabular(self, base_classes: List[str], obj) -> bool:
        return "omnixai.explainers.tabular.auto.TabularExplainer" in base_classes and (
            "mace" in obj.explainer_names
        )
