import os
import sys
from pathlib import Path
import unittest

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
PKGDIR = FILE.parents[2] # visionai dir
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from visionai.scenarios.slip_and_fall_detection import SlipAndFallDetection

class TestSlipAndFallScenarios(unittest.TestCase):
    def test_slip_and_fall(self):
        slip_and_fall = SlipAndFallDetection()
        output = slip_and_fall.start(camera_name=0, test=True)
        assert output == "10_SECS_RAN"



if __name__ == '__main__':
    unittest.main()