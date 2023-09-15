import importlib
import json
import os
import pandas as pd
import shutil


class ModelExport:
    def __init__(self):
        self._FW_VERSION_DICT_ = {
            "sklearn": "0.24.2",
            "tensorflow": "2.2.0",
            "pytorch": "1.6.0"
        }
        self._DATA_TYPE_LIST_ = ["Tabular", "Image", "Text"]
        self._MODEL_TYPE_LIST_ = ["sklearn", "tensorflow", "torch"]
        self._ESTM_TYPE_LIST_ = ["classifier", "others", "regressor"]
        self._BASE_PATH_ = "/home/work"
        self._base_data_dir_ = os.path.join(self._BASE_PATH_, "dataset")
        self._schema_path_ = os.path.join(self._base_data_dir_, ".columns.json")

    def _validate_input(self, value, valid_values, name):
        if value not in valid_values:
            raise ValueError(f"{value}은(는) 유효하지 않은 {name}입니다. 가능한 값은 {valid_values} 입니다.")

    def modelValidationForAiruntime(self, model_type=None, data_type=None, estimator_type=None, sample_dataset=None, target_col=None):
        if any(param is None for param in [model_type, data_type, estimator_type]) \
                or sample_dataset is None or sample_dataset.empty:
            raise ValueError("model_type, data_type, sample_dataset, estimator_type은 반드시 입력되어야 합니다.")

        self._validate_input(model_type, self._MODEL_TYPE_LIST_, "모델 유형")
        self._validate_input(data_type, self._DATA_TYPE_LIST_, "데이터 유형")
        self._validate_input(estimator_type, self._ESTM_TYPE_LIST_, "분석 유형")

        if estimator_type == 'regressor' and target_col is None:
            raise ValueError("모델이 regressor일 경우 target_col 입력이 필요합니다.")

        _DEFAULT_TARGET_COL_ = target_col if estimator_type == 'regressor' else "variety"  # classification

        # datapath none -> _dataset 유무 무관
        if not os.path.exists(self._schema_path_):
            self._write_schema(sample_dataset, estimator_type=estimator_type)

        model_dir = os.path.join(
            "file://", self._BASE_PATH_, "airuntime", model_type, "models")

        _data_info = os.path.join(
            self._BASE_PATH_, "airuntime", model_type, "data-info.json",
        )
        _data_schema = os.path.join(
            self._BASE_PATH_, "airuntime", model_type, "columns.json",
        )
        if os.path.exists(_data_info):
            os.remove(_data_info)
        if os.path.exists(_data_schema):
            os.remove(_data_schema)

        try:
            with open(self._schema_path_, "r") as f:
                schema_info = json.load(f)
            with open(self._schema_path_, "w") as f:
                if _DEFAULT_TARGET_COL_:
                    schema_info.update({
                        "targetColumn": _DEFAULT_TARGET_COL_,
                        "estimatorType": estimator_type,
                    })
                json.dump(schema_info, f)
        except FileNotFoundError:
            print("Dataset을 선택하여야 합니다.")


        _label_encoder_path = os.path.join(model_dir, "labelEncoder.joblib")
        if estimator_type != "classifier" and os.path.exists(_label_encoder_path):
            os.remove(_label_encoder_path)

        data_info_src = os.path.join("file://", self._BASE_PATH_, self._schema_path_)
        data_info_dst = os.path.join("file://", _data_schema)
        shutil.copy(data_info_src, data_info_dst)

        self._write_model_flag(model_type, data_type)

    def _write_model_flag(self, model_type: str = "sklearn", data_type: str = "Tabular"):
        fw_name = model_type
        fw_module = importlib.import_module(fw_name)
        try:
            fw_version = fw_module.__version__ if fw_module.__version__ else self._FW_VERSION_DICT_.get(fw_name)
        except AttributeError:
            fw_version = self._FW_VERSION_DICT_.get(fw_name)
        model_flag = f"""# This file is a SYSTEM-GENERATED file. DO NOT EDIT THIS!!!

MODEL_TYPE={model_type}
FW={fw_name}
FW_VERSION={fw_version}
DATA_TYPE={data_type}
MODEL_TEST=/home/work/airuntime/{model_type}/test_server.py
"""
        # print(model_flag)
        # print(data_type.lower())
        with open(self._schema_path_, "r") as f:
            custom_schema = json.load(f)
        custom_name = custom_schema.get("filename")
        if data_type.lower() == "tabular":
            try:
                data_info, data_path = self._load_schema()
                data_path = data_path.split(self._BASE_PATH_ + os.path.sep)[-1]
                data_name = os.path.basename(data_path)
                if data_name == custom_name:
                    model_flag += "PIPELINE_SCHEMA={pipeline_schema}\n".format(
                        pipeline_schema=json.dumps(data_info["schema"]))
                else:
                    model_flag += "PIPELINE_SCHEMA={pipeline_schema}\n".format(pipeline_schema="")
            except FileNotFoundError:
                data_path = custom_name
                model_flag += "PIPELINE_SCHEMA={pipeline_schema}\n".format(pipeline_schema="")
            model_flag += "SOURCE_URL={data_path}\n".format(data_path=data_path)
        print(model_flag)
        with open(os.path.join(self._BASE_PATH_, ".MODEL_FLAG"), "w") as f:
            f.write(model_flag)

    def _load_schema(self):
        try:
            with open(os.path.join(self._BASE_PATH_, "dataset", "data-info.json"), "r") as f:
                data_info = json.load(f)[0]
                data_path = os.path.join(self._BASE_PATH_, 'dataset', data_info.get('filename', None))
                if not data_path:
                    raise ValueError("파이프라인 데이터 정보가 잘못되었습니다.")
                return data_info, data_path
        except FileNotFoundError as fe:
            raise FileNotFoundError("파이프라인 데이터 정보를 찾을 수 없습니다.")
        except IndexError as ie:
            raise IndexError("파이프라인 데이터 리스트가 잘못되었습니다.")
        except Exception as e:
            raise e

    def _write_schema(self, _dataset: pd.DataFrame, data_path=None, estimator_type="classifier"):
        os.makedirs(os.path.dirname(os.path.abspath(self._schema_path_)), exist_ok=True)
        if data_path is None:
            data_path = ".dummy.csv" # 추후 data_path도 user에게 받을 경우 사용
            _dataset.to_csv(os.path.join(self._BASE_PATH_, data_path), index=False)
        with open(self._schema_path_, "w") as f:
            json.dump({
                "filename": os.path.basename(data_path),
                "columns": _dataset.dtypes.index.tolist(),
                "datatypes": [d.name for d in _dataset.dtypes],
                "estimatorType": estimator_type,
            }, f)