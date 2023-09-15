import os
import sys
from pathlib import Path
import unittest

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
PKGDIR = FILE.parents[2] # visionai dir
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from visionai.scenarios.ppe_detection import PpeDetection

class TestPPEScenarios(unittest.TestCase):
    def test_ppe(self):
        ppe = PpeDetection()
        output = ppe.start(camera_name=0, test=True)
        assert output == "10_SECS_RAN"

if __name__ == '__main__':
    unittest.main()