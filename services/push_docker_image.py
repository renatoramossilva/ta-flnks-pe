import os

from bindl.aws_wrapper.common import AWSClient
from bindl.aws_wrapper.ecr import ECRClient

REPOSITORY = os.getenv("REPOSITORY")
TAG = os.getenv("TAG")

IMAGE_URI_TEMPLATE = "{registry}/{repository}:{tag}"
image_uri = IMAGE_URI_TEMPLATE.format(
    registry=AWSClient().registry, repository=REPOSITORY, tag=TAG
)

# LOCAL VARIABLES
DOCKERFILE_PATH = "docker/Dockerfile"
CONTEXT_PATH = "."

# === EXECUTION FLOW ===
docker_mgr = ECRClient()

docker_mgr.login()
docker_mgr.build_image(
    dockerfile_path=DOCKERFILE_PATH, context_path=CONTEXT_PATH, tag=image_uri
)
docker_mgr.push_image(repository=REPOSITORY, tag=TAG)
