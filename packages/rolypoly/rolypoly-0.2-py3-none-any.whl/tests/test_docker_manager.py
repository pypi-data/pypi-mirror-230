# test_docker_manager.py

import unittest
from unittest.mock import Mock, patch
from docker_manager import DockerManager
import docker 

class TestDockerManager(unittest.TestCase):

    def setUp(self):
        self.mock_client = Mock()
        self.docker_manager = DockerManager()
        self.docker_manager.client = self.mock_client


    def test_stop_and_remove_container_not_found(self):
        self.mock_client.containers.get.side_effect = docker.errors.NotFound("Not Found")

        result = self.docker_manager.stop_and_remove_container("container_name")

        self.assertEqual(result, False)

    def test_stop_and_remove_container_success(self):
        container_mock = Mock()
        self.mock_client.containers.get.return_value = container_mock
        
        result = self.docker_manager.stop_and_remove_container("container_name")
        
        self.assertTrue(result)
        self.mock_client.containers.get.assert_called_with("container_name")
        container_mock.stop.assert_called_once()
        container_mock.remove.assert_called_once()

    def test_start_new_container_success(self):
        result = self.docker_manager.start_new_container("container_name", "image")
        
        self.assertTrue(result)
        self.mock_client.containers.run.assert_called_once()

    def test_start_new_container_fail(self):
        self.mock_client.containers.run.side_effect = Exception("Error")
        
        result = self.docker_manager.start_new_container("container_name", "image")
        
        self.assertFalse(result)


    def test_start_new_container_image_not_found(self):
        self.mock_client.containers.run.side_effect = docker.errors.ImageNotFound("Image not found")
        
        result = self.docker_manager.start_new_container("container_name", "invalid_image")
        
        self.assertFalse(result)
        self.mock_client.containers.run.assert_called_once_with(
            "invalid_image", 
            name="container_name", 
            detach=True, 
            mounts=[], 
            environment=[]
        )

    def test_stop_and_remove_container_force_stop(self):
        container_mock = Mock()
        container_mock.status = "running"
        self.mock_client.containers.get.return_value = container_mock

        with patch('time.sleep'):  # to speed up the test
            result = self.docker_manager.stop_and_remove_container("container_name", timeout=0)
        
        self.assertTrue(result)
        container_mock.stop.assert_called_once()
        
if __name__ == "__main__":
    unittest.main()
