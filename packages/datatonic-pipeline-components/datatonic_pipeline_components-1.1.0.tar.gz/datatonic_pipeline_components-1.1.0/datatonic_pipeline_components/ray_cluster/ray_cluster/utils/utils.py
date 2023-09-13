import re
import os
import json
import time
import subprocess
from ray._private.test_utils import wait_for_condition
import logging


class RayCustomJobSpec:
    """
    Vertex AI populates an environment variable, CLUSTER_SPEC,
    on every replica to describe how the overall cluster is set up.
    This class retrieves some useful information from CLUSTER_SPEC,
    such as host name of the replica in workerpool0 and the open port.
    Explore more information in the following link:
    https://cloud.google.com/vertex-ai/docs/training/distributed-training#cluster-spec-format
    """

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

        try:
            self.cluster_config_str = os.environ.get("CLUSTER_SPEC")
            self.cluster_config_dict = json.loads(self.cluster_config_str)
            self.cluster_info = self.cluster_config_dict["cluster"]
            self.workerpool_type = self.cluster_config_dict["task"]["type"]
        except Exception as error:
            self._logger.error(f"{error}")
            raise RuntimeError(f"{error}")

    def get_head_node_name(self, workerpool_name: str = "workerpool0"):
        """Get the host name of the head node from the cluster spec

        Returns:
            str: cluster
        """
        try:
            host_name = self.cluster_info.get(workerpool_name, {})[0].split(":")[0]
        except Exception as error:
            raise ValueError(
                f"Fetching the host name of the head node from {workerpool_name} \
                    failed with error: {error}. Please check the cluster configuration \
                    {self.cluster_config_dict}"
            )
        return host_name

    def get_open_port(self):
        """Get the open port for nodes communication

        Args:
            cluster_config_dict (dict): Vertex custom job cluster configuration

        Returns:
            str: The port of the head node
        """
        if "open_ports" in self.cluster_config_dict:
            port = self.cluster_config_dict["open_ports"][0]
        else:
            # Use any port for the non-distributed job.
            port = 7777
        return port

    def get_head_node_info(self):
        open_port = self.get_open_port()
        head_node_name = self.get_head_node_name()
        head_node_address = f"{head_node_name}:{open_port}"
        return head_node_name, open_port, head_node_address


class RayCluster(RayCustomJobSpec):
    """
    This class establishes a Ray cluster in a Vertex custom training job cluster
    """

    def __init__(self):
        super().__init__()
        (
            self.head_node_name,
            self.open_port,
            self.head_node_address,
        ) = self.get_head_node_info()
        self._logger.info(f"The head node address is {self.head_node_address}")

    def run_cmd(self, cmd: str, logging: bool = True):
        """Run a bash command

        Args:
            cmd (str): Bash command to be executed.
            logging (bool): Whether to log the result or not. Defaults to True.

        Returns:
            str: The command result as a string
        """
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=True
            )
            self._logger.info(f"{cmd} executed successfully.")
            output = result.stdout
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"Command({cmd})failed with return code {error.returncode}: {error.stderr}"
            )
        if logging:
            self._logger.info(output)
        return output

    def start_ray_cluster(self):
        """Ran a Ray command to start a head node of a Ray cluster"""
        self.run_cmd(
            cmd=f"ray \
                      start \
                      --head \
                     --port={self.open_port} \
                     --redis-shard-ports={self.open_port}"
        )
        time.sleep(5)

    def check_nodes(
        self,
        node_address: str,
        target_num: int = 1,
    ):
        """Check if the number of nodes in the target address is over a certain amount

        Args:
            node_address(str): The node address for getting the node status.
            target_num (int, optional): The expected number of nodes.Default to 1.
        """
        cluster_status = self.run_cmd(
            cmd=f"ray \
                status \
                --address={node_address}",
            logging=False,
        )

        nodes_id = re.findall(r"1 node_.+", cluster_status)
        num_nodes = len(nodes_id)
        self._logger.debug(
            f"{num_nodes} of {target_num} found in the Ray cluster. They are {nodes_id}."
        )
        if num_nodes >= target_num:
            self._logger.info(f"{num_nodes} found in the Ray cluster {nodes_id}.")
            return True
        else:
            return False

    def wait_for_nodes(
        self,
        node_address: str,
        min_nodes: int = 1,
        timeout: int = 300,
        retry_interval_ms: int = 5000,
    ):
        """Wait util the number of nodes meets the requirement

        Args:
            node_address (str): The node address for getting the node status
            timeout (int, optional):  Maximum timeout in seconds.. Defaults to 300.
            retry_interval_ms (int, optional): Retry interval in milliseconds. Defaults to 5000.
        """
        self._logger.info("Waiting for nodes to be connected.")
        wait_for_condition(
            condition_predictor=self.check_nodes,
            timeout=timeout,
            retry_interval_ms=retry_interval_ms,
            **{"node_address": node_address, "target_num": min_nodes},
        )

    def connect_to_node(
        self, node_address: str, timeout: int = 300, retry_interval_ms: int = 5000
    ) -> None:
        """Connect worker node to the head node

        Args:
            node_address (str): The node address for getting the node status
            timeout (int, optional):  Maximum timeout in seconds.. Defaults to 300.
            retry_interval_ms (int, optional): Retry interval in milliseconds. Defaults to 5000.
        """
        wait_for_condition(
            condition_predictor=self.check_nodes,
            timeout=timeout,
            retry_interval_ms=retry_interval_ms,
            **{"node_address": node_address},
        )
        time.sleep(10)
        self.run_cmd(
            cmd=f"ray \
                     start \
                     --address={node_address}"
        )
        self._logger.info(f"{self.workerpool_type} has connected to {node_address}")

    def stop_process(self):
        """Stop Ray processes"""
        self.run_cmd(cmd="ray stop")

    def tear_down_cluster(self):
        """Tear down a Ray cluster."""
        self.run_cmd(cmd="ray down -y")
