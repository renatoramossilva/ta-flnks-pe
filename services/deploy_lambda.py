import os

from bindl.aws_wrapper.common import AWSClient
from bindl.aws_wrapper.lambda_fn import LambdaClient

# DYNAMIC VARIABLES
FUNCTION_NAME = os.getenv("FUNCTION_NAME")
REPOSITORY = os.getenv("REPOSITORY")
TAG = os.getenv("TAG")

IMAGE_URI_TEMPLATE = "{registry}/{repository}:{tag}"
image_uri = IMAGE_URI_TEMPLATE.format(
    registry=AWSClient().registry, repository=REPOSITORY, tag=TAG
)

# === EXECUTION FLOW ===
lambda_mgr = LambdaClient()

lambda_mgr.deploy_image(FUNCTION_NAME, image_uri)
