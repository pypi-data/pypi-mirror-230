import httpx
from typing import Dict, Any, Union, List, Optional
import os
from leapcell.exp import LeapcellException
from leapcell.version import VERSION
import urllib.parse
from functools import reduce
from leapcell.utils import multi_urljoin, build_header
from leapcell.file import LeapcellFile
from io import BytesIO

try:
    from urllib.parse import urlparse, ParseResult
except ImportError:
    from urlparse import urlparse, ParseResult  # type: ignore

MAX_CONNECTION_RETRIES = 2
TIMEOUT_SECS = 600
FILE_UPLOAD_TIMEOUT = 600
FILE_UPLOAD_MAX_SIZE = 1024 * 1024 * 3


def endpoint(resource: str, table_id: str, version="v1", name_type="id") -> str:
    return multi_urljoin("/api/", version + "/", resource + "/", "/table/", table_id)


class HTTPClient(object):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        resource: str,
        table_id: str,
        version="v1",
        name_type="id",
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._url_prefix = endpoint(
            resource, table_id, version=version, name_type=name_type
        )
        self._table_id = table_id
        self._name_type = name_type

    def _request(
        self,
        url_path: str,
        method: str,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Any] = None,
    ) -> Any:
        request = httpx.Request(
            method=method,
            url=urllib.parse.urljoin(self._base_url, url_path),
            json=data,
            files=files,
            params=params,
        )
        try:
            with httpx.Client(
                timeout=TIMEOUT_SECS,
                transport=httpx.HTTPTransport(retries=MAX_CONNECTION_RETRIES),
            ) as client:
                header = request.headers
                header.update(client.headers)
                header.update(
                    build_header(self._api_key),
                )
                request.headers = header
                result = client.send(request)
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timed out: {}".format(e)) from e
        except Exception as e:
            raise LeapcellException(
                "Error communicating with Leapcell: {}".format(e)
            ) from e

        if result.status_code != 200:
            hint = ""
            code = 0
            try:
                response = result.json()
                if "error" in response and response["error"]:
                    hint = response["error"]
                    code = response["code"]
            except ValueError:
                hint = ""
            raise LeapcellException(
                "bad request, code {}, please check apitoken and params, error code: {}, hint: {}".format(
                    result.status_code, code, hint
                )
            )
        response = result.json()

        if "data" not in response:
            raise LeapcellException(
                "bad request, code {}, please check apitoken and params, error code: {}, hint: {}".format(
                    result.status_code, response["code"], response["error"]
                )
            )
        return response["data"]

    def table_meta(self) -> Any:
        name_type = self._name_type
        return self._request(
            url_path="{}".format(self._url_prefix),
            method="GET",
            params={
                "name_type": name_type,
            },
        )

    def create_record(self, data: Dict) -> Dict[str, Any]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def create_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self._request(
            url_path="{}/record/{}".format(self._url_prefix, record_id),
            method="GET",
            params={
                "name_type": self._name_type,
            },
        )

    def get_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/query".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def update_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="PUT",
            data=data,
        )

    def update_record(
        self, record_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/{}".format(self._url_prefix, record_id),
            method="PUT",
            data=data,
        )

    def delete_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="DELETE",
            data=data,
        )

    def delete_record(self, record_id) -> Optional[Dict[str, Any]]:
        return self._request(
            url_path="{}/record/{}".format(self._url_prefix, record_id),
            method="DELETE",
        )

    def aggr_record(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/metrics".format(self._url_prefix),
            method="POST",
            data=data,
        )
    
    def search(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/search".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def upload(self, data: bytes | List[bytes]) -> LeapcellFile | List[LeapcellFile]:
        if isinstance(data, bytes):
            return self._upload(BytesIO(data))
        elif isinstance(data, list):
            return self._upload_multi([BytesIO(d) for d in data])
        else:
            raise TypeError("invalid data {}, which should be byteIO".format(data))

    def _upload(self, file: BytesIO) -> LeapcellFile:
        if file.getbuffer().nbytes > FILE_UPLOAD_MAX_SIZE:
            raise LeapcellException("file is too large, file should be less than 5KB")
        files = {"file": file}
        r = self._request(
            url_path="{}/{}".format(self._url_prefix, "upload"),
            method="POST",
            files=files,
        )
        response = r
        image_item = LeapcellFile(response.get("file", {}))
        return image_item

    def _upload_multi(self, files: List[BytesIO]) -> List[LeapcellFile]:
        upload_files = []
        for f in files:
            if f.getbuffer().nbytes > FILE_UPLOAD_MAX_SIZE:
                raise LeapcellException(
                    "file is too large, file should be less than 5KB"
                )
            upload_files.append(("files", (f)))
        r = self._request(
            url_path="{}/{}".format(self._url_prefix, "upload_multi"),
            method="POST",
            files=upload_files,
        )
        response = r
        image_item = [LeapcellFile(item) for item in response.get("files", [])]
        return image_item
