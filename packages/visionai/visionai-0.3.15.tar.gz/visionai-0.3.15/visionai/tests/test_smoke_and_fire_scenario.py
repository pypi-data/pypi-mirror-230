import os
import sys
from pathlib import Path
import unittest

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
PKGDIR = FILE.parents[2] # visionai dir
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from visionai.scenarios.smoke_and_fire_detection import SmokeAndFireDetection

class TestSmokeAndFireScenarios(unittest.TestCase):
    def test_smoke_and_fire(self):
        smoke_and_fire = SmokeAndFireDetection()
        output = smoke_and_fire.start(camera_name=0, test=True)
        # output = smoke_and_fire.start('https://www.youtube.com/watch?v=cPYaQ-_MKt0')
        assert output == "10_SECS_RAN"
if __name__ == '__main__':
    unittest.main()