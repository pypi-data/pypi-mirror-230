from __future__ import annotations

import logging
from functools import partial
from io import BytesIO
from string import capwords
from urllib.parse import urlparse

from requests import Request, Response
from requests.exceptions import HTTPError

from itkdb import exceptions, models, utils
from itkdb._version import __version__
from itkdb.core import Session
from itkdb.data import path as itkdb_data
from itkdb.responses import PagedResponse

try:
    import pycurl
except ModuleNotFoundError:
    HAS_PYCURL = False
except ImportError as imp_err:
    imp_err_msg = "There is an error importing pycurl. Please see the documentation for some hints.\n\n  https://itkdb.docs.cern.ch/0.4/meta/faq/"  # pylint: disable=invalid-name
    raise ImportError(imp_err_msg) from imp_err
else:
    HAS_PYCURL = True

log = logging.getLogger(__name__)


class Client(Session):
    """
    The top-level user-facing client for interacting with the ITk Production Database API.

    !!! note "Changed in version 0.4.0"
        - added `use_eos` argument

    !!! note "Changed in version 0.4.6"
        - added `pagination_history` argument
    """

    limit = -1

    def __init__(self, use_eos=False, pagination_history=False, **session_kwargs):
        self._use_eos = use_eos
        self._pagination_history = pagination_history
        super().__init__(**session_kwargs)

    def request(self, method, url, *args, **kwargs):
        self.limit = kwargs.pop("limit", -1)

        response = super(Session, self).request(method, url, *args, **kwargs)
        return self._response_handler(response)

    def get(self, url, **kwargs):
        is_cern_url = ".cern.ch" in urlparse(url).netloc
        # is_binary_data = "uu-app-binarystore/getBinaryData" in url
        if is_cern_url:
            log.info(
                "Identified a cern.ch request, will attach CERN SSL chain to request by overriding `verify`."
            )
            kwargs["verify"] = itkdb_data / "CERN_chain.pem"

        # getBinaryData does not handle chunked requests
        # if is_cern_url or is_binary_data:
        if is_cern_url:
            log.info(
                "Identified a request that potentially downloads larger amounts of data, will execute chunked requests (stream=True)."
            )
            kwargs["stream"] = True
            headers = kwargs.get("headers", {})
            headers["transfer-encoding"] = "chunked"
            kwargs["headers"] = headers
        return super().get(url, **kwargs)

    def _handle_warnings(self, data):
        warnings = data.pop("uuAppErrorMap", {})
        try:
            for key, message in warnings.items():
                log.warning("%s: %s", key, message)
        except AttributeError:
            # it's a string like:
            #   'uuAppErrorMap': '#<UuApp::Oidc::Session:0x00561d53890118>'
            log.warning(warnings)

    def upload_to_eos(self, response, eos_file_details=None, **_) -> None:
        """
        requests response hook function to upload a file to eos.
        """
        log.info("I was able to get a token to upload to EOS. Let me upload.")
        try:
            response.raise_for_status()
        except HTTPError:
            log.warning("Something went wrong with uploading to EOS.")
            return response

        # do nothing if betamax is being used (no need to run the cURL for EOS)
        if response.connection.__class__.__name__ == "BetamaxAdapter":
            return None

        # see _request_handler for this information
        fname, fpointer, ftype, fheaders = eos_file_details

        token_request = response.json()

        headers = {
            "Authorization": f"Bearer {token_request['token']}",
            "User-Agent": f"itkdb/{__version__}",
            "Content-Type": ftype,
            **fheaders,
        }

        buffer_header = BytesIO()
        buffer_body = BytesIO()

        curl = pycurl.Curl()
        curl.setopt(curl.URL, token_request["url"])
        curl.setopt(curl.FOLLOWLOCATION, True)
        curl.setopt(curl.UPLOAD, True)
        curl.setopt(
            curl.HTTPHEADER, [f'{capwords(k, "-")}: {v}' for k, v in headers.items()]
        )
        curl.setopt(curl.CAINFO, str((itkdb_data / "CERN_chain.pem").resolve()))
        curl.setopt(curl.READDATA, fpointer)
        curl.setopt(curl.INFILESIZE_LARGE, utils.get_filesize(fname, fpointer))
        curl.setopt(curl.HEADERFUNCTION, buffer_header.write)
        curl.setopt(curl.WRITEFUNCTION, buffer_body.write)
        curl.perform()
        curl.close()

        resp_header = buffer_header.getvalue().decode()
        resp_body = buffer_body.getvalue().decode()

        header_blocks = []
        for item in resp_header.strip().split("\r\n"):
            if item.startswith("HTTP"):
                header_blocks.append([item])
            elif item:
                header_blocks[-1].append(item)

        eos_response = Response()
        eos_response.status_code = int(header_blocks[-1][0].split()[1])
        eos_response.request = Request(
            method="PUT",
            url=token_request["url"],
            headers=headers,
            files={"file": (fname, fpointer, ftype)},
        )

        additional_message = f"  - I was not able to upload file to EOS. Please report the above information to developers.\r\n\r\n{resp_body}\r\n\r\n"
        if eos_response.status_code != 201:
            for header_block in header_blocks:
                additional_message += "\r\n".join(header_block)
                additional_message += "\r\n" + "-" * 10 + "\r\n"
            raise exceptions.ResponseException(
                eos_response, additional_message=additional_message
            )
        response.eos_response = eos_response
        return None

    def delete_from_eos(self, response, **_) -> None:
        """
        requests response hook function to delete a file from eos.
        """
        try:
            response.raise_for_status()
        except HTTPError:
            log.warning("Something went wrong with deleting the attachment.")
            return response

        data = response.json()

        # do nothing if it's not an EOS-type attachment
        # or if betamax is being used (no need to run the cURL for EOS)
        if (
            data["attachment"]["type"] != "eos"
            or response.connection.__class__.__name__ == "BetamaxAdapter"
        ):
            return None

        log.info(
            "It looks like you're deleting an attachment from ITk PD that is stored on EOS, I will try to delete it from EOS for you."
        )

        headers = {
            "Authorization": f"Bearer {data['token']}",
            "User-Agent": f"itkdb/{__version__}",
        }

        buffer_header = BytesIO()
        buffer_body = BytesIO()

        curl = pycurl.Curl()
        curl.setopt(curl.URL, data["attachment"]["url"])
        curl.setopt(curl.FOLLOWLOCATION, True)
        curl.setopt(curl.CUSTOMREQUEST, "DELETE")
        curl.setopt(
            curl.HTTPHEADER, [f'{capwords(k, "-")}: {v}' for k, v in headers.items()]
        )
        curl.setopt(curl.CAINFO, str((itkdb_data / "CERN_chain.pem").resolve()))
        curl.setopt(curl.HEADERFUNCTION, buffer_header.write)
        curl.setopt(curl.WRITEFUNCTION, buffer_body.write)
        curl.perform()
        curl.close()

        resp_header = buffer_header.getvalue().decode()
        resp_body = buffer_body.getvalue().decode()

        header_blocks = []
        for item in resp_header.strip().split("\r\n"):
            if item.startswith("HTTP"):
                header_blocks.append([item])
            elif item:
                header_blocks[-1].append(item)

        eos_response = Response()
        eos_response.status_code = int(header_blocks[-1][0].split()[1])
        eos_response.request = Request(
            method="DELETE",
            url=data["attachment"]["url"],
            headers=headers,
        )

        additional_message = f"  - I was not able to delete the file from EOS. Please report the above information to developers.\r\n\r\n{resp_body}\r\n\r\n"
        if eos_response.status_code != 204:
            for header_block in header_blocks:
                additional_message += "\r\n".join(header_block)
                additional_message += "\r\n" + "-" * 10 + "\r\n"
            raise exceptions.ResponseException(
                eos_response, additional_message=additional_message
            )
        response.eos_response = eos_response
        return None

    def _request_handler(self, request):
        if request.url == self._normalize_url("/itkdbPoisonPillTest"):
            request.url = self._normalize_url("/poison")
        elif request.url == self._normalize_url("/createComponentAttachment"):
            if not self.use_eos:
                return

            if not HAS_PYCURL:
                msg = "You are trying to upload to EOS, but you did not install itkdb[eos] or pycurl is not installed correctly."
                raise RuntimeError(msg)

            fname, fpointer, ftype, fheaders = utils.get_file_components(request.files)

            if not utils.is_eos_uploadable(fname, fpointer):
                return

            log.info(
                "It looks like you're attaching an image, root, or large file, I will try to put it on EOS for you."
            )

            # update headers
            fheaders = fheaders or {}
            request.headers.update(fheaders)

            ftype = ftype or utils.get_mimetype(fname, fpointer)

            details = {
                "type": "component",
                "id": request.data["component"],
                "title": request.data["title"],
                "description": request.data["description"],
                "filesize": utils.get_filesize(fname, fpointer),
            }

            leftover = {
                k: v
                for k, v in request.data.items()
                if k not in ["component", "title", "description"]
            }

            if leftover:
                log.warning("Ignoring user-specified data=%s", leftover)

            request.json = details
            request.data = None
            request.files = None
            request.hooks["response"] = [
                partial(
                    self.upload_to_eos,
                    eos_file_details=(fname, fpointer, ftype, fheaders),
                )
            ]
            request.url = self._normalize_url("requestUploadEosFile")
        elif request.url == self._normalize_url("/createTestRunAttachment"):
            if not self.use_eos:
                return

            if not HAS_PYCURL:
                msg = "You are trying to upload to EOS, but you did not install itkdb[eos] or pycurl is not installed correctly."
                raise RuntimeError(msg)

            fname, fpointer, ftype, fheaders = utils.get_file_components(request.files)

            if not utils.is_eos_uploadable(fname, fpointer):
                return

            log.info(
                "It looks like you're attaching an image, root, or large file, I will try to put it on EOS for you."
            )

            # update headers
            fheaders = fheaders or {}
            request.headers.update(fheaders)

            ftype = ftype or utils.get_mimetype(fname, fpointer)

            details = {
                "type": "testRun",
                "id": request.data["testRun"],
                "title": request.data["title"],
                "description": request.data["description"],
                "filesize": utils.get_filesize(fname, fpointer),
            }

            leftover = {
                k: v
                for k, v in request.data.items()
                if k not in ["component", "title", "description"]
            }

            if leftover:
                log.warning("Ignoring user-specified data=%s", leftover)

            request.json = details
            request.data = None
            request.files = None
            request.hooks["response"] = [
                partial(
                    self.upload_to_eos,
                    eos_file_details=(fname, fpointer, ftype, fheaders),
                )
            ]
            request.url = self._normalize_url("requestUploadEosFile")
        elif request.url == self._normalize_url("/createShipmentAttachment"):
            if not self.use_eos:
                return

            if not HAS_PYCURL:
                msg = "You are trying to upload to EOS, but you did not install itkdb[eos] or pycurl is not installed correctly."
                raise RuntimeError(msg)

            fname, fpointer, ftype, fheaders = utils.get_file_components(request.files)

            if not utils.is_eos_uploadable(fname, fpointer):
                return

            log.info(
                "It looks like you're attaching an image, root, or large file, I will try to put it on EOS for you."
            )

            # update headers
            request.headers.update(fheaders)

            details = {
                "type": "shipment",
                "id": request.data["shipment"],
                "title": request.data["title"],
                "description": request.data["description"],
                "filesize": utils.get_filesize(fname, fpointer),
            }

            leftover = {
                k: v
                for k, v in request.data.items()
                if k not in ["component", "title", "description"]
            }

            if leftover:
                log.warning("Ignoring user-specified data=%s", leftover)

            request.json = details
            request.data = None
            request.files = None
            request.hooks["response"] = [
                partial(
                    self.upload_to_eos,
                    eos_file_details=(fname, fpointer, ftype, fheaders),
                )
            ]
            request.url = self._normalize_url("requestUploadEosFile")
        elif request.url in [
            self._normalize_url("/deleteComponentAttachment"),
            self._normalize_url("/deleteTestRunAttachment"),
            self._normalize_url("/deleteShipmentAttachment"),
        ]:
            if not self.use_eos or not HAS_PYCURL:
                msg = "You are trying to delete an attachment that might be on EOS, but you did not install itkdb[eos] or pycurl is not installed correctly."
                raise RuntimeError(msg)

            request.hooks["response"] = [self.delete_from_eos]

    def _response_handler(self, response):
        # sometimes we don't get content-type, so make sure it's a string at least
        content_type = response.headers.get("content-type")
        if content_type is None:
            return response

        if content_type.startswith("application/json") and not response.url.endswith(
            "uu-app-binarystore/getBinaryData"
        ):
            if response.headers.get("content-length") == "0":
                return {}

            try:
                data = response.json()
                self._handle_warnings(data)
            except ValueError as err:
                raise exceptions.BadJSON(response) from err

            limit = self.limit
            self.limit = -1  # reset the limit again
            if "pageItemList" in data:
                return PagedResponse(
                    super(),
                    response,
                    history=self._pagination_history,
                    limit=limit,
                    key="pageItemList",
                )

            if "itemList" in data:
                page_info = data.get("pageInfo", None)
                if page_info and (
                    page_info["pageIndex"] * page_info["pageSize"] < page_info["total"]
                ):
                    return PagedResponse(
                        super(),
                        response,
                        history=self._pagination_history,
                        limit=limit,
                        key="itemList",
                    )
                return data["itemList"]

            if "testRunList" in data:
                return data["testRunList"]

            if "dtoSample" in data:
                return data["dtoSample"]

            return data

        # we've got a file or attachment we're downloading of some kind, so
        # dump to tempfile and seek from there to determine behavior
        binary_file = models.BinaryFile.from_response(response)
        is_cern_url = ".cern.ch" in urlparse(response.url).netloc

        if (
            is_cern_url
            and binary_file.mimetype == "application/octet-stream"
            and binary_file.content_type != "application/octet-stream"
        ):
            log.warning(
                "Changing the mimetype for the response from EOS from 'application/octet-stream' to '%s'.",
                binary_file.content_type,
            )
            binary_file._mimetype = (  # pylint: disable=protected-access
                binary_file.content_type
            )
            response.headers["content-type"] = binary_file.mimetype

        if binary_file.mimetype.startswith("image/"):
            binary_file.__class__ = models.ImageFile
        elif (
            binary_file.mimetype.startswith("text/")
            or binary_file.mimetype.startswith("text")
            or binary_file.mimetype == "application/json"
        ):
            binary_file.__class__ = models.TextFile
        elif binary_file.mimetype == "application/zip":
            binary_file = models.ZipFile(binary_file)
        else:
            log.warning(
                "No model available for Content-Type: '%s'. Defaulting to BinaryFile.",
                binary_file.mimetype,
            )

        return binary_file

    def prepare_request(self, request):
        request.url = self._normalize_url(request.url)
        self._request_handler(request)
        return super().prepare_request(request)

    @property
    def use_eos(self):
        """
        Flag indicating whether to use eos for uploading attachments.
        """
        return self._use_eos
