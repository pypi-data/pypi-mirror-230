from radops.jobs.executor import (
    add_executor,
    list_executors,
    load_all_executors,
)


def test_list_and_add_executor(settings_fixture):
    load_all_executors()
    assert list_executors() == ["local"]

    add_executor("exc name", hostname="host", username="user")

    assert list_executors() == ["local", "exc name"]
