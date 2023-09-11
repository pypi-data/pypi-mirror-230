"""Azure Container App resource."""

from app.common.component import Component
from app.common.resource import Resource
from diagrams.azure import compute
from typing import Dict


class ContainerApp(Resource):
    """Base resource component."""

    @staticmethod
    def identifier() -> str:
        """Get the identifier for this type in TF."""
        return "azurerm_container_app"

    @staticmethod
    def get_metadata(component: Component) -> str:
        """Get the metadata string from this components attributes."""
        if "revision_mode" in component.attributes and "template" in component.attributes:
            revision_mode = component.attributes['revision_mode']
            image = component.attributes['template'][0]['container'][0]["image"]
 
            return ", ".join([
                ('Revision Mode:' + str(revision_mode) + ''),
                ('Image:' + str(image))
            ])
        else:
            return ""

    @staticmethod
    def get_node(component: Component, **attrs: Dict):
        """Get the underlying diagrams type."""
        metadata = ContainerApp.get_metadata(component)
        return compute.ContainerInstances(Resource.get_name(component, metadata), **attrs)
