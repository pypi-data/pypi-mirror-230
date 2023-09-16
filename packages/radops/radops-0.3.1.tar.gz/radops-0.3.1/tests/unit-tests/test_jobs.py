from radops.jobs.executor import (
    ExecutorType,
    add_executor,
    get_executor,
    list_executors,
    load_all_executors,
)


def test_list_add_get_executor(settings_fixture):
    load_all_executors()
    assert list_executors() == ["local"]

    add_executor(
        "exc name",
        type=ExecutorType.MANUALLY_CONFIGURED,
        hostname="host",
        username="user",
    )

    assert list_executors() == ["local", "exc name"]

    local_exc = get_executor("local")
    assert local_exc.type == ExecutorType.LOCAL
    assert local_exc.is_local
    assert local_exc.hostname is None
    assert local_exc.username is None

    exc = get_executor("exc name")
    assert exc.type == ExecutorType.MANUALLY_CONFIGURED
    assert exc.hostname == "host"
    assert exc.username == "user"
