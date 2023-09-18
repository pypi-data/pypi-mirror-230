import base64
import os
import re
import sys
import time

import requests as request

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../api", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../api", "..", "..", "..")))
from requests.auth import AuthBase
from netskope_api.iterator.const import Const

import logging

logger = logging.getLogger()


class AuthToken(AuthBase):
    """Netskope-API-Token Auth for header token."""

    def __init__(self, token):
        """Initialize the object."""
        self.token = token

    def __call__(self, req):
        """Set Netskope-Api-Token in request"""
        req.headers["Netskope-Api-Token"] = "{}".format(self.token)
        return req


class NetskopeTokenManagemenClient:
    """TokenManagemen client for netskope web transactions"""

    def __init__(self, params):
        """

        :param params:
        """

        configs = {
            "base_url": "https://{}".format(params.get(Const.NSKP_TENANT_HOSTNAME))
        }
        self.token = params.get(Const.NSKP_TOKEN)
        self.user_agent = params.get(Const.NSKP_USER_AGENT)

        if not self.user_agent:
            self.user_agent = "TokenManagement-Client-{}".format(params.get(Const.NSKP_TENANT_HOSTNAME))

        headers = {
            "User-Agent": self.user_agent
        }

        self.configs = configs
        self.session = request.Session()
        self.session.headers.update(headers)
        self.session.proxies = params.get(Const.NSKP_PROXIES)
        self.session.auth = AuthToken(self.token)

    # Construct the url
    def build_url(self):
        """
        :return The Token management API to be called:
        """
        base_url = self.configs.get("base_url")
        url = "{}/api/v2/events/token/transaction_events".format(base_url)
        return url

    # Construct the regenerate url
    def build_regenerate_url(self):
        """
        :return The Token management API to regenerate credentials be called:
        """
        base_url = self.configs.get("base_url")
        url = "{}/api/v2/events/token/transaction_events?regenerate=true".format(base_url)
        return url

    def get(self):
        """
        :return Response objects.
        """
        url = self.build_url()
        logger.info("Get token response, url {} ".format(url))
        res = self.session.get(url=url, timeout=120)
        self.honor_rate_limiting(res.headers)
        token_response = self.format_response(res)
        return token_response

    def regenerate_and_get(self):
        """
        :return Response objects after regenerating subscription key and path.
        """

        url = self.build_regenerate_url()
        res = self.session.get(url=url, timeout=120)
        self.honor_rate_limiting(res.headers)
        token_response = self.format_response(res)
        return token_response

    def honor_rate_limiting(self, headers):
        """
        Identify the response headers carrying the rate limiting value.
        If the rate limit remaining for this endpoint is 0 then wait for the rate limit reset time before sending the response to the client.
        """
        try:
            if Const.RATELIMIT_REMAINING in headers:
                remaining = headers[Const.RATELIMIT_REMAINING]
                if int(remaining) <= 0:
                    logger.warning("Rate limiting reached for the endpoint config {} ".format(self.configs))
                    if Const.RATELIMIT_RESET in headers:
                        time.sleep(int(headers[Const.RATELIMIT_RESET]))
                    else:
                        # if the RESET value does not exist in the header then
                        # sleep for default 1 second as the rate limit remaining is 0
                        time.sleep(1)
        except ValueError as ve:
            logger.error("Value error when honoring the rate limiting wait time {} {}".format(headers, str(ve)))

    def format_response(self, response):
        try:
            final_response = {}
            if response.status_code == Const.SUCCESS_OK_CODE:
                resp_dict = response.json()
                if "result" in resp_dict:
                    result = resp_dict["result"]
                    if "subscription-key" in result:
                        sub_key_resp = result["subscription-key"]
                        decoded_resp = base64.b64decode(sub_key_resp).decode('utf-8').strip()
                        final_response["subscription-key"] = decoded_resp
                    if "subscription" in result:
                        sub_path_resp = result["subscription"]
                        self.validate_lite_subscription(sub_path_resp)
                        final_response["subscription"] = sub_path_resp
                        final_response["ok"] = 1
                    return final_response
            else:
                final_response = {"ok": 0, "status": response.status_code, "error_msg": response.text}
                return final_response
        except ValueError as ve:
            logger.error("Value error when formatting response {} {}".format(response, str(ve)))

    def validate_lite_subscription(self, path):
        regex = r"^projects/[^/]+/locations/[^/]+/subscriptions/[^/]+$"

        if not re.match(regex, path):
            raise ValueError("Incorrect Subscription path format. Valid format: "
                             "projects/<project-id>/locations/<region-id>-<zone-id>/subscriptions/<subscription-name>")
