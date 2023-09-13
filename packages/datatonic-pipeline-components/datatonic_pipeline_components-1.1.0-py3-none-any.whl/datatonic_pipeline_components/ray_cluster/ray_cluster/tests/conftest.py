import pytest
import os
import json


@pytest.fixture
def mock_cluster_spec():
    cluster_spec = {
        "cluster": {
            "workerpool0": ["machine-name-workerpool0-0:2222"],
            "workerpool1": [
                "machine-name-workerpool1-0:2222",
                "machine-name-workerpool1-1:2222",
            ],
        },
        "task": {"type": "workerpool0", "index": 0, "trial": "TRIAL_ID"},
        "open_ports": ["open_port"],
    }
    os.environ["CLUSTER_SPEC"] = json.dumps(cluster_spec)


@pytest.fixture()
def mock_empty_cluster_spec():
    os.environ["CLUSTER_SPEC"] = json.dumps({})


@pytest.fixture()
def mock_cluster_spec_without_cluster():
    cluster_spec = {
        "task": {"type": "workerpool0", "index": 0, "trial": "TRIAL_ID"},
        "open_ports": ["open_port"],
    }
    os.environ["CLUSTER_SPEC"] = json.dumps(cluster_spec)


@pytest.fixture()
def mock_cluster_spec_without_task():
    cluster_spec = {
        "cluster": {
            "workerpool0": ["machine-name-workerpool0-0:2222"],
            "workerpool1": [
                "machine-name-workerpool1-0:2222",
                "machine-name-workerpool1-1:2222",
            ],
        },
        "open_ports": ["open_port"],
    }
    os.environ["CLUSTER_SPEC"] = json.dumps(cluster_spec)


@pytest.fixture
def mock_cluster_spec_without_workerpool():
    cluster_spec = {
        "cluster": {},
        "task": {"type": "workerpool0", "index": 0, "trial": "TRIAL_ID"},
        "open_ports": ["open_port"],
    }
    os.environ["CLUSTER_SPEC"] = json.dumps(cluster_spec)


@pytest.fixture
def mock_cluster_spec_without_open_port():
    cluster_spec = {
        "cluster": {
            "workerpool0": ["machine-name-workerpool0-0:2222"],
            "workerpool1": [
                "machine-name-workerpool1-0:2222",
                "machine-name-workerpool1-1:2222",
            ],
        },
        "task": {"type": "workerpool0", "index": 0, "trial": "TRIAL_ID"},
    }
    os.environ["CLUSTER_SPEC"] = json.dumps(cluster_spec)
