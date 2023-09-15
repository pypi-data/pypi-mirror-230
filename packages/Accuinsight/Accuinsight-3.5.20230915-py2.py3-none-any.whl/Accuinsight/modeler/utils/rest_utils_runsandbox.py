import base64
import time
import logging
import json

import requests

from Accuinsight.__about__ import __version__
from Accuinsight.modeler.utils.string_utils import strip_suffix

RESOURCE_DOES_NOT_EXIST = 'RESOURCE_DOES_NOT_EXIST'

_logger = logging.getLogger(__name__)

_DEFAULT_HEADERS = {
    'User-Agent': 'modeler-python-client/%s' % __version__
}


def http_request(host_creds, endpoint, retries=3, retry_interval=3,
                 max_rate_limit_interval=60, **kwargs):
    """
    Makes an HTTP request with the specified method to the specified hostname/endpoint. Ratelimit
    error code (429) will be retried with an exponential back off (1, 2, 4, ... seconds) for at most
    `max_rate_limit_interval` seconds.  Internal errors (500s) will be retried up to `retries` times
    , waiting `retry_interval` seconds between successive retries. Parses the API response
    (assumed to be JSON) into a Python object and returns it.

    :param host_creds (object containing)
        hostname and optional authentication.
    :return: Parsed API response
    """
    hostname = host_creds.host
    auth_str = None
    if host_creds.username and host_creds.password:
        basic_auth_str = ("%s:%s" % (host_creds.username, host_creds.password)).encode("utf-8")
        auth_str = "Basic " + base64.standard_b64encode(basic_auth_str).decode("utf-8")
    elif host_creds.token:
        auth_str = "Bearer %s" % host_creds.token

    headers = dict(_DEFAULT_HEADERS)
    headers['Content-Type'] = 'application/json'  # Add Content-Type header

    if auth_str:
        headers['Authorization'] = auth_str

    verify = not host_creds.ignore_tls_verification

    def request_with_ratelimit_retries(max_rate_limit_interval, **kwargs):
        response = requests.request(**kwargs)
        time_left = max_rate_limit_interval
        sleep = 1
        while response.status_code == 429 and time_left > 0:
            _logger.warning(
                "API request to {path} returned status code 429 (Rate limit exceeded). "
                "Retrying in %d seconds. "
                "Will continue to retry 429s for up to %d seconds.",
                sleep, time_left)
            time.sleep(sleep)
            time_left -= sleep
            response = requests.request(**kwargs)
            sleep = min(time_left, sleep*2)  # sleep for 1, 2, 4, ... seconds;
        return response

    cleaned_hostname = strip_suffix(hostname, '/')
    url = "%s%s" % (cleaned_hostname, endpoint)
    for i in range(retries):
        # response = request_with_ratelimit_retries(max_rate_limit_interval,
        #                                           url=url, headers=headers, verify=verify, **kwargs)
        response = request_with_ratelimit_retries(max_rate_limit_interval,
                                                  url=url, headers=headers, **kwargs)
        if response.status_code >= 200 and response.status_code < 500:
            return response
        else:
            _logger.error(
                "API request to %s failed with code %s != 200, retrying up to %s more times. "
                "API response body: %s",
                url, response.status_code, retries - i - 1, response.text)
            time.sleep(retry_interval)
    raise ValueError("API request to %s failed to return code 200 after %s tries" %
                          (url, retries))


def _can_parse_as_json(string):
    try:
        json.loads(string)
        return True
    except Exception:  # pylint: disable=broad-except
        return False

def verify_rest_response(response, endpoint):
    """Verify the return code and raise exception if the request was not successful."""
    if response.status_code != 200:
        if _can_parse_as_json(response.text):
            # raise RestException(json.loads(response.text))
            raise ValueError("RestException: '%s'", response.text)
        else:
            base_msg = "API request to endpoint %s failed with error code " \
                       "%s != 200" % (endpoint, response.status_code)
            raise ValueError("%s. Response body: '%s'" % (base_msg, response.text))
    return response