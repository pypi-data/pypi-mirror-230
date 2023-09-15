import docker
import unittest
from unittest.mock import patch
import sys
from pathlib import Path
from cli import stop_cmd

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
PKGDIR = FILE.parents[2] # visionai dir
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from util.general import WorkingDirectory, invoke_cmd
from config import VISIONAI_EXEC

class TestStopCmd(unittest.TestCase):
    
    @WorkingDirectory(PKGDIR)
    def setUp(self):
        # Initialize visionai package before running tests
        output = invoke_cmd(f'{VISIONAI_EXEC} init')

    def test_stop_cmd(self):
        with patch('builtins.print') as test_print:
            with patch.object(docker.Container, 'stop') as test_stop:
                # Test case 1: stop all containers successfully
                test_stop.return_value = None
                stop_cmd()
                test_print.assert_called_with('- - - - - - - - - - - - - - - - - - - - - - - - - - -')
                test_print.assert_called_with('Stop web-app....')
                test_print.assert_called_with('Stop API service....')
                test_print.assert_called_with('Stop redis server....')
                test_print.assert_called_with('Stop grafana server....')
                test_print.assert_called_with('Stop Triton server....')
                test_print.assert_called_with('Done.')

                # Test case 2: Web-app container not found
                test_stop.side_effect = docker.errors.NotFound()
                stop_cmd()
                test_print.assert_called_with('Web-app not running')

                # Test case 3: Web-API container not found
                test_stop.side_effect = [None, docker.errors.NotFound()]
                stop_cmd()
                test_print.assert_called_with('Web-API not running')

                # Test case 4: Redis container not found
                test_stop.side_effect = [None, None, docker.errors.NotFound()]
                stop_cmd()
                test_print.assert_called_with('Redis not running')

                # Test case 5: Grafana container not found
                test_stop.side_effect = [None, None, None, docker.errors.NotFound()]
                stop_cmd()
                test_print.assert_called_with('Grafana not running')

                # Test case 6: Triton container not found
                test_stop.side_effect = [None, None, None, None, docker.errors.NotFound()]
                stop_cmd()
                test_print.assert_called_with('Triton not running')
                
if __name__ == '__main__':
    unittest.main()
