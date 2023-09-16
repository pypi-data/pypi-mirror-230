import os

import pytest

from radops.jobs.gcp import (
    create_instance_from_template,
    delete_instance,
    list_instances,
    list_templates,
)


# since this is a long test, only run if the TEST_GCP environment variable is set
@pytest.mark.skipif(
    os.getenv("TEST_GCP") is None, reason="requires env variable TEST_GCP"
)
def test_start_delete():
    template_name = "smol-cpu-1"
    assert template_name in list_templates()
    initial_n_instances = len(list_instances())
    create_instance_from_template("test-instance-1", "smol-cpu-1")

    assert len(list_instances()) == initial_n_instances + 1

    delete_instance("test-instance-1")
    assert len(list_instances()) == initial_n_instances
