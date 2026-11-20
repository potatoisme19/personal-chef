from ..graph import chef_graph
from ..state import ChefOutput


def discover_recipe(request: str) -> ChefOutput:
    """Run the end-to-end recipe discovery workflow and return its final state."""
    return chef_graph.invoke({"request": request})
