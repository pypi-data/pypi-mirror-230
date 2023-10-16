"""Functions for internal usage."""
from tempfile import TemporaryDirectory
from typing import Optional

from ML_management.mlmanagement import mlmanagement

import mlflow


def _load_model_type(run_id, unwrap: Optional[bool] = True):
    """Load model from local path."""
    with TemporaryDirectory() as temp_dir:
        local_path = mlmanagement.MlflowClient().download_artifacts(run_id, "", temp_dir)
        loaded_model = mlflow.pyfunc.load_model(local_path)
    if unwrap:
        loaded_model = loaded_model.unwrap_python_model()
    return loaded_model
