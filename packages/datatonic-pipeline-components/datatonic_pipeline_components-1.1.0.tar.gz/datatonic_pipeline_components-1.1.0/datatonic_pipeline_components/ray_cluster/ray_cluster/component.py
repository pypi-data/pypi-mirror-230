import os
from pathlib import Path
from kfp.dsl import component

_COMPONENTS_CONTAINER_REGISTRY = os.environ.get(
    "COMPONENTS_CONTAINER_REGISTRY",
    "europe-west1-docker.pkg.dev/dt-playgrounds-mlops/turbo-templates-containers",
)
_IMAGE_NAME = str(Path(__file__).parents[1].name)
_COMPONENTS_IMAGE_TAG = os.environ.get("COMPONENTS_IMAGE_TAG", "latest")


@component(
    base_image="python:3.9-slim-buster",
    target_image=f"{_COMPONENTS_CONTAINER_REGISTRY}/{_IMAGE_NAME}:{_COMPONENTS_IMAGE_TAG}",  # noqa: E501
    output_component_file=os.path.splitext(__file__)[0] + ".yaml",
)
def ray_cluster(
    ray_task_cmd: str,
    node_config_cmd: str = None,
    min_nodes: int = 1,
    cluster_op_timeout: int = 300,
    retry_interval_ms: int = 5000,
    nodes_alive_time: int = 24 * 60 * 60,
):
    """Deploy a Ray cluster and run distributed tasks

    Args:
        ray_task_cmd (str): The command to run the Ray task(s).
        node_config_cmd (str, optional): Command for additional setup that will be executed on all nodes in the cluster.
            For example, installing the dependencies or cloning a codebase. Defaults to None.
        min_nodes (int, optional): The minimum nodes required in the Ray cluster. Defaults to 1.
        cluster_op_timeout (int, optional):  Maximum timeout in seconds of any Ray cluster establish jobs.
            Defaults to 300.
        retry_interval_ms (int, optional): Retry interval in milliseconds of any Ray cluster establish jobs.
            Defaults to 5000.
        nodes_alive_time (int, optional):The amount of time that a node is alive. Defaults to 24*60*60 (1 day).
    """
    import time
    from ray.job_submission import JobSubmissionClient
    from ray_cluster.utils.utils import RayCluster

    ray_cluster = RayCluster()
    if node_config_cmd is not None:
        ray_cluster.run_cmd(cmd=node_config_cmd)

    if ray_cluster.workerpool_type == "workerpool0":
        # Initialising the ray cluster
        ray_cluster.start_ray_cluster()

        ray_cluster.wait_for_nodes(
            node_address=ray_cluster.head_node_address,
            min_nodes=min_nodes,
            timeout=cluster_op_timeout,
            retry_interval_ms=retry_interval_ms,
        )
        time.sleep(5)
        ray_cluster._logger.info(
            "A Ray cluster has been created. Running the custom job."
        )

        # Run ray tasks
        ray_job_client = JobSubmissionClient(ray_cluster.head_node_address)
        submission_id = ray_job_client.submit_job(
            entrypoint=ray_task_cmd,
        )
        ray_cluster._logger.info(
            "Job has been submitted successfully!\n Here are the logs:"
        )
        ray_cluster.run_cmd(
            cmd=f"ray \
                            job \
                            logs \
                            {submission_id} \
                            --follow"
        )
        ray_job_info = ray_job_client.get_job_info(submission_id)
        job_status = ray_job_info.status
        if job_status == "FAILED":
            raise RuntimeError("Job failed")
        else:
            ray_cluster._logger.info(
                f"Job {job_status} with the following information:"
            )
            ray_cluster._logger.info(ray_job_info)

    else:
        # Connect worker nodes to the head node
        ray_cluster.connect_to_node(
            node_address=ray_cluster.head_node_address,
            timeout=cluster_op_timeout,
            retry_interval_ms=retry_interval_ms,
        )
        time.sleep(nodes_alive_time)
