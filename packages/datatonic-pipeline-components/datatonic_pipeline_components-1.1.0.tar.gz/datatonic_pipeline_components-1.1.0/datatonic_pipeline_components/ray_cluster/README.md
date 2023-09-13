# Server-less Ray Cluster Component

This component deploys a Ray Cluster on Vertex AI in a server-less way. Once the cluster is deployed, the users could submit commands to run any tasks in the cluster.

## Inputs
|Name|Description|Type|Default|
|---|---|---|---|
|ray_task_cmd|The commands to run in the Ray cluster. |String||
|node_config_cmd|The command for extra setups on all nodes.For example, installing the dependencies or cloning a codebase.|String|None|
|min_nodes|The minimum nodes required in the Ray cluster|Integer|1|
|cluster_op_timeout| Maximum timeout in seconds of any Ray cluster establish jobs|Integer| 300|
|retry_interval_ms| Retry interval in milliseconds of any Ray cluster establish jobs.|Integer|5000|
|nodes_alive_time|The amount of time that a node is alive|Integer|24*60*60 (1 day)|

Note:
Multi-line commands are also supported to make the component more flexible to use and easily to read. The following example consists 2 steps:
1. Clone the ray repository to a local directory
2. Run a python script `xgboost_benchmark.py` with two flags `--smoke-test`, `--disable-check`
```python
    task_command = ( 
    "git clone https://github.com/ray-project/ray || true;"
    "python ray/release/air_tests/air_benchmarks/workloads/xgboost_benchmark.py"
    "--smoke-test --disable-check"
    )
```

## Outputs
None

## Usage
You can find an example notebook `datatonic_pipeline_components/ray_cluster/example/example.ipynb` that reproduces the official Ray example - [Ray AIR XGBoostTrainer on Kubernetes](https://docs.ray.io/en/latest/cluster/kubernetes/examples/ml-example.html#) without deploying a Kubernetes Cluster.

Basically, this component takes two key arguments, `ray_task_cmd` and `node_config_cmd`. You can use `node_config_cmd` to install extra dependencies, set up environment variables, pull code base and more. `ray_task_cmd` is a string of command(s) that will be submitted to run in the deployed ray cluster.


### None-distributed task using the Ray Framework

```python
import kfp

#Use the component as part of the pipeline
@kfp.dsl.pipeline(name='ray-tasks')
def ray_tasks_pipeline():
    #Ray task commands
    task_command = ( 
    "git clone https://github.com/ray-project/ray || true;"
    "python ray/release/air_tests/air_benchmarks/workloads/xgboost_benchmark.py"
    "--smoke-test --disable-check"
    )

    # Load component
    ray_cluster_op = load_component_from_file(
    "./<path-to-component>/component.yaml"
    )
    ray_cluster_op (
        ray_task_cmd=task_command
    ).set_display_name("ray-tasks")
```



### Distributed Ray

The purpose of using Ray is to run tasks in a distributed manner.To maximise the utility of this component, it is recommended to use [create_custom_training_job_from_component](https://cloud.google.com/vertex-ai/docs/pipelines/customjob-component#create_custom_training_job_from_component)
to create a Ray cluster with multiple worker nodes. Set `enable_web_access` to `True` of the custom training job for debugging purpose. Since it takes time for the worker nodes to be connected to the cluster, passing value to `min_nodes` of the component will hold the tasks until the number of nodes in the cluster exceeds the expected number.

```python
import kfp

#Use the component as part of the pipeline
@kfp.dsl.pipeline(name='ray-tasks')
def ray_tasks_pipeline():

    #Ray task commands
    task_command = ( 
    "git clone https://github.com/ray-project/ray || true;"
    "python ray/release/air_tests/air_benchmarks/workloads/xgboost_benchmark.py"
    "--size 100G --disable-check"
    )

    # Load component
    ray_cluster_op = load_component_from_file(
    "./<path-to-component>/component.yaml"
    )

    # Instantiate custom training job spec
    custom_ray_cluster_op = create_custom_training_job_from_component(
        component_spec=ray_cluster_op,
        machine_type="e2-standard-16",
        replica_count=10,
        enable_web_access=True
    )

    # Create a Ray cluster with multiple worker nodes,
    custom_ray_cluster(
            project="dt-pat-sandbox-dev",
        location="europe-west2",
        ray_task_cmd=task_command
    ).set_display_name("ray_100G")
```

### Ray Debug
To debug at the runtime, please follow the instruction below:
1. Set `enable_web_access` to True when creating the custom training job component
1. Open the Vertex Pipeline UI
2. Find the distributed training component
3. Click `view job`
4. Look for `Training Debugging` field in the popped up page
5. Launch web terminal
6. Use 
   - `ray summary tasks` to check the task status
   - `ray status` to check the usage of the computational resources

[!image](example/debug_instruction.jpg)

  
