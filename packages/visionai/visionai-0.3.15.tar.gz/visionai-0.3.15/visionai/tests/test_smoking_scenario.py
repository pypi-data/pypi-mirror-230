import os
import sys
from pathlib import Path
import unittest

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
PKGDIR = FILE.parents[2] # visionai dir
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from visionai.scenarios.smoking_detection import SmokingDetection

class TestSmokingScenarios(unittest.TestCase):
    def test_smoking(self):
        smoking = SmokingDetection()
        output = smoking.start(camera_name=0, test=True)
        assert output == "10_SECS_RAN"



if __name__ == '__main__':
    unittest.main()