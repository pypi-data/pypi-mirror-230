# PRIVATE README FROM HERE. DO NOT COPY TO PUBLIC REPO !!!!
# NON-PUBLIC README

## Look at README.md for general info on the package

## Installation

### Public install
Some parts of the communication interface which are closely tied to Kelvins ip is removed.

     pip install k-lights-interface

### Private install

    git clone https://x-token-auth:ATCTT3xFfGN0aNwiJqPZeEV_KJ9QA3Y4J9NSLztvrYbZX-ZtS3a-OCOmgp8b4h-4QcPzFhUXtEosYYfaCLBs9F09USsoiy6vnaK20Yp2yKLVIeR9m2TA0FEd6yUvLkTf1kfgIzW_q7zGNAvzaD87grhW9J1w_gIZk9ZS3DQ0na7HhJxTC32_YrM=8EA4C238@bitbucket.org/riftlabs/k-lights-interface-py.git



You can use the following in a requirements.txt file

    git+https://x-token-auth:ATCTT3xFfGN0aNwiJqPZeEV_KJ9QA3Y4J9NSLztvrYbZX-ZtS3a-OCOmgp8b4h-4QcPzFhUXtEosYYfaCLBs9F09USsoiy6vnaK20Yp2yKLVIeR9m2TA0FEd6yUvLkTf1kfgIzW_q7zGNAvzaD87grhW9J1w_gIZk9ZS3DQ0na7HhJxTC32_YrM=8EA4C238@bitbucket.org/riftlabs/k-lights-interface-py.git


## Distributing public version of this package
Make sure build and twine is installed

     pip install build
     pip install twine
     Run the "script_publish_package.py" in scripts/ folder


Manual publish commands:

     python3 -m build
     python3 -m twine upload dist/*

### Uploading to pypi using twine

    twine upload dist/* -u __token__ -p  pypi-AgEIcHlwaS5vcmcCJGYzZjc2NTBmLWQ4YjgtNDc5ZC04ZDM5LTA0NGJkMmYxZjVkZQACKlszLCJlOWExZTJiOC1kOWZlLTQ0NTItODJhZi1lNzIwM2EyNjI2OTUiXQAABiAj1HbWT0DI6U8mYYQDCU8A59CkT8l6bB3Ri7Gc17ERjg

## Updating protocol buffers file

Ensure at workspace root

Run this to generate the proto files for internal use
     
     python -m grpc_tools.protoc -I raw_proto/ --python_betterproto_out=src/k_lights_interface/ k_full.proto

Run this to generate the proto files for public use

     python -m grpc_tools.protoc -I raw_proto/ --python_betterproto_out=src/k_lights_interface/ k_public.proto

## Running tests
Ensure workspace at root

     pytest

