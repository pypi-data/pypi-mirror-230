"""Utility functions for EC2 VPC Endpoint Service Configurations."""
from typing import Any
from typing import Dict


async def convert_raw_resource_to_present_async(
    hub, ctx, idem_resource_name: str, resource_id: str, raw_resource: dict
) -> Dict[str, Any]:
    r"""
    Convert raw resource of vpc_endpoint_service_configuration type into present format.
    """
    resource_translated = {"resource_id": resource_id}

    resource_parameters = {
        "ServiceType": "service_type",
        "ServiceId": "service_id",
        "ServiceName": "service_name",
        "ServiceState": "service_state",
        "AvailabilityZones": "availability_zones",
        "AcceptanceRequired": "acceptance_required",
        "ManagesVpcEndpoints": "manages_vpc_endpoints",
        "NetworkLoadBalancerArns": "network_load_balancer_arns",
        "GatewayLoadBalancerArns": "gateway_load_balancer_arns",
        "SupportedIpAddressTypes": "supported_ip_address_types",
        "BaseEndpointDnsNames": "base_endpoint_dns_names",
        "PrivateDnsName": "private_dns_name",
        "PrivateDnsNameConfiguration": "private_dns_name_configuration",
        "PayerResponsibility": "payer_responsibility",
    }

    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource and raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    # The resource name could be given by the input or auto generated
    # Default idem creation adds name to tags with Name key (as specified in AWS console)
    resource_name = (
        raw_resource.get("tags", {}).get("Name")
        or idem_resource_name
        or raw_resource.get("ServiceName")
    )
    resource_translated["name"] = resource_name

    resource_translated["tags"] = hub.tool.aws.tag_utils.convert_tag_list_to_dict(
        raw_resource.get("Tags")
    )

    return resource_translated


def evaluate_update_desired_state(
    hub, ctx, current_state: dict, desired_state: dict
) -> Dict[str, Any]:
    r"""
    Evaluates desired state for updating vpc_endpoint_service_configuration
    """
    (
        is_config_equal,
        network_lb_added,
        network_lb_removed,
    ) = _evaluate_added_removed_config(
        "network_load_balancer_arns", current_state, desired_state
    )
    if not is_config_equal:
        desired_state["add_network_load_balancer_arns"] = network_lb_added
        desired_state["remove_network_load_balancer_arns"] = network_lb_removed
    (
        is_config_equal,
        gateway_lb_added,
        gateway_lb_removed,
    ) = _evaluate_added_removed_config(
        "gateway_load_balancer_arns", current_state, desired_state
    )
    if not is_config_equal:
        desired_state["add_gateway_load_balancer_arns"] = gateway_lb_added
        desired_state["remove_gateway_load_balancer_arns"] = gateway_lb_removed
    (
        is_config_equal,
        ip_address_types_added,
        ip_address_types_removed,
    ) = _evaluate_added_removed_config(
        "supported_ip_address_types", current_state, desired_state
    )
    if not is_config_equal:
        desired_state["add_supported_ip_address_types"] = ip_address_types_added
        desired_state["remove_supported_ip_address_types"] = ip_address_types_removed

    # Default to False. If desired state no longer wants to have private dns name, we can switch it to True.
    desired_state["remove_private_dns_name"] = False
    if (
        current_state.get("private_dns_name", None) is not None
        and desired_state.get("private_dns_name") is None
    ):
        desired_state["remove_private_dns_name"] = True

    return desired_state


def _evaluate_added_removed_config(
    config_name: str, current_state: dict, desired_state: dict
):
    current = current_state.get(config_name, None)
    desired = desired_state.get(config_name, None)

    is_config_equal = current == desired
    added = list(set(desired) - set(current)) if desired else None
    removed = list(set(current) - set(desired)) if current else None

    if config_name in desired_state:
        del desired_state[config_name]

    return is_config_equal, added, removed
