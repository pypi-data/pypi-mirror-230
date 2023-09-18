"""
This http client send run's results data to modeler back-end server
"""

from Accuinsight.modeler.store.tracking.life_cycle_store import RestStore as LcRestStore
from Accuinsight.modeler.utils.os_getenv import get_os_env
from Accuinsight.modeler.core.LcConst import LcConst

# api for experiment
class LifecycleRestApi:
    def __init__(self, host_url, port, uri):
        self.base_url = 'http://' + host_url + ':' + str(port) + '/' + uri

    def lc_create_run(self, current_run_meta):
        """Create run."""

        store = LcRestStore(self.ModelerHostCreds(self.base_url))
        run = store.lc_create_run(current_run_meta)
        return run
    class ModelerHostCreds(object):
        """
        Provides a hostname and optional authentication for talking to an back-end server.
        :param host: Hostname (e.g., http://localhost:5000) to back-end server. Required.
        :param username: Username to use with Basic authentication when talking to server.
            If this is specified, password must also be specified.
        :param password: Password to use with Basic authentication when talking to server.
            If this is specified, username must also be specified.
        :param token: Token to use with Bearer authentication when talking to server.
            If provided, user/password authentication will be ignored.
        :param ignore_tls_verification: If true, we will not verify the server's hostname or TLS
            certificate. This is useful for certain testing situations, but should never be
            true in production.
        """

        def __init__(self, host, username=None, password=None, token=None,
                     ignore_tls_verification=False):
            if not host:
                raise ValueError("host is a required parameter for ModelerHostCreds")
            self.host = host
            self.username = username
            self.password = password
            self.token = token
            self.ignore_tls_verification = ignore_tls_verification


# api for model deployment (deprecated on 3.0)
# class DeployLogRestApi:
#     def __init__(self, host_url, port, uri):
#         self.base_url = 'http://' + host_url + ':' + str(port) + '/' + uri
#
#     def call_rest_api(self, method, param, mode):
#         store = MonitoringDeployRestStore(ModelerHostCreds(self.base_url))
#         response = store.call_endpoint(method, param, mode)
#
#         return response


if __name__ == "__main__":
    env_value = get_os_env('ENV')
    modeler_rest = LifecycleRestApi(env_value[LcConst.BACK_END_API_URL],
                                    env_value[LcConst.BACK_END_API_PORT],
                                    env_value[LcConst.BACK_END_API_URI])
    modeler_rest.lc_create_run()
