""" Communication with the \*.Main uuSubApp. """

import datetime
import http.client
import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Union

import requests
from requests_toolbelt import user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder

import uun_iot

logger = logging.getLogger(__name__)

TOKEN_LEEWAY = 60  # [s] - leeway between Client and Server Clock


class CommandError(Exception):
    def __init__(self, status, uu_app_error_map):
        super(__class__, self).__init__(uu_app_error_map)
        self._status = status
        self._code = list(uu_app_error_map.keys())[0]
        self._message = uu_app_error_map[self._code]["message"]

    def __str__(self):
        return str(self._status) + "," + self._code + "," + self._message


class UuAppClient:
    """Library functions for communication and authentication with uuApp.

    The class gets a dictionary ``config`` containing the configuration of the application.
    The (root) keys and subkeys of interest to this class are

        - ``uuApp``: information about server uuApp

            - ``gateway``: domain gateway of the corresponding uuApp
            - ``uuAppName``: full name of the uuApp
            - ``awid``
            - ``uuCmdList``: containing uuCmd endpoint. The keys are not used
              by :class:`UuAppClient` class - they are used by the application
              user modules (most commonly specified in Python package path
              ``<package_name>/modules/__init__.py``.

        - ``uuThing``: authentication information about the IoT gateway

            - ``uuIdentity``
            - ``accessCode1``
            - ``accessCode2``

        - ``oidcGrantToken``: information about the authentication token
          service used in server communication

            - ``gateway``: (usually ``uuidentity.plus4u.net``) domain gateway of the `OIDC` service
            - ``uuAppName``: (usually ``uu-oidc-maing02``) full name of the `OIDC` uuApp
            - ``awid``
            - ``clientId``
            - ``clientSecret``
            - ``uuCmd``: (usually ``oidc/grantToken``) uuCmd enpoint for token granting
            - ``tokenPath``: (usually ``./oidc-token``) filesystem location (on
              the IoT gateway) where the token will be saved

    Args:
        config: dictionary with configuration, see above
    """

    _config: dict
    _token: Optional[str]

    def __init__(self, config: dict):
        self._config = config
        self._token = None
        self._token_expires_at = None
        self._user_agent = user_agent("uun-iot", uun_iot.__version__)

        if (
            "uuApp" in self._config
            and "uuThing" in self._config
            and "oidcGrantToken" in self._config
        ):
            self._refresh_token()
        else:
            logger.info(
                "UuApp connection & gateway authentication is not "
                "defined in the configuration file. Are you sure, you do not "
                "want to use the connection? It will not be possible to "
                "issue requests to uu servers."
            )
            logger.debug("Not granting any auth token.")

    def _store_token(self, token_json: dict) -> None:
        with open(self._config["oidcGrantToken"]["tokenPath"], "w") as file:
            file.write(json.dumps(token_json))

    def _refresh_token(self) -> bool:
        """Returns False if token refresh was not needed - iff token is
        already loaded. Refresh token and return True otherwise."""

        if self._token is None:
            # load from file
            token_path = self._config["oidcGrantToken"]["tokenPath"]
            try:
                with open(token_path) as json_file:
                    token = json.load(json_file)
                    self._token = token["id_token"]
                    self._token_expires_at = token["expires_at"]

                logger.debug(
                    "loaded token from %s, expires at [%s]",
                    token_path,
                    datetime.datetime.fromtimestamp(self._token_expires_at),
                )
            except IOError:
                logger.debug("loading token from %s failed, file not found", token_path)

        current_time = TOKEN_LEEWAY + int(time.time())

        if self._token_expires_at is None or self._token_expires_at < current_time:
            # token expired
            self._grant_token()
            logger.debug(
                "granted new token, expires at [%s]",
                datetime.datetime.fromtimestamp(self._token_expires_at),
            )
            return True

        return False

    def _grant_token(self) -> None:
        """Grant token.

        Refresh and save the new token.

        Raises:
            CommandError: [TODO:description]
        """
        scope_host = self._config["uuApp"]["gateway"]
        scope_context = self._config["uuApp"]["uuAppName"]
        scope_awid = self._config["uuApp"]["awid"]

        post_data = {
            "grant_type": "password",
            "username": None,
            "password": None,
            "accessCode1": self._config["uuThing"]["accessCode1"],
            "accessCode2": self._config["uuThing"]["accessCode2"],
            "scope": f"openid https://{scope_host}/{scope_context}/{scope_awid}",
        }

        # does not matter if these are not present - not required - depends on server settings
        try:
            post_data.update(
                {
                    "client_id": self._config["oidcGrantToken"]["clientId"],
                    "client_secret": self._config["oidcGrantToken"]["clientSecret"],
                }
            )
        except KeyError:
            pass

        headers = {"Content-Type": "application/json", "User-Agent": self._user_agent}

        gateway = self._config["oidcGrantToken"]["gateway"]
        uu_app_name = self._config["oidcGrantToken"]["uuAppName"]
        awid = self._config["oidcGrantToken"]["awid"]
        uucmd = self._config["oidcGrantToken"]["uuCmd"]

        conn = http.client.HTTPSConnection(gateway)
        uri = "/%s/%s/%s" % (uu_app_name, awid, uucmd)
        conn.request("POST", uri, json.dumps(post_data), headers)
        response = conn.getresponse()

        if response.status >= 200 and response.status < 300:
            token_json = json.loads(response.read())
            self._token = token_json["id_token"]

            token_json["expires_at"] = int(time.time()) + int(token_json["expires_in"])
            self._token_expires_at = token_json["expires_at"]
            self._store_token(token_json)
        else:
            status = response.status
            error_json = json.loads(response.read())
            raise CommandError(status, error_json["uuAppErrorMap"])

    def _get_full_url(self, uucmd: str) -> str:
        gateway = self._config["uuApp"]["gateway"]
        uu_app_name = self._config["uuApp"]["uuAppName"]
        awid = self._config["uuApp"]["awid"]

        uri = "/%s/%s/%s" % (uu_app_name, awid, uucmd)
        return "https://%s%s" % (gateway, uri)

    def get_request(
        self,
        uucmd: str,
        dto_in: dict = {},
        http_error_level: Optional[int] = logging.WARNING,
    ) -> requests.Response:
        """GET request with oidc2 authentication.

        Args:
            uucmd: uuCmd path of the target uuApp
            dto_in: data to be passed as JSON input to the uuApp
            http_error_level: logging library level of HTTP error (HTTP status
                code not in 200 category), default logging.WARNING
        """
        self._refresh_token()

        headers = {
            "Authorization": "Bearer " + self._token,
            "Content-type": "application/json",
            "User-Agent": self._user_agent,
        }

        full_url = self._get_full_url(uucmd)

        logger.debug("`%s` GET request, payload: %s", uucmd, dto_in)
        response = requests.get(full_url, headers=headers, json=dto_in, timeout=20)

        if http_error_level is not None:
            if not 200 <= response.status_code < 300 and http_error_level is not None:
                logger.log(
                    http_error_level,
                    "`%s` GET response (%s): %s",
                    uucmd,
                    response.status_code,
                    response.text,
                )

        return response

    def get(
        self, uucmd: str, dto_in: dict = {}, log_level: int = logging.WARNING
    ) -> Tuple[Optional[requests.Response], Tuple[bool, Optional[requests.RequestException]]]:
        """Get request

        Get request using a Bearer token. Connection errors are suppressed, logged and returned.

        Args:
            uucmd: UuCmd in relative path format, eg. "gateway/heartbeat"
            dto_in: data to send
            log_level: optional logging level for possible exceptions

        Returns:
            Tuple ``(response, (ok, exc))``,
                :class:`requests.Response` response, ``None`` if exception was raised
                boolean ``ok`` is True if no exception was encountered, False otherwise
                :class:`requests.RequestException` exc is None if no exception
                    during request was raised
        """

        response = None
        ok = False
        exc = None
        try:
            response = self.get_request(uucmd, dto_in, http_error_level=None)
            response.raise_for_status()
            ok = True
        except requests.HTTPError as e:
            logger.log(
                log_level,
                "`%s` GET response (%s): %s",
                uucmd,
                response.status_code,
                response.text,
            )
            exc = e
        except requests.RequestException as e:
            logger.log(log_level, "`%s` GET RequestException: %s", uucmd, str(e))
            exc = e

        return response, (ok, exc)

    def post_request(
        self,
        uucmd: str,
        dto_in: dict = {},
        http_error_level: Optional[int] = logging.WARNING,
    ) -> requests.Response:
        """POST request with oidc2 authentication.

        Args:
            uucmd: uuCmd path of the target uuApp
            dto_in: data to be passed as JSON input to the uuApp
            http_error_level: logging library level of HTTP error (HTTP status
                code not in 200 category), default logging.WARNING
        """
        self._refresh_token()

        headers = {
            "Authorization": "Bearer " + self._token,
            "Content-type": "application/json",
            "User-Agent": self._user_agent,
        }

        full_url = self._get_full_url(uucmd)

        logger.debug("`%s` POST request, payload: %s", uucmd, dto_in)
        response = requests.post(full_url, headers=headers, json=dto_in)

        if http_error_level is not None:
            if not 200 <= response.status_code < 300 and http_error_level is not None:
                logger.log(
                    http_error_level,
                    "`%s` POST response (%s): %s",
                    uucmd,
                    response.status_code,
                    response.text,
                )

        return response

    def post(
        self, uucmd: str, dto_in: dict = {}, log_level: int = logging.WARNING
    ) -> Tuple[Optional[requests.Response], Tuple[bool, Optional[requests.RequestException]]]:
        """Post request

        Post request using a Bearer token. Connection errors are suppressed, logged and returned.

        Args:
            uucmd: UuCmd in relative path format, eg. "gateway/heartbeat"
            dto_in: data to send
            log_level: optional logging level for possible exceptions

        Returns:
            Tuple ``(response, (ok, exc))``,
                :class:`requests.Response` response, ``None`` if exception was raised
                boolean ``ok`` is True if no exception was encountered, False otherwise
                :class:`requests.RequestException` exc is None if no exception
                    during request was raised
        """

        response = None
        ok = False
        exc = None
        try:
            response = self.post_request(uucmd, dto_in, http_error_level=None)
            response.raise_for_status()
            ok = True
        except requests.HTTPError as e:
            logger.log(
                log_level,
                "`%s` POST response (%s): %s",
                uucmd,
                response.status_code,
                response.text,
            )
            exc = e
        except requests.RequestException as e:
            logger.log(log_level, "`%s` POST RequestException: %s", uucmd, str(e))
            exc = e

        return response, (ok, exc)

    def multipart_request(
        self, uucmd: str, dto_in: dict, http_error_level: Optional[int] = logging.WARNING
    ):
        """POST request with oidc2 authentication and MULTIPART encoded data
        with oidc2 authentication. Useful for sending binary data (images, ...). See
        https://toolbelt.readthedocs.io/en/latest/user.html#multipart-form-data-encoder
        for information about multipart encoder.

        Args:
            uucmd: uuCmd path of the target uuApp
            dto_in: data to be encoded in streaming multipart form-data object to the uuApp
            http_error_level: logging library level of HTTP error (HTTP status
                code not in 200 category), default logging.WARNING
        """
        self._refresh_token()

        full_url = self._get_full_url(uucmd)

        multipart_encoded = MultipartEncoder(fields=dto_in)
        headers = {
            "Authorization": "Bearer " + self._token,
            "Content-Type": multipart_encoded.content_type,
            "User-Agent": self._user_agent,
        }
        response = requests.post(full_url, headers=headers, data=multipart_encoded)

        if http_error_level is not None:
            if not 200 <= response.status_code < 300 and http_error_level is not None:
                logger.log(
                    http_error_level,
                    "`%s` MULTIPART response (%s): %s",
                    uucmd,
                    response.status_code,
                    response.text,
                )

        return response

    def multipart(
        self, uucmd: str, dto_in: dict = {}, log_level: int = logging.WARNING
    ) -> Tuple[Optional[requests.Response], Tuple[bool, Optional[requests.RequestException]]]:
        """Multipart request

        Multipart request using a Bearer token. Connection errors are suppressed, logged and returned.

        Args:
            uucmd: UuCmd in relative path format, eg. "gateway/heartbeat"
            dto_in: data to send
            log_level: optional logging level for possible exceptions

        Returns:
            Tuple ``(response, (ok, exc))``,
                :class:`requests.Response` response, ``None`` if exception was raised
                boolean ``ok`` is True if no exception was encountered, False otherwise
                :class:`requests.RequestException` exc is None if no exception
                    during request was raised
        """

        response = None
        ok = False
        exc = None
        try:
            response = self.multipart_request(uucmd, dto_in, http_error_level=None)
            response.raise_for_status()
            ok = True
        except requests.HTTPError as e:
            logger.log(
                log_level,
                "`%s` POST response (%s): %s",
                uucmd,
                response.status_code,
                response.text,
            )
            exc = e
        except requests.RequestException as e:
            logger.log(log_level, "`%s` POST RequestException: %s", uucmd, str(e))
            exc = e

        return response, (ok, exc)


class UuCmdSession:
    """Send all data with UuCmd in one session to prevent multiple connections."""

    def __init__(self, uuclient, uucmd, http_error_level=logging.WARNING):
        self._uucmd = uucmd
        self._loglevel = http_error_level

        uuclient._refresh_token()
        self._url = uuclient._get_full_url(uucmd)

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": "Bearer " + uuclient._token,
                "Content-type": "application/json",
                "User-Agent": uuclient._user_agent,
            }
        )

    def get(
        self, data
    ) -> Tuple[Optional[requests.Response], Tuple[bool, Optional[requests.RequestException]]]:
        """Get request."""
        logger.debug("`%s` GET request, payload: %s", self._uucmd, data)

        response = None
        ok = False
        exc = None
        try:
            response = self._session.post(self._url, json=data)
            response.raise_for_status()
            ok = True
        except requests.HTTPError as e:
            logger.log(
                self._loglevel,
                "`%s` POST response (%s): %s",
                self._uucmd,
                response.status_code,
                response.text,
            )
            exc = e
        except requests.RequestException as e:
            logger.log(
                self._loglevel, "`%s` POST RequestException: %s", self._uucmd, str(e)
            )
            exc = e

        return response, (ok, exc)

    def get_raw(self, data) -> Tuple[requests.Response, bool]:
        """Get request."""
        logger.debug("`%s` GET request, payload: %s", self._uucmd, data)

        response = self._session.get(self._url, json=data)

        if not 200 <= response.status_code < 300:
            logger.log(
                self._loglevel,
                "`%s` GET response (%s): %s",
                self._uucmd,
                response.status_code,
                response.text,
            )
            return response, False

        return response, True

    def post(
        self, data
    ) -> Tuple[Optional[requests.Response], Tuple[bool, Optional[requests.RequestException]]]:
        """Post request."""
        logger.debug("`%s` POST request, payload: %s", self._uucmd, data)

        response = None
        ok = False
        exc = None
        try:
            response = self._session.post(self._url, json=data)
            response.raise_for_status()
            ok = True
        except requests.HTTPError as e:
            logger.log(
                self._loglevel,
                "`%s` POST response (%s): %s",
                self._uucmd,
                response.status_code,
                response.text,
            )
            exc = e
        except requests.RequestException as e:
            logger.log(
                self._loglevel, "`%s` POST RequestException: %s", self._uucmd, str(e)
            )
            exc = e

        return response, (ok, exc)

    def post_raw(self, data) -> Tuple[requests.Response, bool]:
        logger.debug("`%s` POST, payload: %s", self._uucmd, data)

        response = self._session.post(self._url, json=data)

        if not 200 <= response.status_code < 300:
            logger.log(
                self._loglevel,
                "`%s` GET response (%s): %s",
                self._uucmd,
                response.status_code,
                response.text,
            )
            return response, False

        return response, True


#
#    def post_ok(self, data) -> Tuple[requests.Response|requests.RequestException|None, bool]
#
#    def post(self, data) -> Tuple[requests.Response|requests.RequestException|None, bool]:
#        logger.debug("`%s` POST, payload: %s", self._uucmd, data)
#
#        ok = False
#        try:
#            response = self._session.post(self._url, json=data)
#            response.raise_for_status()
#            ok=True
#        except requests.HTTPError:
#            logger.log(self._loglevel, "`%s` POST response (%s): %s", self._uucmd, response.status_code, response.text)
#        except requests.RequestException as e:
#            response = None
#            logger.log(self._loglevel, "`%s` POST RequestException: %s", self._uucmd, str(e))
#
#        return response, ok
#
