"""Unit tests for all utils functions"""
import pytest
import subprocess
from unittest import mock
from ray_cluster.utils.utils import RayCustomJobSpec, RayCluster


@pytest.mark.parametrize(
    "cluster_spec, result",
    [
        (pytest.lazy_fixture("mock_cluster_spec_without_cluster"), "error"),
        (pytest.lazy_fixture("mock_cluster_spec_without_task"), "error"),
        (pytest.lazy_fixture("mock_cluster_spec_without_cluster"), "error"),
    ],
)
def test_ray_custom_job_spec_init_failure(cluster_spec, result: str):
    """Testing if initialising RayCustomJobSpec class failed as expected

    Args:
        result (str): The expected result.
    """
    if result == "error":
        with pytest.raises(RuntimeError):
            custom_job_spec = RayCustomJobSpec()


def test_get_head_node_name(mock_cluster_spec):
    """Test get_head_node_name() in RayCustomJobSpec"""
    custom_job_spec = RayCustomJobSpec()
    assert custom_job_spec.get_head_node_name() == "machine-name-workerpool0-0"


def test_get_head_node_name_failure(mock_cluster_spec_without_workerpool):
    """Test if get_head_node_name() in RayCustomJobSpec failed as expected"""
    with pytest.raises(ValueError):
        custom_job_spec = RayCustomJobSpec()
        custom_job_spec.get_head_node_name()


def test_get_open_port_exist(mock_cluster_spec):
    """Test if get_open_port() in RayCustomJobSpec returns the value of the open_port filed"""
    custom_job_spec = RayCustomJobSpec()
    assert custom_job_spec.get_open_port() == "open_port"


def test_get_open_port_not_exist(mock_cluster_spec_without_open_port):
    """Test get_open_port() in RayCustomJobSpec returns the default value(7777)"""
    custom_job_spec = RayCustomJobSpec()
    assert custom_job_spec.get_open_port() == 7777


def test_get_head_node_info(mock_cluster_spec):
    """Test get_head_node_info() in RayCustomJobSpec"""
    custom_job_spec = RayCustomJobSpec()
    assert custom_job_spec.get_head_node_info() == (
        "machine-name-workerpool0-0",
        "open_port",
        "machine-name-workerpool0-0:open_port",
    )


@mock.patch("subprocess.run")
def test_run_command(mock_run, mock_cluster_spec):
    """Test run_command() in RayCluster"""
    cmd = "echo 'A test command.'"
    mock_run.return_value = mock.MagicMock(stdout="A test command.")
    ray_cluster = RayCluster()
    assert ray_cluster.run_cmd(cmd=cmd) == "A test command."


@mock.patch("subprocess.run")
def test_run_command_failure(mock_run, mock_cluster_spec):
    """Test if run_command() in RayCluster failed as expected"""
    cmd = "A wrong command"
    mock_run.side_effect = subprocess.CalledProcessError(1, cmd[0])
    ray_cluster = RayCluster()
    with pytest.raises(RuntimeError):
        ray_cluster.run_cmd(cmd=cmd)


@mock.patch("subprocess.run")
def test_check_nodes(mock_run, mock_cluster_spec):
    """Test check_nodes() in RayCluster"""
    mock_run.return_value = mock.MagicMock(stdout="1 node_name")
    ray_cluster = RayCluster()
    assert ray_cluster.check_nodes(node_address="mock_address")


@mock.patch("subprocess.run")
def test_check_nodes_failure(mock_run, mock_cluster_spec):
    """Test if check_nodes() in RayCluster failed as expected"""
    mock_run.return_value = mock.MagicMock(stdout="")
    ray_cluster = RayCluster()
    assert not ray_cluster.check_nodes(node_address="mock_address")


@mock.patch("ray_cluster.utils.utils.wait_for_condition")
def test_wait_for_nodes(mock_wait_for_condition, mock_cluster_spec):
    """Test wait_for_nodes() in RayCluster"""
    ray_cluster = RayCluster()
    mock_wait_for_condition.return_value = "done"
    ray_cluster.wait_for_nodes(node_address="mock_address")
    assert mock_wait_for_condition.called


@mock.patch("time.sleep")
@mock.patch("subprocess.run")
@mock.patch("ray_cluster.utils.utils.wait_for_condition")
def test_connect_to_node(
    mock_wait_for_condition, mock_run, mock_sleep, mock_cluster_spec
):
    """Test connect_to_node() in RayCluster"""
    ray_cluster = RayCluster()
    mock_run.return_value = mock.MagicMock(stdout="1 node_name")
    mock_wait_for_condition.return_value = "done"
    mock_sleep.return_value = "1s"
    ray_cluster.connect_to_node(node_address="mock_address")
    assert mock_wait_for_condition.called
    assert mock_run.called
