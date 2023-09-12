from __future__ import annotations

from io import FileIO, IOBase
from typing import BinaryIO, Any

from requests import Request

from semantha_sdk.request.semantha_request import SemanthaRequest


def _convert_value(value: Any):
    if isinstance(value, IOBase):
        return value

    if isinstance(value, bool):
        return str(value).lower()

    return str(value)


def _filter_and_convert_to_str(data: dict, remove_empty_lists=False):
    data = {k: v for k, v in data.items() if v is not None}

    if remove_empty_lists:
        data = {k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)}

    data = {k: _convert_value(v) for k, v in data.items()}
    return data


def _filter_json(data: dict):
    data = {k: v for k, v in data.items() if v is not None}
    return data

class MediaType:
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    JSON = "application/json"
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
class RestClient:

    def __init__(self, server_url: str, api_key: str):
        self.__server_url = server_url
        self.__api_key = api_key

    def __build_headers_for_json_request(self) -> dict[str, str]:
        return {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__api_key}'
        }
        
    def __build_headers_for_request(self) -> dict[str, str]:
        return {
            'Authorization': f'Bearer {self.__api_key}'
        }

    def __request(self,
                  method,
                  url,
                  headers=None,
                  files=None,
                  data=None,
                  params=None,
                  auth=None,
                  cookies=None,
                  hooks=None,
                  json: dict | list = None
                  ) -> SemanthaRequest:
        if headers is None:
            headers = self.__build_headers_for_json_request()
        else:
            headers = {**headers, **self.__build_headers_for_request()}

        if json is not None:
            json = _filter_json(json)

        if data is not None:
            data = _filter_and_convert_to_str(data, remove_empty_lists=True)

        if files is not None:
            files = _filter_and_convert_to_str(files, remove_empty_lists=True)

        if params is not None:
            params = _filter_and_convert_to_str(params)

        headers['User-Agent'] = 'semantha Python SDK; '
        request = Request(
            method=method,
            url=self.__server_url + url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
            json=json
        )
        prepared_request = request.prepare()
        return SemanthaRequest(prepared_request)

    def get(self, url: str, q_params: dict[str, str] = None) -> SemanthaRequest:
        return self.__request("GET", url, params=q_params)

    def post(
            self,
            url: str,
            body: dict = None,
            json: dict | list = None,
            q_params: dict = None,
            headers: dict[str, str] = None,
    ) -> SemanthaRequest:
        if body is None and json is None:
            raise ValueError("Either a body (files/form-data) or a json must be provided!")
        return self.__request("POST", url, files=body, json=json, params=q_params, headers=headers)

    def delete(self, url: str, q_params: dict[str, str] = None, json: dict | list = None) -> SemanthaRequest:
        return self.__request("DELETE", url, params=q_params, json=json)

    def patch(self, url: str, body: dict = None, json: dict | list = None, q_params: dict[str, str] = None) -> SemanthaRequest:
        if body is None and json is None:
            raise ValueError("Either a body (files/form-data) or a json must be provided!")
        return self.__request("PATCH", url, files=body, json=json, params=q_params)

    def put(self, url: str, body: dict = None, json: dict | list = None, q_params: dict[str, str] = None) -> SemanthaRequest:
        if body is None and json is None:
            raise ValueError("Either a body (files/form-data) or a json must be provided!")
        return self.__request("PUT", url, files=body, json=json, params=q_params)

    def to_header(accept_mime_type: str):
        return {"Accept": accept_mime_type}
