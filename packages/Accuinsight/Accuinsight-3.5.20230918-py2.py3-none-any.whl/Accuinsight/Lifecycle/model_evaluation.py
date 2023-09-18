import json
import inspect

from Accuinsight.modeler.utils.os_getenv import is_in_ipython, get_os_env, get_current_notebook
from Accuinsight.modeler.utils.dependency.dependencies import gather_sources_and_dependencies
from Accuinsight.modeler.core.get_for_visual import roc_pr_curve, get_true_y, get_visual_info_regressor
from Accuinsight.modeler.core import calculation_metrics
from Accuinsight.modeler.core.func import get_time
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.Lifecycle.utils import create_metrics_dict
from Accuinsight.modeler.clients.modeler_api_runsandbox import WorkspaceRestApi
from pathlib import Path
from collections import OrderedDict


class RunData:
    def __init__(self, model_file_path, run_nickname_input, train_method, start_ts, end_ts):
        self.data = OrderedDict()
        self.data["path"] = model_file_path
        self.data["isEvaluation"] = "true"

        run_nick_name = Path(model_file_path).stem if run_nickname_input is None else run_nickname_input
        self.data["runNickName"] = run_nick_name
        self.data["name"] = run_nick_name + ' - ' + train_method + ' - No model information'

        self.data["userId"] = str(get_os_env()[LcConst.ENV_USER_SSO_ID])  # owner id
        self.data["creaDt"] = start_ts
        self.data["endDt"] = end_ts
        self.data["duration"] = end_ts - start_ts
        self.data["afLoc"] = ""
        self.data["note"] = ""
        self.data["status"] = "LcFINISHED"
        self.data["modelPath"] = ""
        self.data["jsonPath"] = ""

    def get(self):
        return self.data

class MetricsData:
    def __init__(self, train_method, y_hat_val, y_val, f1_average_in='weighted', recall_average_in='weighted'):
        self.data = []
        if train_method == 'classification':
            print("CLASSIFICATION in model_evaluation_from_data method")
            visual_classification_json = roc_pr_curve(y_hat_val, y_val, f1_average=f1_average_in, recall_average=recall_average_in)
            c_metrics = calculation_metrics.calculate_classification_metrics(y_hat_val, y_val, average=f1_average_in)

            self.data.extend([
                create_metrics_dict("fpr", list(value for value in visual_classification_json['fpr'].values()), list(visual_classification_json['fpr'].keys())),
                create_metrics_dict("tpr", list(value for value in visual_classification_json['tpr'].values()), list(visual_classification_json['tpr'].keys())),
                create_metrics_dict("recall", list(value for value in visual_classification_json['recall'].values()), list(visual_classification_json['recall'].keys())),
                create_metrics_dict("precision", list(value for value in visual_classification_json['precision'].values()), list(visual_classification_json['precision'].keys())),
                create_metrics_dict("legend",
                                    [[value['macro'], value['micro']] for value in visual_classification_json['legend'].values()],
                                    [f"{step}_{metric}" for step in visual_classification_json['legend'] for metric in ['macro', 'micro']]),
                create_metrics_dict("confusion_matrix", list(map(list, visual_classification_json['confusion_matrix'].values()))),
                create_metrics_dict("chart", list(visual_classification_json['chart'].values()), list(visual_classification_json['chart'].keys()))
            ])

        elif train_method == 'regression':
            print("REGRESSION in model_evaluation_from_data method")
            visual_regression_json = {'True_y': get_true_y(y_val), 'Predicted_y': get_visual_info_regressor(y_hat_val)}
            c_metrics = calculation_metrics.calculate_regression_metrics(y_hat_val, y_val)

            self.data.extend([
                create_metrics_dict("true_y", visual_regression_json['True_y']),
                create_metrics_dict("predicted_y", visual_regression_json['Predicted_y'])
            ])

        else:
            raise ValueError('현재 설정한 모델은 지원되지 않습니다. 관리자에게 문의하십시오.')

        selected_metrics_values = [str(metric_value) for metric_value in c_metrics.values()]
        selected_metrics = create_metrics_dict("selected_metrics", selected_metrics_values, steps=list(c_metrics.keys()))
        self.data.append(selected_metrics)

    def get(self):
        return self.data

class EnvironmentData:
    def __init__(self):
        self.data = OrderedDict()
        env_value = get_os_env()
        self.data["project_id"] = str(env_value[LcConst.ENV_PROJECT_ID])
        self.data["workspace_id"] = str(env_value[LcConst.ENV_WORKSPACE_ID])
        self.data["experiment_id"] = str(env_value[LcConst.ENV_EXPERIMENT_ID])
        self.data["userId"] = str(env_value[LcConst.ENV_USER_SSO_ID])  # owner id
        self.data["git"] = OrderedDict()
        self.data["git"]["url"] = ""
        self.data["git"]["commit"] = ""
        self.data["feature"] = OrderedDict()
        self.data["feature"]["importance"] = {}
        self.data["parameter"] = OrderedDict()
        self.data["parameter"]["parameter"] = {}
        self.data["dependency"] = OrderedDict()
        self.data["dependency"]["data"] = []

    def get(self):
        return self.data

def model_evaluation(run_nickname_input=None, train_method=None, y_hat_validation=None,
                     y_validation=None, f1_average_in='weighted', recall_average_in='weighted'):
    start_evl = get_time.now()

    if is_in_ipython():
        var_model_file_path = get_current_notebook()
        _caller_globals = inspect.stack()[1][0].f_globals
        (
            mainfile,
            sources,
            dependencies
        ) = gather_sources_and_dependencies(
            globs=_caller_globals,
            save_git_info=False
        )
    else:
        _caller_globals = inspect.stack()[1][0].f_globals
        (
            mainfile,
            sources,
            dependencies
        ) = gather_sources_and_dependencies(
            globs=_caller_globals,
            save_git_info=True
        )
        var_model_file_path = mainfile['filename']
    print(var_model_file_path)

    run_data = RunData(var_model_file_path, run_nickname_input, train_method, int(start_evl.timestamp()),
                       int(get_time.now().timestamp()))
    metrics_data = MetricsData(train_method, y_hat_validation, y_validation, f1_average_in, recall_average_in)
    env_data = EnvironmentData()

    data = OrderedDict()
    data["run"] = run_data.get()
    data["metrics"] = metrics_data.get()
    data.update(env_data.get())

    env_value = get_os_env('ENV')
    modeler_rest = WorkspaceRestApi(env_value[LcConst.BACK_END_API_URL],
                                    env_value[LcConst.BACK_END_API_PORT],
                                    env_value[LcConst.BACK_END_API_URI])
    param = json.dumps(data)

    # modeler-api로 전송
    modeler_rest.call_rest_api(param, 'model_evaluation')