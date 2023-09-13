import time
import logging
from typing import Union
import shap
import joblib
import pandas as pd
import xgboost as xgb


def load_joblib_model(model_path: str):
    return joblib.load(model_path)


def calculate_shap_values(
    model: Union[xgb.XGBClassifier, xgb.XGBRegressor],
    X: pd.DataFrame,
    enable_gpu: bool,
):
    start = time.process_time()
    if enable_gpu:
        logging.info(
            f"Using GPU to calculate shap values on dataframe with shape {X.shape} "
        )
        model_gpu = model.get_booster()
        model_gpu.set_param({"predictor": "gpu_predictor"})
        explainer = shap.TreeExplainer(model=model_gpu)
    else:
        logging.info(
            f"Using CPU to calculate shap values on dataframe with shape {X.shape} "
        )
        explainer = shap.TreeExplainer(model=model)
    shap_values = explainer.shap_values(X)
    time_taken = time.process_time() - start
    logging.info(f"Took {time_taken} to calculate shap values")
    return shap_values
