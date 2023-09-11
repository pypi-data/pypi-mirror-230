"""Azure Container App Environment resource."""

from app.common.component import Component
from app.common.resource import Resource
from diagrams.azure import compute
from typing import Dict, List

from app.azure.resources.azurerm_container_app import ContainerApp


class ContainerAppEnvironment(Resource):
    """Base resource component."""

    @staticmethod
    def identifier() -> str:
        """Get the identifier for this type in TF."""
        return "azurerm_container_app_environment"

    @staticmethod
    def get_metadata(component: Component) -> str:
        """Get the metadata string from this components attributes."""
        return ""

    @staticmethod
    def get_node(component: Component, **attrs: Dict):
        """Get the underlying diagrams type."""
        metadata = ContainerAppEnvironment.get_metadata(component)
        return compute.ContainerInstances(Resource.get_name(component, metadata), **attrs)
       
    @staticmethod
    def group(components: List[Component]) -> List[Component]:
        """Handle groupings."""
        container_groups = [
            x for x in components if x.type.startswith(ContainerAppEnvironment.identifier())]
        container_apps = [
            x for x in components if x.type == ContainerApp.identifier()]
        
        for container_app in container_apps:
            container_app_environment_id = container_app.attributes["container_app_environment_id"]
            container_app_environment_name = container_app_environment_id.split("/")[-1]
                
            container_app_environment = next(filter(
                    lambda x: x.attributes["id"] == container_app_environment_id, container_groups), None)

            if container_app_environment == None:
                container_app_environment = Component(
                    container_app_environment_name, ContainerAppEnvironment.identifier(), "data", container_app.resource_group, {"name": container_app_environment_name, "resource_group_name": container_app.resource_group})
                container_groups.append(container_app_environment)

            container_app_environment.add_component(container_app)

        return container_groups
