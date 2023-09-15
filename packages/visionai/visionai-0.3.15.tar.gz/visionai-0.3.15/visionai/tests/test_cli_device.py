import unittest
from unittest.mock import patch
from io import StringIO
from cli.device_app import device_list, device_select, device_modules, device_gpu_mem_stats


from config import VISIONAI_EXEC
from util.general import WorkingDirectory, invoke_cmd

class TestDeviceApp(unittest.TestCase):
    @WorkingDirectory(PKGDIR)
    def setUp(self):
        # Initialize visionai package before running tests
        output = invoke_cmd(f'{VISIONAI_EXEC} init')

    def test_device_list(self):
        expected_output = "Devices : ['oos-training', 'edge-dev1', 'edge-dev2']\n"
        with patch('sys.stdout', new=StringIO()) as mock_output:
            device_list()
            self.assertEqual(mock_output.getvalue(), expected_output)

    def test_device_select(self):
        expected_output = "Selecting device : edge-dev1\n"
        with patch('sys.stdout', new=StringIO()) as mock_output:
            device_select("edge-dev1")
            self.assertEqual(mock_output.getvalue(), expected_output)

    def test_device_modules(self):
        expected_output = "Listing modules : ['edgeCtl', 'edgeEvents']\n"
        with patch('sys.stdout', new=StringIO()) as mock_output:
            device_modules()
            self.assertEqual(mock_output.getvalue(), expected_output)

    def test_device_gpu_mem_stats(self):
        expected_output = "Getting gpu/mem stats\n"
        with patch('sys.stdout', new=StringIO()) as mock_output:
            device_gpu_mem_stats()
            self.assertEqual(mock_output.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
