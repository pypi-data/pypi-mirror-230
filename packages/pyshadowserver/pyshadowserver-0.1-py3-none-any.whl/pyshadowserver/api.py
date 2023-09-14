import configparser
import csv
import hashlib
import hmac
import json
import os
from io import StringIO
from typing import Any, Dict, List, Optional, Union

import requests
from appdirs import user_data_dir


class ShadowServerException(Exception):
    pass


class InvalidConfiguration(ShadowServerException):
    pass


class MissingCredentials(ShadowServerException):
    pass


class InvalidAnswer(ShadowServerException):
    pass


class InvalidParameters(ShadowServerException):
    pass


class AccessDenied(InvalidAnswer):
    """
    Raised when an API access is denied
    """

    pass


# TODO: https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Malware-Research
class ShadowServer:
    """
    Main Shadow Server class
    """

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.config_folder = user_data_dir("ShadowServer", "ShadowServer")
        self.config_file = os.path.join(self.config_folder, "config.conf")
        self.api_key: Optional[str] = api_key
        self.api_secret: Optional[str] = api_secret
        self.uri = "https://transform.shadowserver.org/api2/"
        self.user_agent = "pyshadowserver (https://github.com/Te-k/pyshadowserver)"

    def load_config(self) -> None:
        """
        Load configuration from user config dir
        On Mac OS: /Users/USER/Library/Application Support/ShadowServer/config.conf
        On Linux: /home/trentm/.local/share/ShadowServer/config.conf
        On Windows: C:\\Users\\User\\AppData\\Local\\ShadowServer\\ShadowServer\\config.conf
        :raise InvalidConfiguration: if file doesn't exist or doesn't contain the right parameters
        """
        config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            config.read(self.config_file)
            try:
                self.api_key = config["ShadowServer"]["api_key"]
                self.api_secret = config["ShadowServer"]["api_secret"]
            except KeyError:
                raise InvalidConfiguration()
        else:
            raise InvalidConfiguration()

    def save_config(self) -> None:
        """
        Save the current configuration to the configuration file
        """
        config = configparser.ConfigParser()
        config["ShadowServer"] = {}
        config["ShadowServer"]["api_key"] = self.api_key
        config["ShadowServer"]["api_secret"] = self.api_secret

        if not os.path.isdir(self.config_folder):
            os.makedirs(self.config_folder)

        with open(self.config_file, "w") as f:
            config.write(f)

    def _post(self, path: str, data: Dict[str, str]) -> Any:
        """
        Get request
        :param path: URI path
        :param data: data to be passed
        :returns: JSON parsed data
        :raise InvalidAnswer: if API returned a non 200 code
        """
        if self.api_secret is None or self.api_key is None:
            raise MissingCredentials()
        data["apikey"] = self.api_key
        secret_bytes = bytes(str(self.api_secret), "utf-8")
        request_bytes = bytes(json.dumps(data), "utf-8")
        hmac_generator = hmac.new(secret_bytes, request_bytes, hashlib.sha256)
        headers = {"HMAC2": hmac_generator.hexdigest(), "User-Agent": self.user_agent}
        r = requests.post(self.uri + path, headers=headers, data=request_bytes)
        if r.status_code != 200:
            if r.status_code == 401:
                raise AccessDenied()
            else:
                raise InvalidAnswer(
                    "Error HTTP return code %i: %s", r.status_code, r.text
                )
        # FIXME: raise exception if invalid JSON
        return r.json()

    def _get(self, uri: str, params: Dict[str, str]) -> Any:
        """
        Unauthenticated GET request

        """
        r = requests.get(uri, params=params, headers={"User-Agent": self.user_agent})
        if r.status_code != 200:
            raise InvalidAnswer("Error HTTP return code %i: %s", r.status_code, r.text)
        return r.json()

    def asn(
        self,
        origin: Optional[str] = None,
        peer: Optional[str] = None,
        prefix: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Returns routing details for a given address or the Autonomous Systems Number (ASN)
        Unauthenticated query
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-ASN-and-Network-Queries

        :param origin: Report back the originating ASN and ASN name for the specific CIDR
        :param peer: Report back all the BGP peers for a specific CIDR
        :param prefix: Given an ASN report back all the routed CIDR
        :param query: Report back any information about the ASN
        :returns: data returned by the API
        """
        if origin is None and peer is None and prefix is None and query is None:
            raise InvalidParameters()

        params = {}
        if origin is not None:
            params["origin"] = origin
        else:
            if peer is not None:
                params["peer"] = peer
            else:
                if prefix is not None:
                    params["prefix"] = prefix
                else:
                    params["query"] = query

        return self._get("https://api.shadowserver.org/net/asn", params=params)

    def malware_query(self, samples: List[str]) -> List[Dict[str, str]]:
        """
        Returns a JSON response containing static details about the requested sample as well as antivirus vendor and signature details.

        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Malware-Query
        :param samples: list of hashes
        :returns
        """
        return self._get(
            "https://api.shadowserver.org/malware/info",
            params={"sample": ",".join(samples)},
        )

    def honeypot_common_vulnerabilities(
        self, date: str, limit: Optional[int] = None
    ) -> Any:
        """
        Access to methods in this module are limited to members of the honeypot group.
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Honeypot

        :param date:
        :param limit:
        :returns: dictionary
        """
        # FIXME: not tested
        data = {"date": date}
        if limit is not None:
            data["limit"] = limit

        return self._post("honeypot/common-vulnerabilities", data=data)

    def ping(self) -> Dict[str, str]:
        """
        Ping
        :returns: Dictionnary
        """
        return self._post("test/ping", data={})

    def reports_subscribed(self) -> List[str]:
        """
        List reports your organization is subscribted to
        Note:  most organizations will only have a single list they are subscribed to and can get data on.
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportssubscribed

        :returns: list of report names (as strings)
        """
        return self._post("reports/subscribed", data={})

    def reports_types(
        self, date: Optional[str] = None, detail: bool = False
    ) -> Union[List[Dict[str, str]] | List[str]]:
        """
        List of available types of reports.
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportstypes

        :param date: date range matching query interface
        :param detail: include details (default false)
        :returns: list of reports (as str or dictionaries if detail is True)
        """
        data = {"detail": detail}
        if date is not None:
            data["date"] = date

        return self._post("reports/types", data=data)

    def reports_list(
        self, reports: Optional[List[str]] = None, limit=50, date: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        List reports available
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportslist

        :param reports: Report types to return (optional) - note that this is a list and must be bracketed ** [ ] **
        :param limit: Limit the query to a specific number of records
        :param date: Date in format YYY-MM-DD or date range as YYYY-MM-DD:YYYY-MM-DD
        :returns:
        """
        data = {"limit": limit}
        if reports is not None:
            data["reports"] = reports
        if date is not None:
            data["date"] = date
        return self._post("reports/list", data=data)

    def reports_download_raw(self, report_id: str) -> str:
        """
        Download a report based on its id in raw format
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportsdownload

        :param report_id: id of the report
        :returns: report in string format
        """
        r = requests.get(
            "https://dl.shadowserver.org/" + report_id,
            headers={"User-Agent": self.user_agent},
        )
        if r.status_code != 200:
            raise InvalidAnswer("Error HTTP return code %i: %s", r.status_code, r.text)
        return r.text

    def reports_download(self, report_id: str) -> List[Dict[str, str]]:
        """
        Download a report and parse it
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportsdownload

        :param report_id: id of the report
        :returns: report as a structure
        """
        raw_data = self.reports_download_raw(report_id)
        data = StringIO(raw_data)
        reader = csv.reader(data)
        headers = next(reader)
        results = []
        for row in reader:
            entry = {}
            for i, v in enumerate(headers):
                entry[v] = row[i]
            results.append(entry)

        return results

    def reports_query(
        self,
        query: Dict[str, str],
        sort: Optional[str] = None,
        date: Optional[str] = None,
        facet: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """
        Returns a list of events matching the query parameters
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportsquery

        :param query: (dictionary) Search fields [any of the available fields from the reports].
        :param sort: (string) Ascending | descending
        :param date: (string) Date (YYYY-MM-DD) or range (YYYY-MM-DD:YYYY-MM-DD)
        :param facet: (string) Returns the cardinality of each value of the given field sorted from highest to lowest
        :param limit: (number) Specify the number of records to pull
        :param page: (number) Default is 1; used to obtain additional pages of results
        :returns: List of reports
        """
        data = {"query": query}
        if sort is not None:
            data["sort"] = sort
        if date is not None:
            data["date"] = date
        if facet is not None:
            data["facet"] = facet
        if limit is not None:
            data["limit"] = limit
        if page is not None:
            date["page"] = page

        return self._post("reports/query", data=data)

    def reports_stats(
        self,
        date: Optional[str] = None,
        report: Optional[Union[List[str] | str]] = None,
        report_type: Optional[Union[list[str] | str]] = None,
    ) -> List[Dict[str, Union[str | int]]]:
        """
        An API option to allow looking through the history of the statistics of the different reports
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Reports-Query#reportsstats

        :param date: (string) date or date range; default is the previous date
        :param report: (string or list) filter by report name
        :param report_type: (string or list) filter by report type
        :returns: list of dictionaries
        """
        data = {}
        if date is not None:
            data["date"] = date
        if report is not None:
            data["report"] = report
        if report_type is not None:
            data["type"] = report_type

        res = self._post("reports/stats", data=data)

        # Clean the format to return a list of dictionaries
        results = []
        headers = res[0]
        for entry in res[1:]:
            row = {}
            for i, v in enumerate(headers):
                row[v] = entry[i]

            results.append(row)

        return results

    def reports_schema(self, report_type: str) -> Dict[str, str]:
        """
        Obtain JSON schema for a given report type.

        :param report_type: (string) report type
        :returns: description of the format as a dictionary of strings
        """
        return self._post("reports/schema", data={"type": report_type})

    def trusted_program(self, hash: str) -> Dict[str, Any]:
        """
        This web-based API is a source of meta data related to known good files that we have indexed. It includes about 80 different applications Note: Rate limiting by source IP is set to 10 queries per second.
        https://github.com/The-Shadowserver-Foundation/api_utils/wiki/API:-Trusted-Programs-Query

        :param hash: hash of the file
        :returns: Dictionnary with information about the file (empty if not found)
        """
        return self._get(
            "https://api.shadowserver.org/program/trusted", params={"sample": hash}
        )
