from bindl.aws_wrapper.common import AWSClient
from bindl.aws_wrapper.ecr import ECRClient
from bindl.aws_wrapper.lambda_fn import LambdaClient

# DYNAMIC VARIABLES
FUNCTION_NAME = "flnks_lambda"  # lambda function name
REPOSITORY = "my-ecr"  # ECR repository name
tag = "flnks-1.0.10" # ECR image tag, can be dynamically set
IMAGE_URI_TEMPLATE = "{registry}/{repository}:{tag}"
image_uri = IMAGE_URI_TEMPLATE.format(
    registry=AWSClient().registry, repository=REPOSITORY, tag=tag
)

# LOCAL VARIABLES
DOCKERFILE_PATH = "docker/Dockerfile"
CONTEXT_PATH = "."

# === EXECUTION FLOW ===
docker_mgr = ECRClient()
lambda_mgr = LambdaClient()



docker_mgr.login()
docker_mgr.build_image(
    dockerfile_path=DOCKERFILE_PATH, context_path=CONTEXT_PATH, tag=image_uri
)
docker_mgr.push_image(repository=REPOSITORY, tag=tag)
lambda_mgr.deploy_image(FUNCTION_NAME, image_uri)
