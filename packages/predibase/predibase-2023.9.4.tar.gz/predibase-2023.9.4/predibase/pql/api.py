#! /usr/bin/env python
# Copyright (c) 2021 Predibase, Inc.
import json
import logging
import platform
import sys
import time
from dataclasses import dataclass
from threading import Thread
from typing import Any, Callable, Dict, Optional, Tuple, Union

import pandas as pd
import requests
import requests.exceptions
import websockets
from tqdm import tqdm
from urllib3.util import Retry
from websockets.sync.client import connect

from predibase.pql.adapter import TimeoutHTTPAdapter
from predibase.pql.utils import get_results_df, retry
from predibase.resource.user import User
from predibase.util import log_error
from predibase.util.json import max_epochs_of_model_response
from predibase.util.metrics import MetricsPrintedTable
from predibase.version import __version__


class PQLException(RuntimeError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ServerResponseError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(message)
        self.message = message
        self.code = code


@dataclass
class Session:
    connection_id: int = None
    verbose: bool = False
    url: str = None
    serving_grpc_endpoint: str = None
    serving_http_endpoint: str = None
    tenant: str = "default"
    token: str = None
    timeout_in_seconds: int = 60

    def __post_init__(self):
        self._token_user_cache: Optional[Tuple[str, User]] = None

    def execute(
        self,
        statement: str,
        params: Dict[str, Any] = None,
        connection_id: Optional[int] = None,
        engine_id: Optional[int] = None,
    ) -> pd.DataFrame:
        if not self.is_plan_expired():
            if not statement.endswith(";"):
                statement += ";"

            params = params or {}
            if self.verbose:
                logging.info("-- EXECUTE:")
                logging.info(statement)

            conn = connection_id or self.connection_id
            resp = self._post(
                "/queries",
                json={
                    "connectionID": conn,
                    "rawQuery": statement,
                    "queryParams": params,
                    "engineID": engine_id,
                },
            )
            data = _to_json(resp)

            start_t = time.time()
            last_t = start_t

            query_status = data.get("queryStatus")
            if query_status:
                query_id = query_status["id"]
                while not query_status.get("completed"):
                    time.sleep(0.25)
                    query_status = self.get_query_status(query_id)
                    if self.verbose:
                        last_t = show_progress(last_t)

                status = query_status.get("status")
                if status == "completed":
                    if self.verbose:
                        logging.info(f"\n-- DONE: {round(time.time() - start_t, 2)}s")
                    # TODO: do not fetch results all at once, just return metadata like rowcount
                    return self.get_results(query_id)
                else:
                    raise PQLException(
                        f"Query completed with invalid status: {status}\n"
                        f"Query:\n{query_status['rawQuery']}\n"
                        f"Error:\n{query_status['errorText']}\n",
                    )

            raise PQLException(f"Invalid response: {data}")
        else:
            raise PermissionError(
                "Queries are locked for expired plans. Contact us to upgrade.",
            )

    @property
    def user(self) -> User:
        if self._token_user_cache is None or self._token_user_cache[0] != self.token:
            self._token_user_cache = (self.token, self.get_current_user())
        return self._token_user_cache[1]

    def get_current_user(self):
        resp = self.get_json("/users/current")
        return User.from_dict({"session": self, **resp})

    def is_free_trial(self):
        return self.user.tenant.subscription.tier == "free"

    def is_plan_expired(self):
        days_remaining = self.user.tenant.subscription.days_remaining_in_plan

        if days_remaining is None:
            return False

        return days_remaining <= 0

    @retry(times=20, exceptions=(requests.exceptions.ChunkedEncodingError,))
    def get_query_status(self, query_id: int) -> str:
        resp = self._get(f"/queries/{query_id}")
        data = _to_json(resp)
        return data["queryStatus"]

    def get_results(self, query_id: int) -> pd.DataFrame:
        retry_backoff = 10  # seconds
        max_retries = 180  # 6 retries per minute, * 30 minutes
        current_retry_count = 0

        while True:
            resp = self._get(f"/queries/{query_id}/results")
            data = _to_json(resp)

            if resp.status_code == 202:
                # This means that there was an issue w/ the request, engine status was not active
                if current_retry_count >= max_retries:
                    raise PQLException(f'Unable to fetch query results, engine status: {data["engineStatus"]}')

                current_retry_count += 1
                time.sleep(retry_backoff)
                continue

            return get_results_df(data)

    def get_dataset_id(self, name: str) -> int:
        datasets = self.get_datasets()
        matched_datasets = datasets.loc[datasets["name"] == name]
        return int(matched_datasets.iloc[-1].id)

    def set_connection(self, connection_id_or_name: Union[str, int]):
        self.connection_id = self.get_connection_id(connection_id_or_name)

    def get_connections(self) -> pd.DataFrame:
        resp = self._get("/connections")
        data = _to_json(resp).get("connections")
        if data is None:
            return pd.DataFrame()
        return pd.DataFrame.from_dict(data)

    def get_connection_id(self, connection_id_or_name: Union[str, int]):
        if isinstance(connection_id_or_name, str):
            endpoint = f"/connections/name/{connection_id_or_name}"
            resp = self.get_json(endpoint)
            return int(resp["id"])
        return connection_id_or_name

    def get_datasets(self) -> pd.DataFrame:
        resp = self._get("/data/datasets/fetch/allowed_only")
        data = _to_json(resp).get("datasets")
        if data is None:
            return pd.DataFrame()
        return pd.DataFrame.from_dict(data)

    def head(self, endpoint) -> requests.Response:
        return self._http().head(self.url + endpoint, headers=self._get_headers())

    def post(self, endpoint, data: Any = None, json: Any = None, **kwargs):
        resp = self._post(endpoint, data=data, json=json, **kwargs)
        return _to_json(resp)

    def post_json(self, endpoint: str, json: Any, **kwargs):
        resp = self._post(endpoint, json=json, **kwargs)
        return _to_json(resp)

    def put_json(self, endpoint: str, json: Any):
        resp = self._put(endpoint, json)
        return _to_json(resp)

    def delete_json(self, endpoint: str):
        self._delete(endpoint)

    def get_json_until(
        self,
        endpoint: str,
        success_cond: Callable,
        error_cond: Optional[Callable] = None,
    ):
        while True:
            resp = self.get_json(endpoint)
            if success_cond(resp):
                return resp
            if error_cond is not None:
                base_err = error_cond(resp)
                if base_err:
                    err_text = resp.get("modelVersion", {}).get("errorText", "Unknown")
                    error_msg = f"{base_err}\n\n" f"Remote error:\n\n{err_text}\n"
                    raise RuntimeError(error_msg)

            time.sleep(1.0)

    def get_json_until_with_logging(
        self,
        endpoint: str,
        success_cond: Callable,
        error_cond: Optional[Callable] = None,
    ):
        last_status = None

        pbars = []
        training_bar = None
        max_epochs = None
        ws = None
        ws_data = []

        def update_last_pbar():
            if pbars:
                pbars[-1].bar_format = "✓ " + pbar.desc + " {elapsed}"
                pbars[-1].close()

        while True:
            resp = self.get_json(endpoint)
            if success_cond(resp):
                update_last_pbar()
                curr_status = resp["modelVersion"]["status"].capitalize()
                pbar = tqdm(None, bar_format=curr_status.capitalize(), desc=curr_status.capitalize(), ncols=0)
                pbar.update()
                pbar.close()
                return resp
            if error_cond is not None:
                base_err = error_cond(resp)
                if base_err:
                    curr_status = resp["modelVersion"]["status"].capitalize()
                    pbar = tqdm(None, bar_format=curr_status.capitalize(), desc=curr_status.capitalize(), ncols=0)
                    pbar.update()
                    pbar.close()

                    err_text = resp.get("modelVersion", {}).get("errorText", "Unknown")
                    error_msg = f"{base_err}\n\n" f"Remote error:\n\n{err_text}\n"
                    raise RuntimeError(error_msg)
            curr_status = resp["modelVersion"]["status"]
            if curr_status != last_status:
                update_last_pbar()
                last_status = curr_status
                if curr_status != "training":
                    pbar = tqdm(
                        None,
                        bar_format="  " + curr_status.capitalize() + "... {elapsed}",
                        desc=curr_status.capitalize(),
                        ncols=0,
                    )
                    pbars.append(pbar)
                elif not ws:
                    max_epochs = max_epochs_of_model_response(resp["modelVersion"])

                    if training_bar is None:
                        training_bar = tqdm(
                            None,
                            bar_format="  {desc} {elapsed} | {bar}| {n_fmt}/{total_fmt} epochs",
                            desc="Training...",
                            total=max_epochs,
                            ncols=0,
                        )

                    ws = self.get_websocket(f"/models/metrics/history/stream/{resp['modelVersion']['id']}")

                    t = Thread(target=self._stream_model_metrics, args=(ws, ws_data, training_bar))
                    t.start()
            if pbars:
                pbars[-1].update()
            if training_bar is not None:
                training_bar.refresh()
            time.sleep(1.0)

    def get_llm_deployment_until_with_logging(
        self,
        endpoint: str,
        success_cond: Callable,
        error_cond: Optional[Callable] = None,
    ):
        last_status = None
        pbars = []

        while True:
            resp = self.get_json(endpoint)
            if success_cond(resp):
                if pbars:
                    pbars[-1].close()
                curr_status = resp["deploymentStatus"].capitalize()
                pbar = tqdm(None, bar_format=curr_status.capitalize(), desc=curr_status.capitalize(), ncols=0)
                pbar.update()
                pbar.close()
                return resp
            if error_cond is not None:
                base_err = error_cond(resp)
                if base_err:
                    curr_status = resp["deploymentStatus"].capitalize()
                    pbar = tqdm(None, bar_format=curr_status.capitalize(), desc=curr_status.capitalize(), ncols=0)
                    pbar.update()
                    pbar.close()

                    # TODO(hungcs): Add back when we get deployment errors
                    # err_text = resp.get("modelVersion", {}).get("errorText", "Unknown")
                    # error_msg = f"{base_err}\n\n" f"Remote error:\n\n{err_text}\n"
                    raise RuntimeError(base_err)
            curr_status = resp["deploymentStatus"]
            if curr_status != last_status:
                if pbars:
                    pbar = pbars[-1]
                    pbar.bar_format = pbar.desc + " {elapsed}"
                    pbar.close()
                last_status = curr_status
                pbar = tqdm(
                    None,
                    bar_format=curr_status.capitalize() + "... {elapsed}",
                    desc=curr_status.capitalize(),
                    ncols=0,
                )
                pbars.append(pbar)
            if pbars:
                pbars[-1].update()
            # TODO(julian): Adding additional call to ensure endpoint is getting scaled (will timeout after 5s)
            resp = self.get_json(f"{endpoint}/ready")

    def wait_for_dataset(self, endpoint, until_fully_connected: bool = False):
        while True:
            resp = self.get_json(endpoint)
            if "lastError" in resp and resp["lastError"]:
                raise ValueError("Error waiting for dataset", resp["lastError"])
            if until_fully_connected:
                if resp["status"] == "connected":
                    return resp
            else:
                return resp
            time.sleep(1.0)

    def get_json(self, endpoint: str, params: dict = None):
        resp = self._get(endpoint, params=params)
        return _to_json(resp)

    def get_websocket(self, endpoint: str) -> websockets.sync.client.ClientConnection:
        ws_url = self.url.replace("https://", "wss://").replace("http://", "ws://")
        return connect(ws_url + endpoint, additional_headers=self._get_headers())

    def _http(self):
        """Returns a http requests configured with back off and timeout. Will timeout after 20 seconds, and will
        sleep for time based on:

        {backoff factor} * (2 ** ({number of total retries} - 1))
        """
        # see: https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[104, 429, 500, 502, 503, 504],  # Exclude bad request
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
        )
        http = requests.Session()
        adapter = TimeoutHTTPAdapter(
            max_retries=retry_strategy,
            timeout=self.timeout_in_seconds,
        )
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http

    # def _ws(self):
    #     http = requests.Session()
    #     http.mount("wss://", adapter)
    #     http.mount("ws://", adapter)
    #     return http

    def _get_headers(self):
        return {
            "Authorization": "Bearer " + self.token,
            "User-Agent": f"predibase-sdk/{__version__} ({platform.version()})",
        }

    def _post(self, endpoint: str, data: Any = None, json: Any = None, **kwargs):
        return self._http().post(self.url + endpoint, data=data, json=json, headers=self._get_headers(), **kwargs)

    def _get(self, endpoint: str, params: dict = None):
        return self._http().get(self.url + endpoint, headers=self._get_headers(), params=params)

    def _get_ws(self, endpoint: str):
        ws_url = self.url.replace("https://", "wss://").replace("http://", "ws://")
        return requests.Session().get(ws_url + endpoint, headers=self._get_headers(), timeout=None, stream=True)

    def _delete(self, endpoint: str):
        return self._http().delete(self.url + endpoint, headers=self._get_headers())

    def _put(self, endpoint: str, json_data: Any):
        return self._http().put(self.url + endpoint, json=json_data, headers=self._get_headers())

    def _stream_model_metrics(self, ws, ws_data, training_bar):
        try:
            while True:
                resp = ws.recv()
                resp = json.loads(resp)
                metrics_data = resp["data"]
                if len(resp["data"]) > 0:
                    ws_data.append(metrics_data)
                    run_ids = metrics_data.keys()
                    if resp["meta"]["is_hyperopt"]:
                        run_id = max(run_ids, key=lambda rid: metrics_data[rid][-1]["epoch"])
                    else:
                        run_id = next(iter(run_ids))
                    epoch = metrics_data[run_id][-1]["epoch"]
                    training_bar.update(epoch - training_bar.n)
                    for epoch_data in metrics_data[run_id]:
                        filtered_epoch_data = {
                            k: epoch_data[k]
                            for k in epoch_data
                            if k.startswith(("train_metrics", "validation_metrics", "test_metrics"))
                        }
                        table = MetricsPrintedTable(filtered_epoch_data)
                        table.log_info()
                if resp["meta"]["is_completed"]:
                    training_bar.total = training_bar.n
                    training_bar.bar_format = "✓  {desc} {elapsed} | {bar}| {n_fmt}/{total_fmt} epochs"
                    training_bar.close()
                    ws.close()
                    return
        except websockets.exceptions.ConnectionClosedOK:
            pass
        # TODO (hungcs): Handle specific error types
        except Exception:
            pass


def show_progress(last_t):
    t = time.time()
    if t - last_t > 1:
        sys.stdout.write("")
        sys.stdout.flush()
        return t
    return last_t


def _to_json(resp: requests.Response) -> Dict:
    if resp.status_code != 200:
        if resp.status_code == 202:
            # Processing in progress
            return {}

        raise ServerResponseError(f"Error {resp.status_code}: {_get_error(resp)}", resp.status_code)
    if resp.content:
        try:
            data = resp.json()
            if data:
                if type(data) is dict:
                    error_message = data.get("errorMessage")
                    if error_message:
                        # TODO: very strange to call these PQLExceptions.
                        raise PQLException(error_message)
            return data
        except requests.exceptions.JSONDecodeError:
            log_error(f"Failed to decode payload as JSON. Payload text: \n{resp.text}\n")
            raise

    return {}


def _get_error(resp):
    try:
        data = resp.json()
        if data is None:
            return "Unknown server error"
        if "error" in data:
            return data["error"]
        return resp.reason
    except requests.exceptions.JSONDecodeError:
        return f"Failed to decode payload as JSON. Payload text: \n{resp.text}\n"
