import unittest
import docker
from docker_manager import DockerManager

class TestDockerManagerWithRealContainers(unittest.TestCase):

    def setUp(self):
        self.client = docker.from_env()
        self.test_container_name = "test_container"
        self.container = self.client.containers.run("alpine:latest", name=self.test_container_name, detach=True, command="sleep 60")
        self.docker_manager = DockerManager(self.client)

    def test_stop_and_remove_container_success(self):
        result = self.docker_manager.stop_and_remove_container(self.test_container_name)
        self.assertTrue(result)

    def tearDown(self):
        # Remove the test container, in case the test failed to do so
        try:
            container = self.client.containers.get(self.test_container_name)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass  # The container was already removed, nothing to do
