import concurrent.futures
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING, Union

import yaml
from dataclasses_json import config, dataclass_json, LetterCase

from predibase.pql.api import ServerResponseError
from predibase.resource.connection import get_dataset
from predibase.resource.dataset import Dataset
from predibase.resource.engine import Engine
from predibase.resource.llm.response import GeneratedResponse
from predibase.resource.model import create_model_repo, ModelFuture, ModelRepo
from predibase.util import load_yaml

if TYPE_CHECKING:
    from predibase.pql.api import Session


_PATH_HERE = os.path.abspath(os.path.dirname(__file__))
_TEMPLATE_DIR = os.path.join(_PATH_HERE, "templates")


class HuggingFaceLLM:
    def __init__(self, session: "Session", model_name: str):
        self.session = session
        self.model_name = model_name

    def deploy(
        self,
        deployment_name: str,
        engine_template: Optional[str] = None,
        hf_token: Optional[str] = None,
        auto_suspend_seconds: Optional[int] = None,
    ) -> "LLMDeploymentJob":
        params = {"modelName": self.model_name}
        if hf_token:
            params["hfToken"] = hf_token
        data = self.session.get_json("/supported_llms", params=params)
        llm_config = data["deploymentSpec"]

        message = data["message"]
        if message:
            print("=" * len(message))
            print(message)
            print("=" * len(message))

        model_params = {
            **llm_config,
            "name": deployment_name,
            "modelName": self.model_name,
            "engineTemplate": engine_template,
            "scaleDownPeriod": auto_suspend_seconds,
        }

        if hf_token is not None:
            model_params["hfToken"] = hf_token

        print("Deploying the model with the following params:")
        print(model_params)

        self.session.post_json(
            "/llms",
            json=model_params,
        )

        return LLMDeploymentJob(deployment_name, self.session)

    def finetune(
        self,
        template: Optional[str] = None,
        target: Optional[str] = None,
        dataset: Optional[Union[str, Dataset]] = None,
        engine: Optional[Union[str, Engine]] = None,
        config: Optional[Union[str, Dict]] = None,
        repo: Optional[str] = None,
    ) -> ModelFuture:
        if config is None:
            with open(os.path.join(_TEMPLATE_DIR, "defaults.yaml")) as f:
                config_str = f.read()
            config_str = config_str.format(base_model=self.model_name, template=template, target=target)
            print(config_str)
            config = yaml.safe_load(config_str)
        else:
            config = load_yaml(config)

        if repo is None:
            dataset_name = dataset.name if isinstance(dataset, Dataset) else dataset
            if "/" in dataset_name:
                _, dataset_name = dataset_name.split("/")

            model_name = self.model_name
            if "/" in model_name:
                _, model_name = model_name.split("/")

            repo = f"{model_name}-{dataset_name}"

        if "/" in repo:
            repo = repo.replace("/", "-")

        repo: ModelRepo = get_or_create_repo(self.session, repo)
        if dataset is None:
            # Assume the dataset is the same as the repo head
            md = repo.head().to_draft()
            md.config = config
        else:
            if isinstance(dataset, str):
                conn_name = None
                if "/" in dataset:
                    conn_name, dataset = dataset.split("/")
                dataset = get_dataset(self.session, dataset, connection_name=conn_name)
            md = repo.create_draft(config=config, dataset=dataset)

        return md.train_async(engine=engine)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class _LLMDeployment:
    id: int = field(metadata=config(field_name="id"))
    tenant_id: int = field(metadata=config(field_name="tenantID"))
    uuid: str = field(metadata=config(field_name="uuid"))
    name: str = field(metadata=config(field_name="name"))
    description: Optional[str] = field(metadata=config(field_name="description"))
    model_name: str = field(metadata=config(field_name="modelName"))
    num_shards: Optional[int] = field(metadata=config(field_name="numShards"))
    quantize: bool = field(metadata=config(field_name="quantize"))
    deployment_status: str = field(metadata=config(field_name="deploymentStatus"))

    prompt_template: str = field(metadata=config(field_name="promptTemplate"))
    min_replicas: int = field(metadata=config(field_name="minReplicas"))
    max_replicas: int = field(metadata=config(field_name="maxReplicas"))
    created: str = field(metadata=config(field_name="created"))
    updated: str = field(metadata=config(field_name="updated"))
    created_by_user_id: Optional[int] = field(metadata=config(field_name="createdByUserID"))
    scale_down_period: int = field(metadata=config(field_name="scaleDownPeriod"))
    error_text: Optional[str] = field(metadata=config(field_name="errorText"), default=None)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LLMDeploymentReadyResponse:
    name: str
    ready: bool


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LLMDeploymentScaledResponse:
    name: str
    scaled: bool


class LLMDeployment:
    def __init__(self, session: "Session", name: str, deployment_metadata: Optional[_LLMDeployment] = None):
        self.session = session
        self.name = name
        self.data = (
            _LLMDeployment.from_dict(self.session.get_json(f"/llms/{self.name}"))
            if deployment_metadata is None
            else deployment_metadata
        )

    def generate(
        self,
        templates: Union[str, List[str]],
        options: Optional[Dict[str, float]] = None,
    ) -> List[GeneratedResponse]:
        templates = [templates] if isinstance(templates, str) else templates

        resp_list, future_to_args = [], dict()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for input_text in templates:
                future = executor.submit(
                    self.session.post_json,
                    f"/llms/{self.name}/generate",
                    {
                        "inputs": input_text,
                        "parameters": options,
                    },
                )
                future_to_args[future] = (self.name, input_text)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    deployment_name, input_text = future_to_args[future]
                    res = future.result()
                    res = GeneratedResponse(
                        prompt=input_text,
                        response=res["generated_text"],
                        model_name=deployment_name,
                        generated_tokens=res["details"]["generated_tokens"],
                    )
                    resp_list.append(res)
                except Exception as exc:
                    print("ERROR:", exc)
        return resp_list

    def prompt(
        self,
        templates: Union[str, List[str]],
        options: Optional[Dict[str, float]] = None,
    ) -> List[GeneratedResponse]:
        deployment_status = self.get_status()
        if deployment_status != "active":
            raise Exception(f"Target LLM deployment `{self.name}` is not active yet!")

        deployment_ready = self.is_ready()
        if not deployment_ready:
            print(f"WARNING: Target LLM deployment `{self.name}` is not fully scaled yet. Responses may be delayed...")

        # talk directly to the LLM, bypassing Temporal and the engines.
        return self.generate(templates=templates, options=options)

    def delete(self):
        print(f"Requested deletion of llm deployment: `{self.name}` ...")
        endpoint = f"/llms/{self.name}"
        resp = self.session._delete(endpoint)
        if not resp.ok:
            raise RuntimeError(f"Failed to trigger LLM deletion - got status {resp.status_code} -- {resp.reason}")

        while True:
            try:
                self.session.get_json(endpoint)
            except Exception as e:
                if isinstance(e, ServerResponseError) and "record not found" in e.message:
                    print(f"Successfully deleted llm deployment: `{self.name}`")
                    break
                else:
                    raise RuntimeError(f"Error while deleting deployment `{self.name}`: {e} {type(e)}")
            time.sleep(1.0)

    def is_ready(self) -> bool:
        resp = self.session.get_json(f"/llms/{self.name}/ready")
        return LLMDeploymentReadyResponse.from_dict(resp).ready

    def wait_for_ready(self, timeout_seconds: int = 600, poll_interval_seconds: int = 5) -> bool:
        start = time.time()
        while int(time.time() - start) < timeout_seconds:
            if self.is_ready():
                return True
            time.sleep(poll_interval_seconds)
        return False

    def is_scaled(self) -> bool:
        resp = self.session.get_json(f"/llms/{self.name}/scaled")
        return LLMDeploymentScaledResponse.from_dict(resp).scaled

    def get_status(self) -> str:
        resp = _LLMDeployment.from_dict(self.session.get_json(f"/llms/{self.name}"))
        return resp.deployment_status


class LLMDeploymentJob:
    def __init__(self, deployment_name: str, session: "Session"):
        self._deployment_name = deployment_name
        self._uri = f"pb://jobs/deploy::{deployment_name}"
        self._session = session

    def get(self) -> LLMDeployment:
        resp = self._session.get_llm_deployment_until_with_logging(
            f"/llms/{self._deployment_name}",
            lambda resp: resp["deploymentStatus"] == "active",
            lambda resp: f"Failed to create deployment {self._deployment_name} with status {resp['deploymentStatus']}"
            if resp["deploymentStatus"] in ("failed", "canceled")
            else None,
        )

        return LLMDeployment(self._session, self._deployment_name, resp)

    def cancel(self):
        return self._session.post_json(f"/llms/{self._deployment_name}/cancel", {})


def get_or_create_repo(session: "Session", repo_name: str) -> ModelRepo:
    return create_model_repo(session, name=repo_name, exists_ok=True)
