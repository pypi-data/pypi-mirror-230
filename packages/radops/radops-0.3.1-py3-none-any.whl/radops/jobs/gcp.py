from typing import Any, List

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1
from google.oauth2 import service_account

from radops import radops_print
from radops.jobs.executor import ExecutorType, add_executor
from radops.settings import settings


def get_credentials():
    return service_account.Credentials.from_service_account_file(
        settings.gcp_key
    )


def get_client() -> compute_v1.InstancesClient:
    """Get a client for interacting with the GCP Compute API."""
    credentials = get_credentials()
    return compute_v1.InstancesClient(credentials=credentials)


def wait_for_extended_operation(
    operation: ExtendedOperation,
    verbose_name: str = "operation",
    timeout: int = 300,
) -> Any:
    result = operation.result(timeout=timeout)

    if operation.error_code:
        radops_print(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}"
        )
        radops_print(f"Operation ID: {operation.name}")
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        radops_print(f"Warnings during {verbose_name}:\n")
        for warning in operation.warnings:
            radops_print(
                f" - {warning.code}: {warning.message}",
            )

    return result


def create_instance_from_template(
    instance_name: str, template_name: str
) -> compute_v1.Instance:
    instance_client = get_client()

    instance_template_url = f"global/instanceTemplates/{template_name}"

    instance_insert_request = compute_v1.InsertInstanceRequest()
    instance_insert_request.project = settings.gcp_project_id
    instance_insert_request.zone = settings.gcp_zone
    instance_insert_request.source_instance_template = instance_template_url
    instance_insert_request.instance_resource.name = instance_name

    radops_print(f"Creating instance '{instance_name}'.")
    operation = instance_client.insert(instance_insert_request)
    wait_for_extended_operation(operation, "instance creation")
    radops_print(f"Instance {instance_name} created.")
    return instance_client.get(
        project=settings.gcp_project_id,
        instance=instance_name,
        zone=settings.gcp_zone,
    )


def list_instances() -> List[compute_v1.Instance]:
    instance_client = get_client()
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = settings.gcp_project_id
    # Use the `max_results` parameter to limit the number of results that the API returns per response page.
    request.max_results = 50

    agg_list = instance_client.aggregated_list(request=request)

    all_instances = []
    # Despite using the `max_results` parameter, you don't need to handle the pagination
    # yourself. The returned `AggregatedListPager` object handles pagination
    # automatically, returning separated pages as you iterate over the results.
    for _, response in agg_list:
        if response.instances:
            all_instances.extend(response.instances)
    return all_instances


def get_public_ip(instance: compute_v1.Instance) -> str:
    return instance.network_interfaces[0].access_configs[0].nat_i_p


def get_username(instance: compute_v1.Instance) -> str:
    assert instance.metadata.items[0].key == "ssh-keys"
    split = instance.metadata.items[0].value.split(":")
    assert split[1].startswith("ssh-rsa")
    return split[0]


def executor_from_instance(instance: compute_v1.Instance) -> None:
    add_executor(
        type=ExecutorType.GCP,
        name=instance.name,
        hostname=get_public_ip(instance),
        username=get_username(instance),
    )


def create_gcp_executor(name: str, template_name: str):
    instance = create_instance_from_template(name, template_name)
    executor_from_instance(instance)


def stop_instance(instance_name: str) -> None:
    instance_client = get_client()

    radops_print(f"Stopping {instance_name}.")
    operation = instance_client.stop(
        project=settings.gcp_project_id,
        zone=settings.gcp_zone,
        instance=instance_name,
    )
    wait_for_extended_operation(operation, "instance stopping")
    radops_print(f"Instance {instance_name} stopped.")


def delete_instance(instance_name: str) -> None:
    instance_client = get_client()

    radops_print(f"Deleting instance '{instance_name}'.")
    operation = instance_client.delete(
        project=settings.gcp_project_id,
        zone=settings.gcp_zone,
        instance=instance_name,
    )
    wait_for_extended_operation(operation, "instance deletion")
    radops_print(f"Instance {instance_name} deleted.")


def list_templates() -> List[str]:
    template_client = compute_v1.InstanceTemplatesClient(
        credentials=get_credentials()
    )
    return [
        t.name for t in template_client.list(project=settings.gcp_project_id)
    ]
