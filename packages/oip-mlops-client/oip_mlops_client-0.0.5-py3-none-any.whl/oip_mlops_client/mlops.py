import mlflow
import os
from PIL.Image import Image
import numpy as np
from matplotlib.figure import Figure
from plotly.graph_objects import Figure as FigureP
import io
import json
import hashlib
import tempfile
from typing import Union, Dict, List, Optional, Any
from .lib import get_data_from_entity, check_env_variables
from .wavfile import write as wavfile_write
from .rest import http_request, augmented_raise_for_status


def log_artifact_extra(extra: Optional[Dict[str, Any]], artifact_path: str) -> None:
    """
    :param extra: Dict: extra information to log with the artifact
    :param artifact_path: the artifact path
    """

    # If extra is none, nothing to do
    if not extra:
        return

    # Check if necessary env variables are set
    check_env_variables()

    # Get the active run and check if it not none
    run = mlflow.active_run()
    if not run:
        raise RuntimeError("NO ACTIVE RUN, PLEASE START THE RUN...")

    # Add mlflow/experiment_id/run_id/artifacts to artifact path
    run_id = run.info.run_id
    experiment_id = run.info.experiment_id
    artifact_path = os.path.join(
        "mlflow", experiment_id, run_id, "artifacts", artifact_path
    )

    # Add artifact_path to extra that will be used as request body
    extra["artifact_path"] = artifact_path

    # Create token and headers
    endpoint: str = f"{os.environ['OIP_API_HOST']}/mlflow/update_artifact_object"
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {os.environ['MLFLOW_TRACKING_TOKEN']}"
    }

    # Make the request to the tracking server
    resp = http_request("POST", endpoint, headers=headers, json=extra)
    augmented_raise_for_status(resp)


class LogModelMethodWrapper:
    def __init__(self, method):
        self.method = method

    def __call__(self, *args, **kwargs):

        modified_args = list(args)

        if len(args) == 2:
            # If called with two positional arguments
            modified_args[1] = "model"
        elif "artifact_path" in kwargs:
            # If called with named arguments
            kwargs["artifact_path"] = "model"

        return self.method(*modified_args, **kwargs)


class ModuleWrapper:
    def __init__(self, module):
        self.module = module

    def __getattr__(self, attr):
        module_attr = getattr(self.module, attr)

        if attr == "log_model":
            return LogModelMethodWrapper(module_attr)

        return module_attr


class MLOpsMeta(type):
    def __getattr__(cls, attr):

        mlflow_attr = getattr(mlflow, attr)

        # If the attribute is a module, wrap it using ModuleWrapper
        if type(mlflow_attr).__name__ == "module":
            return ModuleWrapper(mlflow_attr)

        return mlflow_attr


class MLOps(metaclass=MLOpsMeta):
    @staticmethod
    def connect(api_host: str, api_key: str, workspace_name: str):
        """
        Connect to the remove MLOPS platform
        It will check if the workspace exists and get its id
        Then set the the api host, the workspace id, and the api key
        :param api_host: str: The API Host
        :param api_key: str: The API Key
        :param workspace_name: str: The workspace name
        """
        # Check if workspace exists
        data = get_data_from_entity(
            access_token=api_key,
            api_host=api_host,
            entity="mlflow_workspace",
            params={
                "filter_cols": "name",
                "filter_ops": "=",
                "filter_vals": workspace_name,
            },
        )
        if not data:
            raise ValueError(f"WORKSPACE {workspace_name} DOES NOT EXIST")

        # Get workspace id
        workspace_id: str = data[0]["id"]

        # Set tracking URL & access token & workspace & api host
        mlflow.set_tracking_uri(f"{api_host}/mlflow/{workspace_id}")
        os.environ["OIP_API_HOST"] = api_host
        os.environ["MLFLOW_WORKSPACE_ID"] = workspace_id
        os.environ["MLFLOW_TRACKING_TOKEN"] = api_key

    @staticmethod
    def set_experiment(experiment_name: str):
        """
        Set experiment by experiment_name
        :param experiment_name: str: experiment name
        """

        # Check env variables
        check_env_variables()

        # Check if exp exists
        data = get_data_from_entity(
            access_token=os.environ["MLFLOW_TRACKING_TOKEN"],
            api_host=os.environ["OIP_API_HOST"],
            entity="mlflow_experiment",
            params={
                "filter_cols": "name|mlflow_workspace_id",
                "filter_ops": "=|=",
                "filter_vals": f"{experiment_name}|{os.environ['MLFLOW_WORKSPACE_ID']}",
            },
        )
        if not data:
            raise ValueError(f"EXPERIMENT {experiment_name} DOES NOT EXIST")

        # Get workspace id
        exp_id: str = data[0]["id"]

        # Set mlflow experiment_id
        mlflow.set_experiment(experiment_id=exp_id)

    @staticmethod
    def close():
        """
        Delete the env variable: MLFLOW_TRACKING_TOKEN
        """
        mlflow.end_run()
        if "MLFLOW_TRACKING_TOKEN" in os.environ:
            del os.environ["MLFLOW_TRACKING_TOKEN"]

    @staticmethod
    def log_image_at_step(
        image: Union[np.ndarray, Image],
        file_name: str,
        step: int,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        artifact_file: str = f"image/step_{str(int(step))}/{file_name}"
        mlflow.log_image(image, artifact_file)
        log_artifact_extra(extra, artifact_file)

    @staticmethod
    def log_figure_at_step(
        figure: Union[Figure, FigureP],
        file_name: str,
        step: int,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        artifact_path: str = f"figure/step_{str(int(step))}/{file_name}"
        mlflow.log_figure(figure, artifact_path)
        log_artifact_extra(extra, artifact_path)

    @staticmethod
    def log_json_at_step(
        dictionary: Union[Dict, List],
        file_name: str,
        step: int,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        artifact_path: str = f"json/step_{str(int(step))}/{file_name}"
        mlflow.log_dict(dictionary, artifact_path)
        log_artifact_extra(extra, artifact_path)

    @staticmethod
    def log_text_at_step(
        text: str,
        file_name: str,
        step: int,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        artifact_path: str = f"text/step_{str(int(step))}/{file_name}"
        mlflow.log_text(text, artifact_path)
        log_artifact_extra(extra, artifact_path)

    @staticmethod
    def log_llm_predictions_at_step(
        inputs: List[Dict[str, str]],
        outputs: List[str],
        prompts: List[str],
        step: int,
    ) -> None:
        dictionary: Dict[str, Any] = {
            "inputs": inputs,
            "outputs": outputs,
            "prompts": prompts,
        }
        serialized_data: bytes = json.dumps(dictionary, sort_keys=True).encode("utf-8")
        md5_hash: str = hashlib.md5(serialized_data).hexdigest()
        file_name: str = f"{md5_hash}.json"
        artifact_path: str = f"llm_predictions/step_{str(int(step))}/{file_name}"
        mlflow.log_dict(dictionary, artifact_path)

    @staticmethod
    def log_audio_at_step(
        data: Union[
            np.ndarray,
        ],
        file_name: str,
        step: int,
        rate: int = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:

        audio_formats = ("mp3", "wav", "flac")

        audio_format = file_name.split(".")[-1]
        if isinstance(data, np.ndarray):
            # Currently, only WAV audio formats are supported for numpy
            if audio_format != "wav":
                raise ValueError(f"Only WAV audio formats are supported for numpy")

            if not rate:
                rate = 22500
                print(f'Parameter "rate" is not provided! Using default: {rate}')
            bs = wavfile_write.write(rate, data)
            data = bs

        # act as a regular file with enforced audio format definition by user side
        if not audio_format:
            raise ValueError("Audio format must be provided.")
        elif audio_format not in audio_formats:
            raise ValueError(
                f"Invalid audio format is provided. Must be one of {audio_formats}"
            )

        if isinstance(data, str):
            if not os.path.exists(data) or not os.path.isfile(data):
                raise ValueError("Invalid audio file path")
            with open(data, "rb") as FS:
                data = FS.read()
        elif isinstance(data, io.BytesIO):
            data = data.read()

        if not isinstance(data, bytes):
            raise TypeError("Content is not a byte-stream object")

        artifact_path: str = f"audio/step_{str(int(step))}/{file_name}"
        with tempfile.NamedTemporaryFile(suffix=f".{audio_format}") as tmp:
            tmp.write(data)
            local_path = tmp.name
            mlflow.log_artifact(local_path, artifact_path)

        log_artifact_extra(extra, artifact_path)

    @staticmethod
    def infer_signature(model_input, model_output):
        return mlflow.models.signature.infer_signature(model_input, model_output)
