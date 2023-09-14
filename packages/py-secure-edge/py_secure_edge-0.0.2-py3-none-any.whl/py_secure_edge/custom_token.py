import datetime
from urllib.parse import urlparse

import jwt
import ksuid
import jwt.utils as utils


class ViewerAttributes:

    def __init__(self):
        self.country = ''
        self.region = ''
        self.sessionId = ''
        self.headers = dict()
        self.query_strings = dict()


class TokenPolicy:

    def __init__(self):
        self.country = False
        self.region = False
        self.session = False
        self.expiry = datetime.timedelta(hours=24)
        self.first_access_expiry = datetime.timedelta(minutes=5)
        self.headers = ['user-agent', 'referer']
        self.query_strings = []


class CustomToken:

    def __init__(self, secrets: dict):
        self.secrets = secrets
        self.algorithm = "HS256"

    def generate_url(self, url_str, key_id, token_policy: TokenPolicy, viewer_attrs: ViewerAttributes):
        claims = {
            "co": False,
            "reg": False,
            "ssn": False,
            "headers": [],
            "qs": [],
            "exp": datetime.datetime.timestamp((datetime.datetime.now() + token_policy.expiry)),
            "faExp": datetime.datetime.timestamp((datetime.datetime.now() + token_policy.first_access_expiry)),
        }

        int_sig_input = ''
        if token_policy.country:
            claims["co"] = True
            int_sig_input = "{}{}:".format(int_sig_input, viewer_attrs.country)

        if token_policy.region:
            claims["reg"] = True
            int_sig_input = "{}{}:".format(int_sig_input, viewer_attrs.region)
        session_id = ''
        if token_policy.session:
            claims["ssn"] = True
            session_id = viewer_attrs.sessionId if viewer_attrs.sessionId else ksuid.ksuid()
            int_sig_input = "{}{}:".format(int_sig_input, session_id)

        if len(token_policy.headers) > 0:
            payload_headers = []
            for header in token_policy.headers:
                payload_headers.append(header)
                if viewer_attrs.headers[header]:
                    int_sig_input = "{}{}:".format(int_sig_input, viewer_attrs.headers[header])
            claims["headers"] = payload_headers

        if len(token_policy.query_strings) > 0:
            payload_qs = []
            for qs in token_policy.query_strings:
                payload_qs.append(qs)
                if viewer_attrs.query_strings[qs]:
                    int_sig_input = "{}{}:".format(int_sig_input, viewer_attrs.query_strings[qs])
            claims["qs"] = payload_qs

        if int_sig_input:
            int_sig_input = int_sig_input[0:-1]
            alg_obj = jwt.get_algorithm_by_name(self.algorithm)
            key = alg_obj.prepare_key(self.secrets[key_id])
            signature = alg_obj.sign(int_sig_input.encode('utf-8'), key)
            claims["intsig"] = utils.base64url_encode(signature).decode('utf-8')

        token = jwt.encode(claims, self.secrets[key_id], algorithm=self.algorithm,
                           headers={"kid": key_id})
        url = urlparse(url_str)
        return "{}://{}/{}.{}{}".format(url.scheme, url.hostname, session_id, token, url.path) \
            if session_id else "{}://{}/{}{}".format(url.scheme, url.hostname, token, url.path)

