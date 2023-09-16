from dataclasses import dataclass

from amazon_sagemaker_jupyter_scheduler.app_metadata import get_sagemaker_environment
from amazon_sagemaker_jupyter_scheduler.environment_detector import (
    JupyterLabEnvironment,
)
from amazon_sagemaker_jupyter_scheduler.providers.standalone_image_metadata import (
    get_image_metadata_standalone,
)
from amazon_sagemaker_jupyter_scheduler.providers.studio_image_metadata import (
    get_image_metadata_studio,
)


# MAIN ENTRY POINT
async def get_image_metadata(image_arn: str, aws_region: str):
    if get_sagemaker_environment() == JupyterLabEnvironment.SAGEMAKER_STUDIO:
        return await get_image_metadata_studio(image_arn, aws_region)

    return await get_image_metadata_standalone(image_arn, aws_region)
