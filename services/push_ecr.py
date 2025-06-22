import boto3
import base64
import docker
import deploy_lambda


class ECRDockerClient:
    def __init__(self, region: str, registry: str):
        self.region = region
        self.registry = registry
        self.ecr_client = boto3.client("ecr", region_name=region)
        self.docker_client = docker.from_env()

    def login(self):
        print(f"Getting ECR token for region {self.region} ...")
        token_response = self.ecr_client.get_authorization_token()
        auth_data = token_response["authorizationData"][0]
        token = auth_data["authorizationToken"]
        proxy_endpoint = auth_data["proxyEndpoint"]

        # Decode token
        decoded = base64.b64decode(token).decode("utf-8")
        username, password = decoded.split(":", 1)

        print(f"Logging in to Docker registry {proxy_endpoint} ...")
        self.docker_client.login(username=username, password=password, registry=proxy_endpoint)
        print("✅ Login successful")

    def push_image(self, repository: str, tag: str):
        image_uri = f"{self.registry}/{repository}:{tag}"
        print(f"Pushing image {image_uri} ...")

        push_logs = self.docker_client.images.push(image_uri, stream=True, decode=True)
        for line in push_logs:
            msg = line.get("status") or line.get("errorDetail", {}).get("message") or line
            print(msg)

    def build_image(self, dockerfile_path: str, context_path: str, tag: str):
        print(f"Building image {tag} ...")
        image, logs = self.docker_client.images.build(
            path=context_path,
            dockerfile=dockerfile_path,
            tag=tag,
            rm=True,
        )
        for chunk in logs:
            line = chunk.get("stream") or chunk.get("status") or chunk.get("error")
            if line:
                print(line.strip())
        return image


# # Exemplo de uso
# if __name__ == "__main__":
#     REGION = "eu-central-1"
#     REGISTRY = "845590645935.dkr.ecr.eu-central-1.amazonaws.com"
#     REPOSITORY = "my-ecr"
#     TAG = "flnks-1.0.2"
#     DOCKERFILE_PATH = "docker/Dockerfile"
#     CONTEXT_PATH = "."

#     client = ECRDockerClient(region=REGION, registry=REGISTRY)
#     client.login()
#     client.build_image(dockerfile_path=DOCKERFILE_PATH, context_path=CONTEXT_PATH, tag=f"{REGISTRY}/{REPOSITORY}:{TAG}")
#     client.push_image(repository=REPOSITORY, tag=TAG)

#     deployer = deploy_lambda.LambdaDeployer(region=REGION)
#     deployer.deploy_image(function_name=deploy_lambda.FUNCTION_NAME, image_uri=TAG)