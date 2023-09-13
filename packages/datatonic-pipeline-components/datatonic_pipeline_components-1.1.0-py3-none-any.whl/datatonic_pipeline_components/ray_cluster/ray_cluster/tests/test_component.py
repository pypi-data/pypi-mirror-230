"""Unit tests for the Ray cluster component"""
from unittest import mock
from ray_cluster.component import ray_cluster

ray_comp_func = ray_cluster.python_func


@mock.patch("time.sleep")
@mock.patch("ray.job_submission.JobSubmissionClient")
@mock.patch("ray_cluster.utils.utils.RayCluster")
def test_ray_cluster_comp_head_node(
    mock_ray_cluster,
    mock_job_submission_client,
    mock_sleep,
):
    """Test the component functionality in the head node"""
    mock_sleep.return_value = "1s"
    mock_ray_cluster.return_value = mock.MagicMock(workerpool_type="workerpool0")
    ray_comp_func(ray_task_cmd="test command")
    assert mock_ray_cluster.return_value.start_ray_cluster.called
    assert mock_ray_cluster.return_value.wait_for_nodes.called
    assert mock_job_submission_client.return_value.submit_job.called
    assert mock_job_submission_client.return_value.get_job_info.called


@mock.patch("time.sleep")
@mock.patch("ray_cluster.utils.utils.RayCluster")
def test_ray_cluster_comp_worker_node(
    mock_ray_cluster,
    mock_sleep,
):
    """Test the component functionality in the worker node"""
    mock_sleep.return_value = "1s"
    mock_ray_cluster.return_value = mock.MagicMock(workerpool_type="workerpool1")
    ray_comp_func(ray_task_cmd="test command")
    assert mock_ray_cluster.return_value.connect_to_node.called
