"""Flywheel client."""
import math
import os
import re
import time
import typing as t
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from random import random

from fw_http_client import HttpClient, errors
from fw_utils import AnyFile, AttrDict, open_any
from fw_utils.dicts import inflate_dotdict
from fw_utils.files import BinFile
from memoization import cached
from packaging import version

from .config import FWClientConfig

__all__ = ["FWClient"]

# cache time to live (duration to cache /api/config and /api/version response)
CACHE_TTL = 3600  # 1 hour
# global cache of drone keys (device api keys acquired via drone secret)
DRONE_DEVICE_KEYS = {}


class FWClient(HttpClient):
    """Flywheel HTTP API Client."""

    def __init__(self, config: t.Optional[FWClientConfig] = None, **kwargs) -> None:
        """Initialize FW client from the config."""
        config = config or FWClientConfig(**kwargs)
        super().__init__(config)
        self.svc_urls = {
            "/api": config.baseurl,
            "/io-proxy": config.io_proxy_url,
            "/snapshot": config.snapshot_url,
            "/xfer": config.xfer_url,
        }
        if not config.api_key and config.drone_secret:
            config.api_key = self._get_device_key(config)
        if config.api_key:
            # careful, core-api is case-sensitively testing for Bearer...
            key_type = "Bearer" if len(config.api_key) == 57 else "scitran-user"
            self.headers["Authorization"] = f"{key_type} {config.api_key}"
        self._executor: t.Optional[ThreadPoolExecutor] = None

    def _get_device_key(self, config: FWClientConfig) -> str:
        """Return device API key for the given drone_secret (cached)."""
        drone = (config.baseurl, config.device_type, config.device_label)
        if drone not in DRONE_DEVICE_KEYS:
            # limit the use of the secret only for acquiring a device api key
            headers = {
                "X-Scitran-Auth": config.drone_secret,
                "X-Scitran-Method": config.device_type,
                "X-Scitran-Name": config.device_label,
            }
            # core-api auto-creates new device entries based on type and label
            # however, it may create conflicting ones for parallel requests...
            # FLYW-17258 intended to fix and guard against that, to no avail
            # to mitigate, add some(0-1) jitter before the 1st connection
            if "PYTEST_CURRENT_TEST" not in os.environ:
                time.sleep(random())  # pragma: no cover
            # furthermore, delete redundant device entries, leaving only the 1st
            # ie. try to enforce type/label uniqueness from the client side
            type_filter = f"type={config.device_type}"
            label_filter = f"label={config.device_label}"
            query = f"filter={type_filter}&filter={label_filter}"
            for device in self.get(f"/api/devices?{query}", headers=headers)[1:]:
                self.delete(f"/api/devices/{device._id}", headers=headers)
            # legacy api keys are auto-generated and returned on the response
            # TODO generate key if not exposed after devices get enhanced keys
            # NOTE caching will need rework and move to self due to expiration
            device = self.get("/api/devices/self", headers=headers)
            DRONE_DEVICE_KEYS[drone] = device.key
        return DRONE_DEVICE_KEYS[drone]

    @property
    def executor(self) -> ThreadPoolExecutor:
        """Return thread pool executor."""
        if not self._executor:
            self._executor = ThreadPoolExecutor()
        return self._executor

    def request(self, method: str, url: str, **kwargs):  # type: ignore
        """Send request and return loaded JSON response."""
        if not url.startswith("http"):
            svc_prefix = re.sub(r"^(/[^/]+)?.*$", r"\1", url)
            # use service base url if defined
            if self.svc_urls.get(svc_prefix):
                url = f"{self.svc_urls[svc_prefix]}{url}"
            # otherwise default to self.baseurl IFF looks like a domain
            elif re.match(r".*\.[a-z]{2,}", self.baseurl):
                url = f"{self.baseurl}{url}"  # pragma: no cover
            # raise error about missing service url for known prefixes/APIs
            elif svc_prefix in self.svc_urls:
                svc_name = f"{svc_prefix[1:]}".replace("-", "_")
                msg = f"FWClient: {svc_name}_url required for {svc_prefix} requests"
                raise ValueError(msg)
            # raise error about invalid path for unknown prefixes
            else:
                raise ValueError(f"FWClient: invalid URL path prefix: {svc_prefix}")
        return super().request(method, url, **kwargs)

    @property
    def core_config(self) -> AttrDict:
        """Return Core's configuration."""
        return self.get_core_config()  # type: ignore

    @cached(ttl=CACHE_TTL)
    def get_core_config(self) -> AttrDict:
        """Return Core's configuration (cached)."""
        return self.get("/api/config")

    @property
    def core_version(self) -> t.Optional[str]:
        """Return Core's release version."""
        return self.get_core_version()  # type: ignore

    @cached(ttl=CACHE_TTL)
    def get_core_version(self) -> t.Optional[str]:
        """Return Core's release version (cached)."""
        return self.get("/api/version").get("release")

    @property
    def auth_status(self) -> AttrDict:
        """Return the client's auth status."""
        return self.get_auth_status()  # type: ignore

    @cached(ttl=CACHE_TTL)
    def get_auth_status(self) -> AttrDict:
        """Return the client's auth status (cached)."""
        status = self.get("/api/auth/status")
        if status.is_device:
            status["info"] = self.get(f"/api/devices/{status.origin.id}")
        else:
            status["info"] = self.get("/api/users/self")
        return status

    def check_feature(self, feature: str) -> bool:
        """Return True if Core has the given feature and it's enabled."""
        return bool(self.core_config.features.get(feature))  # type: ignore

    def check_version(self, min_ver: str) -> bool:
        """Return True if Core's version is greater or equal to 'min_ver'."""
        if not self.core_version:
            # assume latest on dev deployments without a version
            return True
        return version.parse(self.core_version) >= version.parse(min_ver)

    def iter_results(self, url: str, **params):
        """Yield find results from paginated listing API endpoint responses."""
        headers = {"X-Accept-Feature": "Pagination"}
        get_page = partial(self.get, url, headers=headers)
        after_id = url.startswith("/xfer") or not params.get("sort")
        while results := get_page(params=params).get("results"):
            yield from results
            if after_id:
                params["after_id"] = results[-1]["_id"]
            else:
                params["page"] = params.get("page", 1) + 1

    def store_file(
        self,
        project_id: str,
        file: t.BinaryIO,
        origin: t.Optional[dict] = None,
        content_encoding: t.Optional[str] = None,
    ) -> str:
        """Store a single file using the /api/storage/files endpoint (device only)."""
        assert self.auth_status.is_device, "Device authentication required"
        endpoint = "/api/storage/files"
        origin = origin or self.auth_status.origin
        params = {
            "project_id": project_id,
            "origin_type": origin["type"],
            "origin_id": origin["id"],
            "signed_url": True,
        }
        headers = {"Content-Encoding": content_encoding} if content_encoding else {}
        response = self.post(endpoint, params=params, headers=headers, raw=True)
        if response.ok:
            upload = response.json()
            ul_url = upload["upload_url"]
            ul_headers = {"Authorization": None, **upload.get("upload_headers", {})}
            try:
                self.put(ul_url, headers=ul_headers, data=file)
            except errors.RequestException:
                url = f"{endpoint}/{upload['storage_file_id']}"
                self.delete(url, params={"ignore_storage_errors": True})
                raise
        elif response.status_code == 409:
            del params["signed_url"]
            files = {"file": file}
            upload = self.post(endpoint, params=params, headers=headers, files=files)
        else:
            response.raise_for_status()
        return upload["storage_file_id"]

    def upload(self, meta: dict, file: AnyFile, threads: bool = True) -> dict:
        """Upload file to Flywheel."""
        meta = inflate_dotdict(meta)
        ticket = self.post("/xfer/upload", json=meta)
        upload_headers = {"Authorization": None}
        upload_headers.update(ticket.get("upload_headers", {}))

        def do_upload(args):
            part_url, part = args
            with part as data:
                return self.put(part_url, data=data, headers=upload_headers, raw=True)

        # TODO auto fill file size if possible
        full_size = meta["file"]["size"]
        part_num = len(ticket["upload_urls"])
        part_size = math.ceil(full_size / part_num)
        finish_payload = {"_id": ticket["_id"]}

        def iter_file_parts(file_: t.Union[str, BinFile]) -> t.Iterable[FilePart]:
            for i in range(part_num):
                yield FilePart(file_, i * part_size, part_size, full_size)

        with open_any(file) as r_file:
            # use thread pool executor
            # IFF there are multiple parts and data is thread-safe
            _map: t.Callable
            if r_file.localpath and part_num > 1 and threads:
                _map, parts = self.executor.map, iter_file_parts(r_file.localpath)
            # otherwise upload parts sequentially
            else:
                _map, parts = map, iter_file_parts(r_file)
            # collect upload results, we only have to do anything in case of S3 now
            for result in _map(do_upload, zip(ticket["upload_urls"], parts)):
                if ticket.get("s3_multipart_upload_id"):
                    finish_payload.setdefault("etags", [])
                    finish_payload["etags"].append(result.headers["etag"])
        return self.post(ticket["finish_url"], json=finish_payload)

    def close(self):
        """Close thread pool executor if needed and close the session."""
        if self._executor:
            self._executor.shutdown()
        super().close()


class FilePart:
    """Part of a larger file to upload.

    |___________________________________________________|
    0          |                 |              full_size
               |----part_size----|
             tell()

    Opening the underlying file object will be deferred if got a filepath
    to support multi-threading.
    """

    def __init__(
        self,
        file: t.Union[str, BinFile],
        start_byte: int,
        part_size: int,
        full_size: int,
    ) -> None:
        """Initialize file part."""
        self.file_opened = False
        self.filepath = file if isinstance(file, str) else None
        self._file = file if isinstance(file, BinFile) else None
        assert self.filepath or self._file, "expected a filepath or a BinFile instance"
        self.start_byte = start_byte
        self.full_size = full_size
        self.part_size = min(full_size - start_byte, part_size)
        self.remaining = self.part_size

    @property
    def file(self) -> BinFile:
        """Return and cache opened file object."""
        if self._file is None:
            self._file = open_any(t.cast(str, self.filepath))
            self._file.seek(self.start_byte)
            self.file_opened = True
        return self._file

    def tell(self) -> int:
        """Return current position."""
        return self.part_size - self.remaining

    def seek(self, offset: int, whence: int = 0) -> None:
        """Seek to the beginning of the file part."""
        # only support seek to the beginning of the file part
        assert offset == 0 and whence == 0  # pragma: no cover
        self.file.seek(self.start_byte)  # pragma: no cover

    def read(self, n: int = -1) -> bytes:
        """Read n bytes from the file part.

        Trying to read pass the end of the file part size
        will behave like we've reached the end of the file.
        """
        if self.remaining == 0:
            return b""

        if self.remaining < n or n < 0:
            res = self.file.read(self.remaining)
            self.remaining = 0
            return res

        self.remaining -= n  # pragma: no cover
        return self.file.read(n)  # pragma: no cover

    def __len__(self) -> int:
        """Return length of this file part."""
        return self.part_size

    def __enter__(self) -> "FilePart":
        """Enter 'with' context - seek to start."""
        self.file.seek(self.start_byte)
        return self

    def __exit__(self, exc_cls, exc_val, exc_trace) -> None:
        """Exit 'with' context - close file if it was opened by FilePart."""
        if self.file_opened:
            self.file.close()
