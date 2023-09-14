import json
import uuid
from datetime import datetime, timedelta, timezone
from struct import unpack
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from dql.dataset import DatasetStats

T = TypeVar("T")
LsData = Optional[List[Dict[str, Any]]]
DatasetInfoData = Optional[Dict[str, Any]]
DatasetStatsData = Optional[DatasetStats]
DatasetRowsData = Optional[Iterable[Dict[str, Any]]]


def _parse_dates(obj: Dict, date_fields: List[str]):
    """
    Function that converts string ISO dates to datetime.datetime instances in object
    """
    for date_field in date_fields:
        if obj.get(date_field):
            obj[date_field] = datetime.fromisoformat(obj[date_field])


class Response(Generic[T]):
    def __init__(self, data: T, ok: bool, message: str) -> None:
        self.data = data
        self.ok = ok
        self.message = message


class StudioClient:
    def __init__(
        self, url: str, username: str, token: str, timeout: float = 3600.0
    ) -> None:
        self._check_dependencies()
        self.url = url.rstrip("/")
        self.username = username
        self.token = token
        self.timeout = timeout

    def _check_dependencies(self) -> None:
        try:
            # pylint: disable=unused-import
            import msgpack  # noqa: F401
            import requests  # noqa: F401
        except ImportError as exc:
            raise Exception(
                f"Missing dependency: {exc.name}\n"
                "To install run:\n"
                "\tpip install 'dql-alpha[remote]'"
            )

    def _send_request_msgpack(self, route: str, data: Dict[str, Any]) -> Response[Any]:
        import msgpack
        import requests

        response = requests.post(
            f"{self.url}/{route}",
            json={**data, "team_name": self.username},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {self.token}",
            },
            timeout=self.timeout,
        )
        ok = response.ok
        content = msgpack.unpackb(response.content, ext_hook=self._unpacker_hook)
        response_data = content.get("data")
        if ok and response_data is None:
            message = "Indexing in progress"
        else:
            message = content.get("message", "")
        return Response(response_data, ok, message)

    def _send_request(self, route: str, data: Dict[str, Any]) -> Response[Any]:
        import requests

        response = requests.post(
            f"{self.url}/{route}",
            json={**data, "team_name": self.username},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {self.token}",
            },
            timeout=self.timeout,
        )
        ok = response.ok
        data = json.loads(response.content.decode("utf-8"))
        if not ok:
            message = data.get("message", "")
        else:
            message = ""

        return Response(data, ok, message)

    def _send_streaming_request(
        self, route: str, data: Dict[str, Any]
    ) -> Iterator[Response[Any]]:
        import requests

        s = requests.Session()

        with s.post(
            f"{self.url}/{route}",
            json={**data, "team_name": self.username},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {self.token}",
            },
            timeout=self.timeout,
            stream=True,
        ) as response:
            ok = response.ok  # type: ignore [attr-defined]
            if not ok:
                data = json.loads(
                    response.content.decode("utf-8")  # type: ignore [attr-defined]
                )
                message = data.get("message", "")
                yield Response(data, ok, message)
                return

            for line in response.iter_lines():  # type: ignore [attr-defined]
                yield Response(json.loads(line.decode("utf-8")), ok, "")

    @staticmethod
    def _unpacker_hook(code, data):
        import msgpack

        if code == 42:  # for parsing datetime objects
            has_timezone = False
            timezone_offset = None
            if len(data) == 8:
                # we send only timestamp without timezone if data is 8 bytes
                values = unpack("!d", data)
            else:
                has_timezone = True
                values = unpack("!dl", data)

            timestamp = values[0]
            if has_timezone:
                timezone_offset = values[1]
                return datetime.fromtimestamp(
                    timestamp, timezone(timedelta(seconds=timezone_offset))
                )
            else:
                return datetime.fromtimestamp(timestamp)

        return msgpack.ExtType(code, data)

    def ls(self, paths: Iterable[str]) -> Iterator[Tuple[str, Response[LsData]]]:
        # TODO: change LsData (response.data value) to be list of lists
        # to handle cases where a path will be expanded (i.e. globs)
        response: Response[LsData]
        for path in paths:
            response = self._send_request_msgpack("ls", {"source": path})
            yield path, response

    def dataset_info(self, name: str) -> Response[DatasetInfoData]:
        def _parse_dataset_info(dataset_info):
            _parse_dates(dataset_info, ["created_at", "finished_at"])
            for version in dataset_info.get("versions"):
                _parse_dates(version, ["created_at"])

            return dataset_info

        response = self._send_request("dataset-info", {"dataset_name": name})
        if response.ok:
            response.data = _parse_dataset_info(response.data)
        return response

    def dataset_rows(
        self, name: str, version: int
    ) -> Iterator[Response[DatasetRowsData]]:
        def _parse_row(row):
            row["id"] = uuid.UUID(row["id"])
            row["parent_id"] = uuid.UUID(row["parent_id"])
            _parse_dates(row, ["last_modified"])

            return row

        for response in self._send_streaming_request(
            "dataset-rows", {"dataset_name": name, "dataset_version": version}
        ):
            if response.ok:
                response.data = [_parse_row(r) for r in response.data]
            yield response

    def dataset_stats(self, name: str, version: int) -> Response[DatasetStatsData]:
        response = self._send_request(
            "dataset-stats", {"dataset_name": name, "dataset_version": version}
        )
        if response.ok:
            response.data = DatasetStats(**response.data)
        return response
