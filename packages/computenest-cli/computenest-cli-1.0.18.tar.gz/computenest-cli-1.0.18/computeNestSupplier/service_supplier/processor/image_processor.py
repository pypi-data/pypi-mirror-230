import os
import time
import json
from computeNestSupplier.service_supplier.client.image_client import ImageClient
from computeNestSupplier.service_supplier.common.util import Util
from computeNestSupplier.service_supplier.common import constant
from computeNestSupplier.service_supplier.common.credentials import Credentials


class ImageProcessor:
    IMAGEID = 'imageId'
    RUNNING = 'Running'
    WAITING = 'Waiting'
    QUEUED = 'Queued'
    FAILED = 'Failed'
    SUCCESS = 'Success'

    def __init__(self, region_id, access_key_id, access_key_secret):
        self.region_id = region_id
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.image = ImageClient(self.region_id, self.access_key_id, self.access_key_secret)

    def process_image(self, image_data):
        execution_id = self.image.start_update_Image_execution(image_data)
        print("========================================================")
        print("The task to create an image has started executing")
        print("The execution id: ", execution_id)
        print("========================================================")
        while True:
            image_data = self.image.list_execution(execution_id)
            status = image_data.body.executions[0].status
            if status == self.RUNNING or status == self.RUNNING or status == self.QUEUED:
                print('Be executing...')
            elif status == self.FAILED:
                status_message = image_data.body.executions[0].status_message
                print('Execution failed')
                print("The failed status message: ", status_message)
                raise RuntimeError("The task to create an image has failed")
            elif status == self.SUCCESS:
                image_data = self.image.list_execution(execution_id)
                outputs = json.loads(image_data.body.executions[0].outputs)
                image_id = outputs[self.IMAGEID]
                print("========================================================")
                print("Successfully created a new image!")
                print("The image id: ", image_id)
                print("========================================================")
                break
            time.sleep(100)

        return image_id

    def process_acr_image(self, acr_image_name, acr_image_tag, file_path):
        credentials = Credentials(self.region_id, self.access_key_id, self.access_key_secret)
        response = credentials.get_artifact_repository_credentials(constant.ACR_IMAGE)
        username = response.body.credentials.username
        password = response.body.credentials.password
        repository_name = response.body.available_resources[0].repository_name
        docker_path = os.path.dirname(response.body.available_resources[0].path)
        file_path = os.path.dirname(file_path)
        commands = [
            f"docker build -t {acr_image_name}:{acr_image_tag} .",
            f"docker login {repository_name} --username={username} --password={password}",
            f"docker tag {acr_image_name}:{acr_image_tag} {docker_path}/{acr_image_name}:{acr_image_tag}",
            f"docker push {docker_path}/{acr_image_name}:{acr_image_tag}"
        ]
        for command in commands:
            try:
                output, error = Util.run_cli_command(command, file_path)
                print(output.decode())
                print(error.decode())
            except Exception as e:
                print(f"Error occurred: {e}")

    def process_helm_chart(self, helm_chart_name, file_path):
        credentials = Credentials(self.region_id, self.access_key_id, self.access_key_secret)
        response = credentials.get_artifact_repository_credentials(constant.HELM_CHART)
        username = response.body.credentials.username
        password = response.body.credentials.password
        repository_name = response.body.available_resources[0].repository_name
        chart_path = os.path.dirname(response.body.available_resources[0].path)
        file_path = os.path.dirname(file_path)
        commands = [
            f"helm registry login -u {username} {repository_name} -p {password}",
            f"helm push {helm_chart_name}.tgz oci://{chart_path}"
        ]
        for command in commands:
            try:
                output, error = Util.run_cli_command(command, file_path)
                print(output.decode())
                print(error.decode())
            except Exception as e:
                print(f"Error occurred: {e}")