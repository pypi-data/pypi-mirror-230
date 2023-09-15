import json
import logging

from Accuinsight.modeler.store.tracking.lc_abstract_store import AbstractStore as LcAbstractStore
from Accuinsight.modeler.utils.os_getenv import get_os_env
from Accuinsight.modeler.core.Run.ParseRun import BaseParser
from Accuinsight.modeler.core.Run.RunInfo.RunInfo import dict_to_list
from Accuinsight.modeler.core.LcConst.LcConst import SOURCE_FILE_GIT_META, PYTHON_DEPENDENCY, SOURCE_FILE_GIT_REPO, \
    SOURCE_FILE_GIT_COMMIT_ID, RUN_RESULT_PATH, RUN_MODEL_SHAP_JSON_PATH
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.modeler.utils.rest_utils_runsandbox import http_request, verify_rest_response


def _set_run_info_dict(current_run_meta, user_sso_id):
    model_path = ''
    json_path = ''

    if current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH] is not None:
        model_path = current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH]

    if current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] is not None:
        model_path = current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH]

    if current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] is not None:
        json_path = current_run_meta[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH]

    run_info = {
        "userId": user_sso_id,
        "runNickName": current_run_meta[LcConst.RUN_OBJ_NICK_NAME],
        "creaDt": str(current_run_meta[LcConst.START_TIME]),
        "endDt": str(current_run_meta[LcConst.END_TIME]),
        "duration": str(current_run_meta[LcConst.DELTA_TIME]),
        "afLoc": "",
        "status": "LcFINISHED",
        "path": current_run_meta[LcConst.RUN_OBJ_MODEL_FILE_PATH],
        "modelPath": model_path,
        "jsonPath": json_path,
        "name": current_run_meta[LcConst.RUN_OBJ_NAME],
        "note": "",
        "isEvaluation": current_run_meta[LcConst.RUN_OBJ_IS_EVALUATION]
    }

    return run_info


class RestStore(LcAbstractStore):
    """
    Client for a remote tracking server accessed via REST API calls
    """

    def __init__(self, get_host_creds):
        super(RestStore, self).__init__()
        self.get_host_creds = get_host_creds

    @property
    def host_creds(self):
        return self.get_host_creds

    def _call_endpoint(self, json_body, current_run_meta):

        # '/project/{project}/workspace/{workspaceId}/experiment/{experimentId}/run'
        env_value = get_os_env()
        endpoint = '/project/{project}/workspace/{workspaceId}/experiment/{experimentId}/run'
        endpoint = endpoint.replace('{project}', str(env_value[LcConst.ENV_PROJECT_ID]))
        endpoint = endpoint.replace('{workspaceId}', str(env_value[LcConst.ENV_WORKSPACE_ID]))
        endpoint = endpoint.replace('{experimentId}', str(env_value[LcConst.ENV_EXPERIMENT_ID]))
        if json_body:
            data = json.loads(json_body)
            data = self._make_metrics_data(data)
            data = self._make_parameter_data(data)
            data = self._make_feature_data(data, current_run_meta)
        param = json.dumps(data)

        try:
            response = http_request(host_creds=self.host_creds, endpoint=endpoint, method='POST', data=param)
            response = verify_rest_response(response, endpoint).text

        except Exception as e:
            logging.error("Modeler API server connection failed", e)
            response = None

        return response

    def lc_create_run(self, current_run_meta):
        """
        Create a run under the specified experiment ID.

        :return: The ID of the created Run object
        """

        # read workspace environment
        # project_id, workspace_id, experiment_id and user_id
        env_value = get_os_env()
        project_id = str(env_value[LcConst.ENV_PROJECT_ID])
        workspace_id = str(env_value[LcConst.ENV_WORKSPACE_ID])
        experiment_id = str(env_value[LcConst.ENV_EXPERIMENT_ID])
        user_id = str(env_value[LcConst.ENV_USER_SSO_ID])  # owner id

        if current_run_meta[LcConst.RUN_OBJ_IS_EVALUATION]=="false":
            print("training model.")
            with open(current_run_meta[LcConst.RUN_RESULT_PATH][LcConst.RUN_MODEL_JSON_PATH]) as run_json_file:
                json_data = json.load(run_json_file)

                try:
                    user_id = json_data['user_id']
                except KeyError:
                    pass
        nick_name = current_run_meta[LcConst.NICK_NAME]
        run_proto = _set_run_info_dict(current_run_meta, user_id)

        git_meta = {'filename': '', 'repo': '', 'commit': ''}
        git_meta_data = {
            "url": git_meta[SOURCE_FILE_GIT_REPO],
            "commit": git_meta[SOURCE_FILE_GIT_COMMIT_ID]
        }

        if SOURCE_FILE_GIT_META in current_run_meta:
            git_meta = current_run_meta[SOURCE_FILE_GIT_META]
            if SOURCE_FILE_GIT_REPO in git_meta:
                git_meta_data = {
                    "url": git_meta[SOURCE_FILE_GIT_REPO],
                    "commit": git_meta[SOURCE_FILE_GIT_COMMIT_ID]
                }

        py_depen = {'data': ''}
        if PYTHON_DEPENDENCY in current_run_meta:
            pdep = current_run_meta[PYTHON_DEPENDENCY]
            pdep_list = dict_to_list(pdep)
            py_depen = {
                "data": pdep_list
            }

        # to get parameter and metric
        run_data = BaseParser.run_parser(BaseParser.get_parser_type(current_run_meta), current_run_meta)
        metric_data = run_data['metrics']
        parameter_data = run_data['params']
        visual_data = None
        if 'visual' in run_data:
            visual_data = run_data['visual']
        if current_run_meta[LcConst.RUN_OBJ_IS_EVALUATION]=="false":
            artifact = {
                "name": run_data['artifact']['name'],
                "version": run_data['artifact']['version']
            }

            artifact_proto = artifact
        else:
            artifact_proto = None

        req_body = json.dumps({
            "project_id": project_id,
            "workspace_id": workspace_id,
            "experiment_id": experiment_id,
            "userId": user_id,
            "run_nick_name": nick_name,
            "run": run_proto,  # Assuming this is now a dict
            "artifact": artifact_proto,  # Assuming this is now a dict
            "git": git_meta_data,
            "parameter": parameter_data,
            "metrics": metric_data,
            "visuals": visual_data,
            "dependency": py_depen
        })

        response = self._call_endpoint(req_body, current_run_meta)

        return response

    def create_tag(self, run_id, tag):
        """
        Set a tag for the specified run

        :param run_id: String ID of the run
        :param tag: RunTag instance to log
        """

        # TODO brian_todo

        pass

    def _make_metrics_data(self, json_body):
        result = []
        # metrics_object = {'key': '', 'values': [], 'timestamp': [], 'steps': []}

        # get metrics
        metrics_data = json_body['metrics']
        # get visuals
        if 'visuals' in json_body and json_body['visuals'] is not None:
            visuals_data = json_body['visuals']
            for item in visuals_data:
                metrics_object = {'key': item['key'], 'values': [], 'timestamp': item['timestamp'],
                                  'steps': item['steps']}
                # key, listValues, timestamp, steps
                if 'listValues' in item:
                    for values in item['listValues'][0]['values']:
                        metrics_object['values'].append(values['values'])
                else:
                    metrics_object['values'].extend(item['values'][0]['values'])

                result.append(metrics_object)
                metrics_data.append(metrics_object)

        if 'visuals' in json_body:
            del json_body['visuals']

        return json_body

    def _make_parameter_data(self, json_body):
        result = []
        # metrics_object = {'key': '', 'values': [], 'timestamp': [], 'steps': []}

        # get metrics
        try:
            parameter_data = json_body['parameter']
        except KeyError:
            parameter_data = []
        # "parameter": {
        #     "parameter": {
        #       "learningrate": "0.12",
        #       "subsample": "0.72",
        #       "colsamplebytree": "0.62",
        #       "maxdepth": "52",
        #       "alpha": "0.82"
        #     }
        #   }

        parameter = {'parameter': {}}

        parameter_dict = {k: v for d in parameter_data for k, v in d.items()}
        parameter = {'parameter': parameter_dict}
        #
        # for param in parameter_data:
        #     # key = param['key']
        #     # value = param['value']
        #     parameter['parameter'].append(param)
        #     # column_dict.setdefault(col_name, []).append(row[col_name])

        if 'parameter' in json_body:
            del json_body['parameter']

        json_body['parameter'] = parameter
        return json_body

    def _make_feature_data(self, json_body, run_info_json):
        json_body['feature'] = {}
        json_body['feature']['importance'] = {}

        run_result_path = run_info_json[RUN_RESULT_PATH]

        # json_path = run_result_path[RUN_MODEL_SHAP_JSON_PATH]

        # json_path = None

        if RUN_MODEL_SHAP_JSON_PATH in run_result_path.keys():
            json_path = run_result_path[RUN_MODEL_SHAP_JSON_PATH]

            with open(json_path) as json_file:
                shap_json_data = json.load(json_file)
            json_body['feature']['importance'] = shap_json_data

        return json_body