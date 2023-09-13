from pathlib import Path
from kfp.components import load_component_from_file

# Get the current directory as a Path object
current_dir = Path(__file__).resolve().parent

# Find all directories in the current directory that are not prefixed with "_"
components = [
    x for x in current_dir.iterdir() if x.is_dir() and not x.name.startswith("_")
]

# Load the components and create global variables for each of them
for component in components:
    component_yaml_path = component / f"{component.name}/component.yaml"
    globals()[component.name] = load_component_from_file(component_yaml_path)

# Define __all__ as the list of loaded components
__all__ = [component.name for component in components]
