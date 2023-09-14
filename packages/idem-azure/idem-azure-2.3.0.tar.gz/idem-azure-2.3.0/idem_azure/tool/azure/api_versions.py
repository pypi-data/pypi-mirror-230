from dict_tools.data import NamespaceDict

# Azure API versions by service/resource

# In plugin code, API version can be accessed either as a constant/expression or as a function call result.
# Sample code (both variants should return api_version "2021-12-01"):
#   api_version = hub.tool.azure.api_versions.compute.disks
#   api_version = hub.tool.azure.api_versions.get_api_version('compute.disks')


def get_api_version(hub, resource_type: str) -> str:
    if resource_type.startswith("azure."):
        resource_type = resource_type.replace("azure.", "")

    ref = hub.tool.azure.api_versions
    for path_segment in resource_type.split("."):
        ref = ref[path_segment]

    return ref


compute = NamespaceDict(
    {
        "disks": "2021-12-01",
        "virtual_machines": "2022-03-01",
    }
)

sql_database = NamespaceDict(
    {
        "databases": "2021-11-01",
    }
)

network = NamespaceDict(
    {
        "network_interfaces": "2021-08-01",
        "virtual_networks": "2022-07-01",
        "virtual_network_peerings": "2021-03-01",
    }
)
