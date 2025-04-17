import os
import sys
import importlib.util

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Path to the current folder
custom_node_dir = os.path.dirname(__file__)

# Add the folder to sys.path just in case
if custom_node_dir not in sys.path:
    sys.path.append(custom_node_dir)

# Walk through all files in the custom node directory
for filename in os.listdir(custom_node_dir):
    filepath = os.path.join(custom_node_dir, filename)

    # Skip __init__.py and non-Python files
    if filename == "__init__.py" or not filename.endswith(".py"):
        continue

    try:
        module_name = os.path.splitext(filename)[0]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Collect mappings if present
        if hasattr(module, "NODE_CLASS_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

        print(f"✔ Loaded node module: {module_name}")
    except Exception as e:
        print(f"❌ Failed to load module {filename}: {e}")

print(f"✅ RK_Comfyui loaded with {len(NODE_CLASS_MAPPINGS)} nodes")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
