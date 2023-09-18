import os
import argparse
import subprocess
import re
from Accuinsight.modeler.clients.modeler_api_runsandbox import WorkspaceRestApi
from Accuinsight.modeler.core.workspace_run_log import WorkspaceRunLog
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.modeler.utils.os_getenv import get_os_env


class WorkspaceRun:
    """
        Object for running code and sending the result to backend.
    """
    def __init__(self):
        env_value = get_os_env('ENV')

        self.workspace_run_log = WorkspaceRunLog()
        self.workspace_run_api = WorkspaceRestApi(env_value[LcConst.BACK_END_API_URL],
                                                  env_value[LcConst.BACK_END_API_PORT],
                                                  env_value[LcConst.BACK_END_API_URI])
        self.code_path = None
        self.custom_args = ''

    def exec_code(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--workspaceRunId', default=None)
        parser.add_argument('--codePath', default=None)
        parser.add_argument('--argument', default='')
        parser.add_argument('--envPath', default='/opt/conda')

        args, unknown = parser.parse_known_args()
        args_dict = vars(args)

        # set custom arguments
        if not args_dict['argument'] == '':
            self.custom_args = ' ' + args_dict['argument']\
                .replace('[[:space:]]', ' ').replace('[[:equal:]]', '=').replace('[[:hyphen:]]', '--')

        special_char_check = self.custom_args.strip()

        if special_char_check.startswith("'") and special_char_check.endswith("'"):
            self.custom_args = self.custom_args.translate(self.custom_args.maketrans({"'": None}))
            # Regex Special Chars
            regex = re.compile('[@!$%^&()|]')
            # Convert Space-Separated String to List
            argument_list = self.custom_args.split()
            tmp_custom_args = ""

            for arg in argument_list:
                if (regex.search(arg) != None):
                    input_arg = "'%s'" % arg
                else:
                    input_arg = arg
                tmp_custom_args = "%s %s" % (tmp_custom_args, input_arg)
            self.custom_args = tmp_custom_args
        else:
            print("Not matched argument formats from workspaceRun-shell")

        self.code_path = args_dict['codePath']
        self.workspace_run_log.workspace_run_id = args_dict['workspaceRunId']

        if not self.code_path:
            raise Exception("codePath cannot be none")

        env_path = args_dict['envPath']
        new_env = os.environ.copy()
        new_env['PATH'] = env_path + '/bin:' + new_env['PATH']

        _, file_extension = os.path.splitext(self.code_path)

        # genearate command based on file types(py or ipynb)
        if file_extension == '.py':
            command = "%s/bin/python -u '%s'%s > /tmp/output_%s.log 2>&1" % (
                env_path, self.code_path, self.custom_args, self.workspace_run_log.workspace_run_id
            )
            log_message = "Execute .py (envPath : %s)" % env_path
        elif file_extension == '.ipynb':
            command = "%s/bin/ipython --no-term-title --InteractiveShell.colors=NoColor '%s'%s > /tmp/output_%s.log 2>&1" % (
                env_path, self.code_path, self.custom_args, self.workspace_run_log.workspace_run_id
            )
            log_message = "Execute .ipynb (envPath : %s)" % env_path
        else:
            raise ValueError("Unsupported file extension: %s" % file_extension)

        try:
            subprocess.run(command, shell=True, encoding='UTF-8', env=new_env).check_returncode()
            self.workspace_run_log.is_success = True

            # add file extension and env path log
            with open("/tmp/output_%s.log" % self.workspace_run_log.workspace_run_id, 'a') as file_log:
                file_log.write(log_message)

            # add success log
            with open("/tmp/output_%s.log" % self.workspace_run_log.workspace_run_id, 'a') as result_log:
                result_log.write("\nWorkspace run with id=%s has been successfully finished.\n" %
                                 self.workspace_run_log.workspace_run_id)
        except subprocess.CalledProcessError:
            # if failed
            self.workspace_run_log.is_success = False
        finally:
            # call backend api (afterRun)
            self.workspace_run_api.call_rest_api(self.workspace_run_log.get_result_param(), 'run')


if __name__ == "__main__":
    workspace_run = WorkspaceRun()
    workspace_run.exec_code()
