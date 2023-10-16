"""Define test executor class."""
from abc import ABC

from ML_management.executor_template.executor_pattern import JobExecutorPattern
from ML_management.executor_template.upload_model_mode import UploadModelMode
from ML_management.models.model_type_to_methods_map import ModelMethodName


class TestExecutor(JobExecutorPattern, ABC):
    """Test executor from pattern with defined settings parameters."""

    def __init__(self):
        super().__init__(
            executor_name="test", desired_model_methods=[ModelMethodName.predict_function], executor_upload_model_mode=UploadModelMode.none
        )

    def execute(self):
        """Define execute function that calls predict_function of model with corresponding params."""
        return self.model.predict_function(**self.model_methods_parameters[ModelMethodName.predict_function])
