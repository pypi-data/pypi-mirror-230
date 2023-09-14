import logging

from ._guardpoint_cardholdertypes import CardholderTypesAPI
from ._guardpoint_scheduledmags import ScheduledMagsAPI
from ._guardpoint_customizedfields import CustomizedFieldsAPI
from ._guardpoint_personaldetails import PersonalDetailsAPI
from ._guardpoint_securitygroups import SecurityGroupsAPI
from .guardpoint_connection import GuardPointConnection, GuardPointAuthType
from ._guardpoint_cards import CardsAPI
from ._guardpoint_cardholders import CardholdersAPI
from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from ._guardpoint_areas import AreasAPI
from .guardpoint_utils import url_parser

log = logging.getLogger(__name__)


class GuardPoint(GuardPointConnection, CardsAPI, CardholdersAPI, AreasAPI, SecurityGroupsAPI,
                 CustomizedFieldsAPI, PersonalDetailsAPI, ScheduledMagsAPI, CardholderTypesAPI):

    def __init__(self, **kwargs):
        # Set default values if not present
        host = kwargs.get('host', "localhost")
        port = kwargs.get('port', None)
        url_components = url_parser(host)
        if url_components['host'] == '':
            url_components['host'] = url_components['path']
            url_components['path'] = ''
        if port:
            url_components['port'] = port
        auth = kwargs.get('auth', GuardPointAuthType.BEARER_TOKEN)
        user = kwargs.get('username', "admin")
        pwd = kwargs.get('pwd', "admin")
        key = kwargs.get('key', "00000000-0000-0000-0000-000000000000")
        token = kwargs.get('token', None)
        certfile = kwargs.get('cert_file', None)
        keyfile = kwargs.get('key_file', None)
        cafile = kwargs.get('ca_file', None)
        timeout = kwargs.get('timeout', 5)
        p12_file = kwargs.get('p12_file', None)
        p12_pwd = kwargs.get('p12_pwd', "")
        super().__init__(url_components=url_components, auth=auth, user=user, pwd=pwd, key=key, token=token,
                         cert_file=certfile, key_file=keyfile, ca_file=cafile, timeout=timeout,
                         p12_file=p12_file, p12_pwd=p12_pwd)

    def get_cardholder_count(self):
        url = self.baseurl + "/odata/GetCardholdersCount"
        code, json_body = self.gp_json_query("GET", url=url)

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'totalItems' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return int(json_body['totalItems'])
