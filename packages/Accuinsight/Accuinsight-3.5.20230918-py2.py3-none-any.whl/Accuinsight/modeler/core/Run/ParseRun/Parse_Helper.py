from Accuinsight.modeler.core.LcConst.LcConst import RUN_OBJ_DATA_VERSION


def get_data_version(param_data):
    data_version = ''
    if RUN_OBJ_DATA_VERSION in param_data:
        data_version = param_data[RUN_OBJ_DATA_VERSION]

    return {
        RUN_OBJ_DATA_VERSION: data_version
    }
