"""Client for API V2.

See https://github.com/actigraph/StudyAdminAPIDocumentation.
"""

import base64
import hashlib
import hmac
from datetime import datetime
from email.utils import formatdate
from typing import Any, Dict, List, Union

import requests

from actiapi import ActiGraphClient

session = requests.Session()

class ActiGraphClientV2(ActiGraphClient):
    """Client for CentrePoint V2 API."""

    BASE_URL = "https://studyadmin-api.actigraphcorp.com"

    def _HMACSHA256Base64(self, message: str):
        message_bytes = bytes(message, "utf-8")
        secret = bytes(self.api_secret_key, "utf-8")
        signature = base64.b64encode(
            hmac.new(secret, message_bytes, digestmod=hashlib.sha256).digest()
        )
        return signature.decode()

    def _generate_headers(
        self,
        http_verb,
        resource_uri,
    ):
        """Formulate http headers."""
        cur_date = formatdate(timeval=None, localtime=False, usegmt=True)
        cur_date_iso = datetime.utcnow().isoformat().split(".")[0] + "Z"
        string_to_sign = "\n".join(
            [
                http_verb,
                "",
                "",
                cur_date_iso,
                "/".join([ActiGraphClientV2.BASE_URL, resource_uri]),
            ]
        )

        signed_string = self._HMACSHA256Base64(string_to_sign)

        headers = {
            "Authorization": "AGS " + self.api_access_key + ":" + signed_string,
            "Date": cur_date,
        }
        return headers

    def get_study_metadata(self, study_id: str) -> List[Dict[str, Any]]:
        """Download list of subjects and their metadata."""
        resource_uri_subject_metadata = f"v1/studies/{study_id}/subjects"
        headers_subject_metadata = self._generate_headers(
            "GET", resource_uri_subject_metadata
        )
        subject_metadata_str = session.get(
            "/".join([ActiGraphClientV2.BASE_URL, resource_uri_subject_metadata]),
            headers=headers_subject_metadata,stream=False,
        )
        subject_metadata = subject_metadata_str.json()
        return subject_metadata

    def get_files(self, subject_id) -> List[Dict[str, Any]]:
        """Get file list for given subject."""
        resource_uri_subject_rawdata = "v1/subjects/" + str(subject_id) + "/dataFiles"
        headers_subject_rawdata = self._generate_headers(
            "GET", resource_uri_subject_rawdata
        )
        subject_rawdata = session.get(
            "/".join([ActiGraphClientV2.BASE_URL, resource_uri_subject_rawdata]),
            headers=headers_subject_rawdata,stream=False
        ).json()

        return subject_rawdata["RAW"]

    def get_url(self, data_file_id) -> str:
        """Get the URL for a file based on its id."""
        resource_uri_rawdata_url = f"v1/datafiles/{data_file_id}/DownloadUrl"
        headers_rawdata_url = self._generate_headers("GET", resource_uri_rawdata_url)
        rawdata_url = session.get(
            "/".join([ActiGraphClientV2.BASE_URL, resource_uri_rawdata_url]),
            headers=headers_rawdata_url,stream=False,
        )

        rawdata_dict = rawdata_url.json()
        return rawdata_dict["DownloadURL"]

    def get_daily_summary(self, subject_id: Union[int, str]) -> List[Dict[str, Any]]:
        """Return daily summary data.

        Parameters
        ----------
        user:
            Global user_id
        """
        resource_uri_subject_rawdata = "v1/subjects/" + str(subject_id) + "/daystats"
        headers_subject_rawdata = self._generate_headers(
            "GET", resource_uri_subject_rawdata
        )
        subject_rawdata = session.get(
            "/".join([ActiGraphClientV2.BASE_URL, resource_uri_subject_rawdata]),
            headers=headers_subject_rawdata, stream=False,
        ).json()

        return subject_rawdata
