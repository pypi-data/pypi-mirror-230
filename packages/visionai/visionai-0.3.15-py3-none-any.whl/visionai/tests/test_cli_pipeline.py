import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from rich import print
from cli import pipeline_app

from config import VISIONAI_EXEC
from util.general import WorkingDirectory, invoke_cmd  
             
@pytest.fixture
def runner():
    return CliRunner()

def test_pipeline_create(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['create', '--name', 'test_pipe'])

        assert result.exit_code == 0
        assert 'Creating pipeline test_pipe' in mock_print.call_args_list[0][0][0]


def test_pipeline_add_scenario(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['add-scenario', '--pipeline', 'test_pipe', '--scenario', 'smoke-and-fire'])

        assert result.exit_code == 0
        assert 'Adding scenario smoke-and-fire to pipeline test_pipe' in mock_print.call_args_list[0][0][0]


def test_pipeline_add_preprocess(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['add-preprocess', '--pipeline', 'test_pipe', '--preprocess', 'face-blur'])

        assert result.exit_code == 0
        assert 'Adding preprocess face-blur to pipeline test_pipe' in mock_print.call_args_list[0][0][0]


def test_pipeline_add_camera(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['add-camera', '--pipeline', 'test_pipe', '--camera', 'OFFICE-01'])

        assert result.exit_code == 0
        assert 'Adding camera OFFICE-01 to pipeline test_pipe' in mock_print.call_args_list[0][0][0]


def test_pipeline_remove_camera(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['remove-camera', '--pipeline', 'test_pipe', '--camera', 'OFFICE-01'])

        assert result.exit_code == 0
        assert 'Removing camera OFFICE-01 to pipeline test_pipe' in mock_print.call_args_list[0][0][0]


def test_pipeline_reset(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['reset', '--pipeline', 'test_pipe'])

        assert result.exit_code == 0
        assert 'Pipeline test_pipe reset' in mock_print.call_args_list[0][0][0]


def test_pipeline_show(runner):
    with patch('main.print') as mock_print:
        result = runner.invoke(pipeline_app, ['show', '--pipeline', 'test_pipe'])

        assert result.exit_code == 0
if __name__=='__main__':
    CliRunner()