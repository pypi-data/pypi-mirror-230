import unittest
import json, requests
import sys

from pathlib import Path
from config import SCENARIOS_OVERRIDE



class TestScenarioJson(unittest.TestCase):

    def test_scenario_json_file_exist(self):
        my_file = Path(SCENARIOS_OVERRIDE)
        assert my_file.is_file()

    def test_scenario_json_file_not_empty(self):
        my_file = Path(SCENARIOS_OVERRIDE)
        assert my_file.stat().st_size != 0


    def test_scenario_json_file_has_correct_format(self):
        with open(SCENARIOS_OVERRIDE,'r') as f:
            scenarios = json.load(f)
        assert isinstance(scenarios, dict)
        for scenario in scenarios['scenarios']:
            assert isinstance(scenario, dict)
            assert 'id' in scenario
            assert len(scenario['id']) > 0

            assert 'name' in scenario
            assert len(scenario['name']) > 0

            assert 'version' in scenario
            assert len(scenario['version']) > 0
            assert 'overview' in scenario
            assert 'docs' in scenario
            assert 'image' in scenario
            assert 'thumbnail' in scenario
            assert 'models' in scenario

            assert requests.get(scenario['image'], stream=True).status_code != 404
            assert requests.get(scenario['thumbnail'], stream=True).status_code != 404

            if(bool(scenario['models']['latest'])):
                assert requests.get(scenario['models']['latest']['model_url'], stream=True).status_code != 404

            assert isinstance(scenario['models'], dict)
            assert isinstance(scenario['models']['latest'], dict)
            assert isinstance(scenario['models']['other'], list)

            assert 'version' in scenario['models']['latest']
            assert len(scenario['models']['latest']['version']) > 0

            assert 'name' in scenario['models']['latest']
            assert len(scenario['models']['latest']['name']) > 0

            assert 'accuracy' in scenario['models']['latest']
            assert 'recall' in scenario['models']['latest']
            assert 'f1' in scenario['models']['latest']
            assert 'datasetSize' in scenario['models']['latest']

            assert 'model_url' in scenario['models']['latest']
            assert len(scenario['models']['latest']['model_url']) > 0

            assert isinstance(scenario['tags'], list)
            assert len(scenario['tags']) > 0

            assert isinstance(scenario['categories'], list)
            assert len(scenario['categories']) > 0


            assert isinstance(scenario['events'], list)
            assert len(scenario['events']) > 0

            assert isinstance(scenario['configuration'], list)


if __name__ == '__main__':
    unittest.main()



