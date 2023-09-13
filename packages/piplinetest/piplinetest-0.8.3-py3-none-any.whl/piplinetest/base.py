import re
import traceback
import csv
import time
import threading
import multiprocessing
from logging import getLogger, Logger
from typing import Union, List, Any, Optional
from enum import Enum
from json import load
from pathlib import Path

from pydantic import BaseModel, Field
from requests import Response

from .import_utils import import_lib
from .http_request import http_request
from .log import setup_logger


logger = setup_logger()


class LockType(str, Enum):
    thread = "thread"
    process = "process"


class TestStepTypeEnum(Enum):
    http_api = "http_api"
    ui = "ui"


class BaseTestStep(BaseModel):
    """base test step

    Args:
        BaseModel (_type_): every http test step
    """

    url_format_pattern: str = r"{(.*?)}"
    lock_type: Optional[LockType] = Field(title="lock type", default=None)

    name: str = Field(title="test step name", default=None)
    url: str = Field(title="http api url")
    method: str = Field(title="http method like: GET|POST|PATCH")
    headers: Union[dict, None] = Field(title="http header", default={})
    params: Union[dict, None] = Field(title="http parameter", default={})
    timeout: int = Field(title="http request timeout", default=5)
    body_template_json_path: Union[str, None] = Field(
        title="if given, replace body with file path content", default=None
    )
    body: Union[dict, str, None] = Field(title="http body", default={})
    elapsed_milliseconds: float = Field(
        title="http request elapsed milliseconds", default=None
    )

    process_methods_prefix_split_char: str = Field(default=".")
    process_methods_prefix: str = Field(
        title="process method import prefix", default=None
    )
    pre_process_method: Union[str, list, None] = Field(
        title="process method call before send http", default=None
    )
    after_process_method: Union[str, list, None] = Field(
        title="process method call after send http", default=None
    )
    fail_msg: str = Field(title="error", default=None)
    fail_traceback: str = Field(title="traceback", default=None)

    def _exception_handle(self, e: Exception, res: Union[Response, None]):
        self.fail_traceback = traceback.format_exc()
        if res:
            self.fail_msg = res.text
        else:
            self.fail_msg = e.__str__()
        raise e

    def _read_http_body(self):
        if self.body_template_json_path:
            with open(
                "/".join(
                    self.process_methods_prefix.split(
                        self.process_methods_prefix_split_char
                    )
                )
                + self.body_template_json_path,
                "r",
                encoding="utf-8",
            ) as f:
                self.body = load(f)
        else:
            pass

    def _process_http_res(self, http_res: Response) -> Union[dict, str]:
        if http_res.status_code == 204:
            return ""
        content_type = http_res.headers.get("Content-Type", "")
        if content_type == "application/json":
            return http_res.json()
        elif content_type == "application/pdf":
            return ""
        else:
            return http_res.text

    def _format_url(self, cls: "BasePipLineTest"):
        url_formats = re.findall(self.url_format_pattern, self.url)
        if url_formats:
            for x in url_formats:
                attr_value = getattr(cls, x)
                self.url = self.url.replace("{" + x + "}", str(attr_value))

    def _send_request_data(self, cls: "BasePipLineTest") -> Response:
        request_kwargs = {
            "http_url": cls.host + self.url,
            "method": self.method if self.method else None,
            "headers": self.headers,
            "params": self.params,
            "timeout": self.timeout,
        }
        if isinstance(self.body, (dict, list)):
            request_kwargs["json"] = self.body
        elif isinstance(self.body, str):
            request_kwargs["data"] = self.body
        else:
            pass

        res = None
        try:
            res = http_request(**request_kwargs)
            res.raise_for_status()
            self.elapsed_milliseconds = res.elapsed.microseconds // 1000
            return res
        except Exception as e:
            self._exception_handle(e, res)

    def _invoke_pre_process_method(
        self, cls: "BasePipLineTest", http_res_dict: dict = {}
    ):
        if self.pre_process_method is not None:
            if isinstance(self.pre_process_method, list):
                for x in self.pre_process_method:
                    pre_process_method = import_lib(self.process_methods_prefix + x)
                    pre_process_method(
                        test_class=cls, test_step=self, http_res_dict=http_res_dict
                    )
            else:
                pre_process_method = import_lib(
                    self.process_methods_prefix + self.pre_process_method
                )
                pre_process_method(
                    test_class=cls, test_step=self, http_res_dict=http_res_dict
                )

    def _invoke_after_process_method(
        self, cls: "BasePipLineTest", http_res_dict: dict = {}
    ):
        if self.after_process_method is not None:
            if isinstance(self.after_process_method, list):
                for x in self.after_process_method:
                    after_process_method = import_lib(self.process_methods_prefix + x)
                    after_process_method(
                        test_class=cls, test_step=self, http_res_dict=http_res_dict
                    )
            else:
                after_process_method = import_lib(
                    self.process_methods_prefix + self.after_process_method
                )
                after_process_method(
                    test_class=cls, test_step=self, http_res_dict=http_res_dict
                )
        else:
            self.body = http_res_dict

    def execute(self, cls: "BasePipLineTest"):
        # use cls logger
        # cls.getLogger().debug(self.dict())

        # read http body json template file
        if self.body_template_json_path:
            self._read_http_body()

        # execute pre_process_method
        self._invoke_pre_process_method(cls=cls, http_res_dict={})

        # format url str path. convert `{var}` to actual value.
        self._format_url(cls)

        # send http request
        res = self._send_request_data(cls)

        # execute after_process_method
        self._invoke_after_process_method(
            cls=cls, http_res_dict=self._process_http_res(res)
        )


class BasePipLineTest(BaseModel):
    """base test class"""

    name: str = Field(title="test name", default=None)
    host: str = Field(title="http host")
    total_execute_round: int = Field(title="total execute round", default=1)
    test_arguments: Union[dict, None] = Field(title="execute arguments", default=None)
    test_steps_list: List[Any] = Field(title="test step lists to execute", default=[])
    test_steps_instance_list: List[BaseTestStep] = Field(
        title="test step instance list", default=[]
    )
    sleep_seconds_every_test_step: int = Field(
        title="second sleep every test step", default=None
    )
    datas_csv_title_attribute: list = Field(
        title="csv attribute title for collect test step statistic data",
        default=[
            "url",
            "method",
            "elapsed_milliseconds",
        ],
    )
    logger_name: str = Field(title="logger name", default="piplinetest")

    def _sleep_every_test_step(self):
        if self.sleep_seconds_every_test_step:
            time.sleep(self.sleep_seconds_every_test_step)

    def write_test_steps_http_statics_data(self, file_path: Path):
        result = []
        data = []
        with open(file_path, "a+", encoding="utf-8") as f:
            for x in self.test_steps_instance_list:
                data = [getattr(x, x1) for x1 in self.datas_csv_title_attribute]

                result.append(data)
            writer = csv.writer(f)
            writer.writerows(result)

    def getLogger(self) -> Logger:
        return getLogger(self.logger_name)

    def add_test_step(self, step: BaseTestStep):
        self.test_steps_list.append(step)

    def _execute(self, http_headers={}, http_body={}, http_params={}):
        headers = http_headers
        body = http_body
        params = http_params
        # init_dict.pop("test_steps_list")
        for x in self.test_steps_list:
            if issubclass(x, BasePipLineTest):
                pipline_test = x(host=self.host)
                pipline_test.execute(
                    http_headers=headers, http_body=body, http_params=params
                )
            elif issubclass(x, BaseTestStep):
                per_test_step = x(headers=headers, body=body, params=params)
                try:
                    per_test_step.execute(self)
                except Exception as e:
                    raise e
                finally:
                    self.test_steps_instance_list.append(per_test_step)
                headers = per_test_step.headers
                body = per_test_step.body
                params = per_test_step.params
                self._sleep_every_test_step()
            else:
                raise TypeError(
                    "test_steps_list item must be instance of BasePipLineTest|BasePipLineTest!"
                )

    def execute(self, http_headers=None, http_body=None, http_params=None):
        """
        invoke all `test step` in `test_steps_list`
        """
        headers = {} if http_headers is None else http_headers
        body = {} if http_body is None else http_body
        params = {} if http_params is None else http_params
        for _ in range(self.total_execute_round):
            self._execute(headers, body, params)
        # self.getLogger().debug(self.dict())
