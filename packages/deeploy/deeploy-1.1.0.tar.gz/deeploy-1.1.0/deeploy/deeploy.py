import json
import logging
import os
import shutil
import uuid
from typing import Any, List, Tuple

from git import Repo
from pydantic import parse_obj_as

from deeploy.common.functions import (
    delete_all_contents_in_directory,
    directory_empty,
    directory_exists,
    file_exists,
)
from deeploy.enums import ExplainerType, ModelType, TransformerType
from deeploy.models import (
    ClientConfig,
    CreateDeployment,
    Deployment,
    DeployOptions,
    ModelReferenceJson,
    PredictionLog,
    UpdateDeployment,
    UpdateDeploymentMetadata,
    UpdateOptions,
    V1Prediction,
    V2Prediction,
)
from deeploy.models.model_reference_json import BlobReference, DockerReference
from deeploy.models.prediction_log import RequestLog
from deeploy.services import DeeployService, ExplainerWrapper, GitService, ModelWrapper


class Client(object):
    """
    A class for interacting with Deeploy
    """

    __config: ClientConfig

    def __init__(
        self,
        host: str,
        workspace_id: str,
        access_key: str = None,
        secret_key: str = None,
        deployment_token: str = None,
        branch_name: str = None,
        team_id: str = None,
    ) -> None:
        """Initialise the Deeploy client
        Parameters:
            host (str): The host at which Deeploy is located, i.e. deeploy.example.com
            workspace_id (str): The ID of the workspace in which your repository
                is located
            access_key (str): Personal Access Key generated from the Deeploy UI
            secret_key (str): Secret Access Key generated from the Deeploy UI
            token (str): Deployment token generated from the Deeploy UI
            branch_name (str, optional): The banchname on which to commit new models.
                Defaults to the current branchname.
            team_id (str, optional): Initialize the client for a team ID, needed for app.deeploy.ml.
        """

        self.__config = ClientConfig(
            **{
                "access_key": access_key,
                "secret_key": secret_key,
                "token": deployment_token,
                "host": host,
                "workspace_id": workspace_id,
                "branch_name": branch_name,
                "repository_id": "",
                "team_id": team_id,
            }
        )

        self.__deeploy_service = DeeployService(
            host, workspace_id, access_key, secret_key, deployment_token, team_id
        )

        return

    def deploy(
        self,
        options: DeployOptions,
        local_repository_path: str,
        model: Any = None,
        explainer: Any = None,
        model_type: int = None,
        explainer_type: int = None,
        transformer_type: int = None,
        overwrite_contract: bool = False,
        overwrite_metadata: bool = False,
        commit_message: str = None,
        contract_path: str = "",
    ) -> Deployment:
        """Deploy a model on Deeploy
        Parameters:
            model (Any): The class instance of an ML model
            options (DeployOptions): An instance of the deploy options class
                containing the deployment options
            local_repository_path (str): Absolute path to the local git repository
                which is connected to Deeploy
            explainer (Any, optional): The class instance of an optional model explainer
            model_type (int, optional): model type enum from ModelType class
            explainer_type (int, optional): explainer type enum from ExplainerType class
            transformer_type (int, optional): transformer type enum from TransformerType class
            overwrite_contract (bool, optional): Whether or not to overwrite files that are in the
                'model' and 'explainer' folders in the git folder. Defaults to False
            overwrite_metadata (bool, optional): Whether or not to overwrite the metadata.json
                file. Defaults to False.
            commit_message (str, optional): Commit message to use
            contract_path (str, optional): Relative repository subpath that contains the
                Deeploy contract to deploy from
        """
        commit = False

        if not (self.__config.access_key and self.__config.secret_key):
            raise Exception("Missing access credentials to create deployment.")

        git_service = GitService(local_repository_path)

        repository_in_workspace, repository_id = self.__is_git_repository_in_workspace(
            git_service
        )

        if not repository_in_workspace:
            raise Exception(
                "Repository was not found in the Deeploy workspace. \
                 Make sure you have connected it before."
            )
        else:
            self.__config.repository_id = repository_id

        logging.info("Pulling from the remote repository...")
        git_service.pull()
        logging.info("Successfully pulled from the remote repository.")

        if model:
            model_type = self.__process_model(
                model,
                options,
                local_repository_path,
                git_service,
                overwrite_contract,
                contract_path,
            ).value
            commit = True
        elif options.model_docker_config or options.model_blob_config:
            self.__prepare_directory(
                "model", git_service, local_repository_path, contract_path, overwrite_contract
            )
            model_folder = os.path.join(local_repository_path, contract_path, "model")
            shutil.rmtree(model_folder)
            os.mkdir(model_folder)
            if options.model_docker_config:
                model_type = ModelType.CUSTOM.value
                self.__create_reference_file(
                    model_folder, dockerReference=options.model_docker_config
                )
            elif options.model_blob_config:
                model_type = model_type
                self.__create_reference_file(
                    model_folder, blobReference=options.model_blob_config
                )
            git_service.add_folder_to_staging(os.path.join(contract_path, "model"))
            commit = True
        else:
            reference_path = os.path.join(
                local_repository_path, contract_path, "model", "reference.json"
            )
            if not os.path.exists(reference_path):
                raise Exception("Missing model reference file in repository.")

            try:
                with open(reference_path) as referenceFile:
                    data = json.load(referenceFile)
                    if "reference" in data:
                        if "blob" in data["reference"]:
                            model_type = model_type
                        elif "docker" in data["reference"]:
                            model_type = ModelType.CUSTOM.value
                        else:
                            raise Exception(
                                "No information on to be deployed model available."
                            )
                    else:
                        raise Exception(
                            "No information on to be deployed model available."
                        )
            except IOError as e:
                raise Exception("Failed to deploy model from reference.json file.") from e

        automated_commit_message = "[Deeploy Client] Add new model"

        if explainer:
            explainer_type = self.__process_explainer(
                explainer,
                git_service,
                local_repository_path,
                overwrite_contract,
                contract_path,
            )
            automated_commit_message += " and explainer"
            commit = True
        elif options.explainer_docker_config or options.explainer_blob_config:
            self.__prepare_directory(
                "explainer", git_service, local_repository_path, contract_path, overwrite_contract
            )
            explainer_folder = os.path.join(
                local_repository_path, contract_path, "explainer"
            )
            shutil.rmtree(explainer_folder)
            os.mkdir(explainer_folder)
            if options.explainer_docker_config:
                explainer_type = ExplainerType.CUSTOM.value
                self.__create_reference_file(
                    explainer_folder, dockerReference=options.explainer_docker_config
                )
            elif options.explainer_blob_config:
                explainer_type = explainer_type
                self.__create_reference_file(
                    explainer_folder, blobReference=options.explainer_blob_config
                )
            git_service.add_folder_to_staging(os.path.join(contract_path, "explainer"))
            automated_commit_message += " and explainer"
            commit = True
        else:
            reference_path = os.path.join(
                local_repository_path, contract_path, "explainer", "reference.json"
            )

            try:
                with open(reference_path) as referenceFile:
                    data = json.load(referenceFile)
                    if "reference" in data:
                        if "blob" in data["reference"]:
                            explainer_type = explainer_type
                        elif "docker" in data["reference"]:
                            explainer_type = ExplainerType.CUSTOM.value
                        else:
                            raise Exception(
                                "No information on to be deployed explainer available."
                            )
                    else:
                        raise Exception(
                            "No information on to be deployed explainer available."
                        )
            except IOError:
                explainer_type = ExplainerType.NO_EXPLAINER.value

        if options.transformer_docker_config:
            self.__prepare_directory(
                "transformer", git_service, local_repository_path, contract_path, overwrite_contract
            )
            transformer_folder = os.path.join(
                local_repository_path, contract_path, "transformer"
            )
            shutil.rmtree(transformer_folder)
            os.mkdir(transformer_folder)
            transformer_type = TransformerType.CUSTOM.value
            self.__create_reference_file(
                transformer_folder, dockerReference=options.transformer_docker_config
            )
            git_service.add_folder_to_staging(os.path.join(contract_path, "transformer"))
            automated_commit_message += " and transformer"
            commit = True
        else:
            if transformer_type == TransformerType.CUSTOM.value:
                raise Exception(
                            f"No transformer docker configuration found in options, set transformer type to {TransformerType.NO_TRANSFORMER.value} or add docker config to options."
                        )    
        metadata_path = os.path.join(
            local_repository_path, contract_path, "metadata.json"
        )
        self.__prepare_metadata_file(
            metadata_path,
            options.feature_labels,
            options.problem_type,
            options.prediction_classes,
            overwrite_metadata,
        )
        git_service.add_folder_to_staging(os.path.join(contract_path, "metadata.json"))

        if commit:
            logging.info("Committing and pushing the result to the remote.")
            commit_sha = git_service.commit(commit_message if commit_message else automated_commit_message)
            git_service.push()
        else:
            commit_sha = Repo(local_repository_path).head.commit.hexsha

        deployment_options = {
            "name": options.name,
            "description": options.description,
            "repository_id": self.__config.repository_id,
            "example_input": options.example_input,
            "example_output": options.example_output,
            "model_type": model_type,
            "model_serverless": options.model_serverless,
            "model_instance_type": options.model_instance_type,
            "model_cpu_limit": options.model_cpu_limit,
            "model_cpu_request": options.model_cpu_request,
            "model_mem_limit": options.model_mem_limit,
            "model_mem_request": options.model_mem_request,
            "branch_name": git_service.get_current_branch_name(),
            "commit": commit_sha,
            "explainer_type": explainer_type,
            "explainer_serverless": options.explainer_serverless,
            "explainer_instance_type": options.explainer_instance_type,
            "explainer_cpu_limit": options.explainer_cpu_limit,
            "explainer_cpu_request": options.explainer_cpu_request,
            "explainer_mem_limit": options.explainer_mem_limit,
            "explainer_mem_request": options.explainer_mem_request,
            "transformer_type": transformer_type,
            "transformer_serverless": options.transformer_serverless,
            "transformer_instance_type": options.transformer_instance_type,
            "transformer_cpu_limit": options.transformer_cpu_limit,
            "transformer_cpu_request": options.transformer_cpu_request,
            "transformer_mem_limit": options.transformer_mem_limit,
            "transformer_mem_request": options.transformer_mem_request,
            "contract_path": contract_path,
            "tags": {"primary": options.custom_id, "secondary": []},
        }

        deployment = self.__deeploy_service.create_deployment(
            self.__config.workspace_id, CreateDeployment(**deployment_options)
        )

        return deployment

    def update(
        self,
        options: UpdateOptions,
        local_repository_path: str = None,
        model: Any = None,
        explainer: Any = None,
        model_type: int = None,
        explainer_type: int = None,
        transformer_type: int = None,
        overwrite_contract: bool = False,
        overwrite_metadata: bool = False,
        commit_sha: str = None,
        commit_message: str = None,
        contract_path: str = "",
    ) -> Deployment:
        """Update a model on Deeploy
        Parameters:
            model (Any): The class instance of an ML model
            options (UpdateOptions): An instance of the update options class
                containing the update options
            local_repository_path (str): Absolute path to the local git repository
                which is connected to Deeploy
            explainer (Any, optional): The class instance of an optional model explainer
            model_type (int, optional): model type enum from ModelType class
            explainer_type (int, optional): explainer type enum from ExplainerType class
            transformer_type (int, optional): transformer type enum from TransformerType class
            overwrite_contract (bool, optional): Whether or not to overwrite files that are in the
                'model' and 'explainer' folders in the git folder. Defaults to False
            overwrite_metadata (bool, optional): Whether or not to overwrite the metadata.json
                file. Defaults to False.
            commit_sha (str, optional): Commit SHA to update to
            commit_message (str, optional): Commit message to use
            contract_path (str, optional): Relative repository subpath that contains the
                Deeploy contract to deploy from
        """
        if not (self.__config.access_key and self.__config.secret_key):
            raise Exception("Missing access credentials to update deployment.")

        if not (
            self.__deeploy_service.get_deployment(
                self.__config.workspace_id, options.deployment_id
            )
        ):
            raise Exception(
                "Deployment was not found in the Deeploy workspace. \
                 Make sure the Deployment Id is correct."
            )

        git_service = GitService(local_repository_path)

        current_deployment = self.__deeploy_service.get_deployment(
            self.__config.workspace_id, options.deployment_id
        )

        commit = False
        automated_commit_message = ""
        if model or explainer:
            if local_repository_path is None:
                raise Exception(
                    "Local repository path is required to update \
                     the model or explainer."
                )
            else:
                (
                    repository_in_workspace,
                    repository_id,
                ) = self.__is_git_repository_in_workspace(git_service)

            if not repository_in_workspace:
                raise Exception(
                    "Repository was not found in the Deeploy workspace. \
                     Make sure you have connected it before."
                )

            self.__config.repository_id = repository_id

            commit = True
            logging.info("Pulling from the remote repository...")
            git_service.pull()
            logging.info("Successfully pulled from the remote repository.")

            if model:
                model_wrapper = self.__process_model(
                    model,
                    options,
                    local_repository_path,
                    git_service,
                    overwrite_contract,
                    contract_path,
                )
                model_type = model_wrapper.get_model_type().value
                automated_commit_message += "[Deeploy client] Add new model"
            else:
                # TODO: read existing reference.json and check if its a blob url or image
                # if blob url then require model_type else set model_type as custom
                model_type = model_type if model_type else ModelType.CUSTOM.value

            if explainer:
                explainer_wrapper = self.__process_explainer(
                    explainer,
                    git_service,
                    local_repository_path,
                    overwrite_contract,
                    contract_path,
                )
                explainer_type = explainer_wrapper.get_explainer_type().value
                if explainer_type != ExplainerType.NO_EXPLAINER.value:
                    automated_commit_message += " and update explainer" if automated_commit_message else "[Deeploy Client] Update explainer"
            else:
                # TODO: read existing reference.json and check if its a blob url or image
                # if blob url then require explainer_type else set explainer_type as custom
                explainer_type = (
                    explainer_type
                    if explainer_type
                    else ExplainerType.NO_EXPLAINER.value
                )

        # process model reference.json
        if options.model_docker_config or options.model_blob_config:
            self.__prepare_directory(
                "model", git_service, local_repository_path, contract_path, overwrite_contract
            )
            model_folder = os.path.join(local_repository_path, contract_path, "model")
            shutil.rmtree(model_folder)
            os.mkdir(model_folder)
            if options.model_docker_config:
                model_type = ModelType.CUSTOM.value
                self.__create_reference_file(
                    model_folder, dockerReference=options.model_docker_config
                )
            elif options.model_blob_config:
                model_type = model_type
                self.__create_reference_file(
                    model_folder, blobReference=options.model_blob_config
                )
            git_service.add_folder_to_staging(os.path.join(contract_path, "model"))
            commit = True

        # process explainer reference.json
        if options.explainer_docker_config or options.explainer_blob_config:
            self.__prepare_directory(
                "explainer", git_service, local_repository_path, contract_path, overwrite_contract
            )
            explainer_folder = os.path.join(
                local_repository_path, contract_path, "explainer"
            )
            shutil.rmtree(explainer_folder)
            os.mkdir(explainer_folder)
            if options.explainer_docker_config:
                explainer_type = ExplainerType.CUSTOM.value
                self.__create_reference_file(
                    explainer_folder, dockerReference=options.explainer_docker_config
                )
            elif options.explainer_blob_config:
                explainer_type = explainer_type
                self.__create_reference_file(
                    explainer_folder, blobReference=options.explainer_blob_config
                )
            git_service.add_folder_to_staging(os.path.join(contract_path, "explainer"))
            automated_commit_message += " and update explainer" if automated_commit_message else "[Deeploy Client] Update explainer"
            commit = True

        if options.transformer_docker_config:
            self.__prepare_directory(
                "transformer", git_service, local_repository_path, contract_path, overwrite_contract
            )
            transformer_folder = os.path.join(
                local_repository_path, contract_path, "transformer"
            )
            shutil.rmtree(transformer_folder)
            os.mkdir(transformer_folder)

            transformer_type = TransformerType.CUSTOM.value
            self.__create_reference_file(
                transformer_folder, dockerReference=options.transformer_docker_config
            )

            git_service.add_folder_to_staging(os.path.join(contract_path, "transformer"))
            automated_commit_message += " and update transformer" if automated_commit_message else "[Deeploy Client] Update transformer"
            commit = True
        
        else:
            if transformer_type == TransformerType.CUSTOM.value:
                raise Exception(
                            f"No transformer docker configuration found in options, set transformer type to {TransformerType.NO_TRANSFORMER.value} or add docker config to options."
                        )    

        metadata_path = os.path.join(
            local_repository_path, contract_path, "metadata.json"
        )
        self.__prepare_metadata_file(
            metadata_path,
            options.feature_labels,
            options.problem_type,
            options.prediction_classes,
            overwrite_metadata,
        )
        git_service.add_folder_to_staging(os.path.join(contract_path, "metadata.json"))

        if commit:
            logging.info("Committing and pushing the result to the remote.")
            commit_sha = git_service.commit(commit_message if commit_message else automated_commit_message)
            git_service.push()
        else:
            commit_sha = (
                Repo(local_repository_path).head.commit.hexsha
                if commit_sha is None
                else commit_sha
            )

        self.__config.repository_id = current_deployment.active_version["repositoryId"]

        update_options = {
            "deployment_id": options.deployment_id,
            "name": options.name,
            "description": options.description,
            "repository_id": self.__config.repository_id,
            "example_input": options.example_input,
            "example_output": options.example_output,
            "model_type": model_type,
            "model_serverless": options.model_serverless,
            "model_instance_type": options.model_instance_type,
            "model_cpu_limit": options.model_cpu_limit,
            "model_cpu_request": options.model_cpu_request,
            "model_mem_limit": options.model_mem_limit,
            "model_mem_request": options.model_mem_request,
            "branch_name": git_service.get_current_branch_name(),
            "commit": commit_sha,
            "commit_message": commit_message,
            "explainer_type": explainer_type,
            "explainer_serverless": options.explainer_serverless,
            "explainer_instance_type": options.explainer_instance_type,
            "explainer_cpu_limit": options.explainer_cpu_limit,
            "explainer_cpu_request": options.explainer_cpu_request,
            "explainer_mem_limit": options.explainer_mem_limit,
            "explainer_mem_request": options.explainer_mem_request,
            "transformer_type": transformer_type,
            "transformer_serverless": options.transformer_serverless,
            "transformer_instance_type": options.transformer_instance_type,
            "transformer_cpu_limit": options.transformer_cpu_limit,
            "transformer_cpu_request": options.transformer_cpu_request,
            "transformer_mem_limit": options.transformer_mem_limit,
            "transformer_mem_request": options.transformer_mem_request,
            "contract_path": contract_path,
        }

        update_options = self.__remove_null_values(update_options)

        if len(UpdateDeploymentMetadata(**update_options).json()) > 2:
            updated_deployment = self.__deeploy_service.update_deployment_metadata(
                self.__config.workspace_id, UpdateDeploymentMetadata(**update_options)
            )

        if (len(UpdateDeployment(**update_options).json())) > 2:
            updated_deployment = self.__deeploy_service.update_deployment(
                self.__config.workspace_id, UpdateDeployment(**update_options)
            )

        return updated_deployment

    def predict(
        self, deployment_id: str, request_body: dict
    ) -> V1Prediction or V2Prediction:
        """Make a predict call
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
            request_body (dict): Request body with input data for the model
        """

        workspace_id = self.__config.workspace_id
        prediction = self.__deeploy_service.predict(
            workspace_id, deployment_id, request_body
        )
        return prediction

    def explain(
        self, deployment_id: str, request_body: dict, image: bool = False
    ) -> object:
        """Make an explain call
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
            request_body (dict): Request body with input data for the model
            image (bool): Return image or not
        """
        workspace_id = self.__config.workspace_id
        explanation = self.__deeploy_service.explain(
            workspace_id, deployment_id, request_body, image
        )
        return explanation

    def getRequestLogs(self, deployment_id: str) -> List[RequestLog]:
        """Retrieve request logs
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
        """
        workspace_id = self.__config.workspace_id
        requestLogs = self.__deeploy_service.getRequestLogs(workspace_id, deployment_id)
        return requestLogs

    def getPredictionLogs(
        self, deployment_id: str, evaluated_only=False
    ) -> List[PredictionLog]:
        """Retrieve prediction logs
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
            evaluated_only (boolean): if true, return only predictions that have been evaluated
        """
        workspace_id = self.__config.workspace_id
        predictionLogs = self.__deeploy_service.getPredictionLogs(
            workspace_id, deployment_id, evaluated_only
        )
        return predictionLogs

    def getOnePredictionLog(
        self, deployment_id: str, request_log_id: str, prediction_log_id: str
    ) -> PredictionLog:
        """Retrieve one log
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
            request_log_id (str): ID of the request_log containing the prediction
            prediction_log_id (str): ID of the prediction_log to be retrieved
        """
        workspace_id = self.__config.workspace_id
        predictionLog = self.__deeploy_service.getOnePredictionLog(
            workspace_id, deployment_id, request_log_id, prediction_log_id
        )
        return predictionLog

    def evaluate(
        self,
        deployment_id: str,
        request_log_id: str,
        prediction_log_id: str,
        evaluation_input: dict,
    ) -> None:
        """Evaluate a prediction log
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
            log_id (int): ID of the log to be evaluated
            evaluation_input: Dict with result, value, and explanation
        """
        workspace_id = self.__config.workspace_id
        self.__deeploy_service.evaluate(
            workspace_id,
            deployment_id,
            request_log_id,
            prediction_log_id,
            evaluation_input,
        )

    def actuals(self, deployment_id: str, actuals_input: dict) -> None:
        """Evaluate a prediction log
        Parameters:
            deployment_id (str): ID of the Deeploy deployment
            actuals_input (dict): Object with predictionIds and actualsValues
                                 where the order of the values will match
                                 predictions with the actuals
                                 {
                                    "predictionIds": [],
                                    "actualValues": {"predictions" | "output": []}
                                 }
        """
        workspace_id = self.__config.workspace_id
        self.__deeploy_service.actuals(workspace_id, deployment_id, actuals_input)

    def __are_clientoptions_valid(self, config: ClientConfig) -> bool:
        """Check if the supplied options are valid"""
        try:
            self.__deeploy_service.get_workspace(config.workspace_id)
        except Exception as e:
            raise e

        return True

    def __is_git_repository_in_workspace(
        self, git_service: GitService
    ) -> Tuple[bool, str]:
        remote_url = git_service.get_remote_url()
        workspace_id = self.__config.workspace_id

        repositories = self.__deeploy_service.get_repositories(workspace_id)

        correct_repositories = list(
            filter(
                lambda x: x.remote_path == self.__parse_url_ssh_to_https(remote_url)
                or x.remote_path == remote_url,
                repositories,
            )
        )

        if len(correct_repositories) != 0:
            repository_id = correct_repositories[0].id
            return True, repository_id

        return False, None

    def __parse_url_ssh_to_https(self, remote_path: str) -> str or None:
        if remote_path[:4] != "git@":
            # https to ssh
            path_tokens = remote_path.split("/")
            provider = path_tokens[2]
            user = path_tokens[3]
            path = path_tokens[4:]
            link = "git@" + provider + ":" + user
            for sub_directory in path:
                link += "/" + sub_directory
        else:
            # ssh to https
            path_tokens = remote_path.split("@")
            link = "https://" + path_tokens[1].replace(":", "/")
        return link

    def __prepare_directory(
        self,
        component: str,
        git_service: GitService,
        local_repository_path: str,
        contract_path: str,
        overwrite_contract,
    ) -> None:
        folder_path = os.path.join(local_repository_path, contract_path, component)
        if not directory_exists(folder_path):
            try:
                os.mkdir(folder_path)
            except OSError:
                logging.error("Creation of the directory %s failed" % folder_path)
        elif not directory_empty(folder_path):
            if not overwrite_contract:
                raise Exception(
                    "The folder %s is not empty. Pass 'overwrite=True' to overwrite contents."
                    % folder_path
                )
            delete_all_contents_in_directory(folder_path)
            git_service.delete_folder_from_staging(component)
        else:  # folder exists and empty
            pass
        return

    def __prepare_metadata_file(
        self,
        path: str,
        feature_labels=None,
        problem_type=None,
        prediction_classes=None,
        overwrite_metadata=False,
    ) -> None:
        data = {"featureLabels": [], "problemType": {}, "predictionClasses": ""}

        if feature_labels:
            data["featureLabels"] = feature_labels
        if problem_type:
            data["problemType"] = problem_type
        if prediction_classes:
            data["predictionClasses"] = prediction_classes

        if file_exists(path) and not overwrite_metadata:
            pass
        else:
            try:
                with open(path, "w") as f:
                    json.dump(data, f)
            except OSError:
                logging.error("Creation of the file %s failed" % path)

    def __get_upload_size(self, local_folder_path: str) -> int:
        total_file_sizes = 0
        for root, _, files in os.walk(local_folder_path):
            for single_file in files:
                file_path = os.path.join(root, single_file)
                file_size = os.path.getsize(file_path)
                total_file_sizes += file_size
        return total_file_sizes

    def __upload_folder_to_blob(
        self, local_repository_path: str, local_folder_path: str
    ) -> str:
        upload_locations = list()
        blob_folder_uuid = str(uuid.uuid4())
        relative_folder_path = os.path.relpath(local_folder_path, local_repository_path)
        for root, _, files in os.walk(local_folder_path):
            for single_file in files:
                relative_file_path = os.path.join(
                    relative_folder_path, os.path.relpath(root, local_folder_path)
                )
                file_path = os.path.join(root, single_file)
                blob_file_location = self.__deeploy_service.upload_blob_file(
                    file_path,
                    relative_file_path,
                    self.__config.workspace_id,
                    self.__config.repository_id,
                    blob_folder_uuid,
                )
                upload_locations.append(blob_file_location)

        partition = upload_locations[0].partition(relative_folder_path)
        blob_folder_path = partition[0] + partition[1]
        return blob_folder_path

    def __remove_null_values(self, d: dict) -> dict:
        def empty(x):
            return x is None or x == {} or x == []

        if not isinstance(d, (dict, list)):
            return d
        elif isinstance(d, list):
            return [
                v for v in (self.__remove_null_values(v) for v in d) if not empty(v)
            ]
        else:
            return {
                k: v
                for k, v in ((k, self.__remove_null_values(v)) for k, v in d.items())
                if not empty(v)
            }

    def __create_reference_file(
        self,
        local_folder_path: str,
        dockerReference: DockerReference = None,
        blobReference: BlobReference = None,
    ) -> None:
        file_path = os.path.join(local_folder_path, "reference.json")

        reference_json = {
            "reference": {
                "docker": {
                    "image": dockerReference.image if dockerReference else None,
                    "uri": dockerReference.uri if dockerReference else None,
                    "credentialsId": dockerReference.credentialsId
                    if dockerReference
                    else None,
                    "port": dockerReference.port if dockerReference else None,
                },
                "blob": {
                    "url": blobReference.url if blobReference else None,
                    "credentialsId": blobReference.credentialsId
                    if blobReference
                    else None,
                    "region": blobReference.region if blobReference else None,
                },
            },
        }
        reference_json = self.__remove_null_values(reference_json)

        data = parse_obj_as(ModelReferenceJson, reference_json)

        with open(file_path, "w") as outfile:
            json.dump(data.dict(), outfile)
        return

    def __process_model(
        self,
        model,
        options: DeployOptions or UpdateOptions,
        local_repository_path: str,
        git_service: GitService,
        overwrite_contract: bool,
        contract_path: str,
    ) -> ModelType:
        logging.info("Saving the model to disk...")
        model_folder = os.path.join(local_repository_path, contract_path, "model")
        model_wrapper = ModelWrapper(
            model,
            pytorch_model_file_path=options.pytorch_model_file_path,
            pytorch_torchserve_handler_name=options.pytorch_torchserve_handler_name,
        )
        self.__prepare_directory(
            "model", git_service, local_repository_path, contract_path, overwrite_contract
        )
        model_wrapper.save(model_folder)
        blob_storage_link = self.__upload_folder_to_blob(
            local_repository_path, model_folder
        )
        shutil.rmtree(model_folder)
        os.mkdir(model_folder)
        self.__create_reference_file(
            model_folder, blobReference=BlobReference(url=blob_storage_link)
        )
        git_service.add_folder_to_staging(os.path.join(contract_path, "model"))
        return model_wrapper.get_model_type()

    def __process_explainer(
        self,
        explainer,
        git_service: GitService,
        local_repository_path: str,
        overwrite_contract: bool,
        contract_path: str,
    ) -> ExplainerType:
        logging.info("Saving the explainer to disk...")
        explainer_wrapper = ExplainerWrapper(explainer)
        self.__prepare_directory(
            "explainer", git_service, local_repository_path, contract_path, overwrite_contract
        )
        explainer_folder = os.path.join(
            local_repository_path, contract_path, "explainer"
        )
        explainer_wrapper.save(explainer_folder)
        blob_storage_link = self.__upload_folder_to_blob(
            local_repository_path, explainer_folder
        )
        shutil.rmtree(explainer_folder)
        os.mkdir(explainer_folder)
        self.__create_reference_file(
            explainer_folder, blobReference=BlobReference(url=blob_storage_link)
        )
        git_service.add_folder_to_staging(os.path.join(contract_path, "explainer"))
        return explainer_wrapper.get_explainer_type().value
