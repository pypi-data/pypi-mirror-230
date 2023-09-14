import json
import os
from unittest.mock import patch

import pytest
from amazon_sagemaker_jupyter_scheduler.environment_detector import (
    JupyterLabEnvironment,
    JupyterLabEnvironmentDetector,
)
from amazon_sagemaker_jupyter_scheduler.environments import (
    SagemakerEnvironmentManager,
    region_name_to_code,
)


@pytest.fixture(autouse=True)
def mock_jupyter_lab_environment():
    with patch(
        "amazon_sagemaker_jupyter_scheduler.environments.JupyterLabEnvironmentDetector",
        autospec=True,
    ) as mock_detector:
        mock_detector.return_value.current_environment = (
            JupyterLabEnvironment.SAGEMAKER_STUDIO
        )
        yield


class TestSagemakerEnvironments:
    patch.dict(os.environ, {"REGION_NAME": "us-west-2", "HOME": "."}, clear=True)

    def test_default_sagemaker_defaults(self):
        envs_response = SagemakerEnvironmentManager().list_environments()
        assert envs_response[0].name == "sagemaker-default-env"
        for instance in envs_response[0].compute_types:
            assert instance.startswith("ml")

    def test_region_mapping(self):
        package_root = os.path.abspath(os.path.dirname(__file__).rstrip("/tests"))
        region_mapping_filename = os.path.join(package_root, "host_region_mapping.json")
        with open(region_mapping_filename) as file:
            region_mapping = json.load(file)["regions"]
            for region_display_name in region_name_to_code.values():
                assert region_display_name in region_mapping
