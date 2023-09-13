import subprocess
from upload_pytorch_model.utils.gcs_helper import (
    stage_files_locally,
    split_bucket_object_file,
    upload_to_gcs,
)


def run_command(
    model_name: str,
    serialized_file: str,
    handler: str,
    version: str = None,
    extra_files: str = None,
    requirements: str = None,
):
    """Execute command to create torch model archiver"""

    cmd = [
        "torch-model-archiver",
        "-f",
        f"--model-name={model_name}",
        f"--serialized-file={serialized_file}",
        f"--handler={handler}",
    ]

    # TODO: There has to be a neater way of doing this
    if extra_files and len(extra_files) > 0:
        cmd += [f"--extra-files={extra_files}"]
    if version:
        cmd += [f"--version={version}"]
    if requirements:
        cmd += [f"--requirements-file={requirements}"]

    process = subprocess.run(cmd, capture_output=True, shell=False)
    process.check_returncode()

    return cmd


def create_model_archiver(
    gcs_model_path: str,
    model_name: str,
    version: str,
    local_model_file: str,
    handler: str,
    extra_files_staging_path: str = None,
    extra_files_to_ignore: list = [],
    extra_prediction_files: str = None,
    requirements: str = None,
    custom_tokenizer_path: str = None,
    custom_tokenizer_name: str = None,
):
    """
    Create model archiver file. For this, it needs to stage locally the following files:

        1. Model artifact + model files in same folder (outputted by default by HuggingFace)
        2. Optionally, it can download:
            2.1 Custom handler file
            2.2 Requirements file
            2.3 Custom tokemizer artifact
            2.4 Additional files required for prediction
    """
    model_bucket_name, model_object_name, _ = split_bucket_object_file(
        path=gcs_model_path
    )
    if extra_files_staging_path:
        (
            extra_files_staging_bucket,
            extra_files_staging_object,
            _,
        ) = split_bucket_object_file(path=extra_files_staging_path)

    print("Staging model file locally...")
    stage_files_locally(
        bucket_name=model_bucket_name,
        object_name=model_object_name,
        file_name=local_model_file,
    )

    print("Staging additional model files locally...")
    extra_files = stage_files_locally(
        bucket_name=model_bucket_name,
        object_name=model_object_name,
        ignore_files=extra_files_to_ignore + [local_model_file],
        model_extra_files=True,
    )

    if handler.endswith(".py"):  # Custom handler script
        print("Staging custom handler file locally")
        stage_files_locally(
            bucket_name=extra_files_staging_bucket,
            object_name=extra_files_staging_object,
            file_name=handler,
        )
    if requirements:
        print("Staging model requirements file locally")
        stage_files_locally(
            bucket_name=extra_files_staging_bucket,
            object_name=extra_files_staging_object,
            file_name=requirements,
        )

    if extra_prediction_files:
        extra_files = extra_files + "," + extra_prediction_files
        print("Staging extra prediction files locally")
        for prediction_file in extra_prediction_files.split(","):
            stage_files_locally(
                bucket_name=extra_files_staging_bucket,
                object_name=extra_files_staging_object,
                file_name=prediction_file,
            )

    if custom_tokenizer_path:
        print("Staging custom tokenizer locally")
        (
            custom_tokenizer_bucket,
            custom_tokenizer_object,
            custom_tokenizer_name,
        ) = split_bucket_object_file(
            path=extra_files_staging_path, file_name=custom_tokenizer_name
        )
        stage_files_locally(
            bucket_name=custom_tokenizer_bucket,
            object_name=custom_tokenizer_object,
            file_name=custom_tokenizer_name,
        )
        extra_files = extra_files + "," + custom_tokenizer_name

    if len(extra_files) > 0 and extra_files[0] == ",":
        extra_files = extra_files[1:]

    print("Run TAR packaging")
    cmd = run_command(
        model_name=model_name,
        version=version,
        serialized_file=local_model_file,
        handler=handler,
        extra_files=extra_files,
        requirements=requirements,
    )

    print("Uploading to GCS")
    upload_to_gcs(
        bucket_name=model_bucket_name,
        object_name=model_object_name,
        model_name=model_name,
    )
