import os
import subprocess
import argparse
# Get the absolute path of the workspace root
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Set the current working directory to the workspace root
os.chdir(workspace_root)
print(f"Current working directory: {workspace_root}")

from create_public_proto import create_public_proto

import subprocess

def main(args: argparse.Namespace):
    python_path = args.python_path
    # Create the public proto file
    create_public_proto()
    # Build the public proto file
    ret = subprocess.run([f"{python_path}", '-m', 'grpc_tools.protoc', '-I', 'raw_proto/', '--python_betterproto_out=src/k_lights_interface/', 'k_public.proto'], stdout=subprocess.PIPE, stderr=subprocess.PIPE , text=True)
    if ret.stderr and "No module" in ret.stderr:
        print(f"Unable to generate proto {ret.stderr}")
        return -1
    ret = subprocess.run([f"{python_path}", '-m', 'build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE , text=True)
    if ret.stderr and "No module" in ret.stderr:
        print(f"Unable to build distribution {ret.stderr}")
        return -1
    
    print("Now you can publish the package to pypi using the upload command found in PRIVATE_README.md")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--python-path",
        action="store_true",
        help="path to the python executable that has the required packages installed",
        default=".venv/Scripts/python.exe",
    )
    args = parser.parse_args()
    ret = main(args)
    if ret != 0:
        print("Failed to publish package")