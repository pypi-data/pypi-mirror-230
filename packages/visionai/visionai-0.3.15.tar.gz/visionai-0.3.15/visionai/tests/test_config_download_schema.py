import json
import requests
import tempfile
import http.server
import socketserver
from pathlib import Path

FILE = Path(__file__).resolve()
CONFIGDIR = FILE.parents[0]  # config directory

# Define a mock URL and file for testing
SCENARIOS_OVERRIDE = tempfile.NamedTemporaryFile(delete=False).name
SCENARIOS_URL = "http://localhost:8000/scenarios.json"

def main():
    res = requests.get(SCENARIOS_URL)
    scenarios = res.json()
    with open(SCENARIOS_OVERRIDE, 'w') as f:
        json.dump(scenarios, f, indent=4)

    print(f'Scenarios schema {SCENARIOS_URL} downloaded to {SCENARIOS_OVERRIDE}')

def test_main():
    # Write some JSON data to a temporary file
    mock_scenarios = {"scenarios": [{"name": "scenario1"}, {"name": "scenario2"}]}
    mock_scenarios_file = tempfile.NamedTemporaryFile(delete=False)
    mock_scenarios_file.write(json.dumps(mock_scenarios).encode())
    mock_scenarios_file.close()

    # Start a local server to serve the temporary file
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        print("Serving mock scenarios at http://localhost:8000/scenarios.json")
        httpd.RequestHandlerClass.protocol_version = "HTTP/1.0"
        httpd.serve_forever()

    # Modify the URL to point to the local server
    global SCENARIOS_URL
    SCENARIOS_URL = "http://localhost:8000/scenarios.json"

    # Invoke the main function
    main()

    # Read the contents of the output file and compare to expected JSON data
    with open(SCENARIOS_OVERRIDE) as f:
        result = json.load(f)

    assert result == mock_scenarios
