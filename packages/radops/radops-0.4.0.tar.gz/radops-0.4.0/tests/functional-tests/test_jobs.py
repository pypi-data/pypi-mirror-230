import os
import shutil
import time
from unittest.mock import patch

import pytest

from radops.jobs.executor import get_executor, get_logs, job_pipeline
from radops.settings import settings


@pytest.mark.skipif(shutil.which("docker") is None, reason="requires docker")
def test_local_executors_pipeline():
    executor = get_executor("local")  # local executor

    with patch("radops.jobs.executor.push_image") as patched_push, patch(
        "radops.jobs.executor.LocalDockerJobExecutor.pull"
    ) as patched_pull, patch(
        "radops.jobs.executor.LocalDockerJobExecutor.login"
    ) as patched_login:
        job_id = job_pipeline(executor, "demos/remote_execution")

    assert patched_push.call_count == 1
    assert patched_pull.call_count == 1
    assert patched_login.call_count == 1
    assert isinstance(job_id, str)
    # give it some time to run
    time.sleep(1)
    assert get_logs(executor, job_id) == "Hello world.\n"

    with patch("radops.jobs.executor.push_image") as patched_push, patch(
        "radops.jobs.executor.LocalDockerJobExecutor.pull"
    ) as patched_pull, patch(
        "radops.jobs.executor.LocalDockerJobExecutor.login"
    ) as patched_login:
        job_id = job_pipeline(
            executor, "demos/remote_execution", command="'Other text'"
        )

    assert patched_push.call_count == 1
    assert patched_pull.call_count == 1
    assert isinstance(job_id, str)
    # give it some time to run
    time.sleep(1)
    assert get_logs(executor, job_id) == "Other text\n"

    with patch("radops.jobs.executor.push_image") as patched_push, patch(
        "radops.jobs.executor.LocalDockerJobExecutor.pull"
    ) as patched_pull, patch(
        "radops.jobs.executor.LocalDockerJobExecutor.login"
    ) as patched_login:
        job_id = job_pipeline(
            executor, "demos/remote_execution", command="settings"
        )
    time.sleep(1)
    assert settings.email in get_logs(executor, job_id)


@pytest.mark.skipif(
    os.getenv("REMOTE_TEST_EXECUTOR") is None,
    reason="requires env variable REMOTE_TEST_EXECUTOR",
)
def test_remote_executors_pipeline():
    # for some reason this test is failing if not run with pytest -s option???
    executor = get_executor(os.environ["REMOTE_TEST_EXECUTOR"])

    job_id = job_pipeline(executor, "demos/remote_execution")

    assert isinstance(job_id, str)
    # give it some time to run
    time.sleep(1)
    assert get_logs(executor, job_id) == "Hello world.\n"

    job_id = job_pipeline(
        executor, "demos/remote_execution", command="'Other text'"
    )

    assert isinstance(job_id, str)
    # give it some time to run
    time.sleep(1)
    assert get_logs(executor, job_id) == "Other text\n"
