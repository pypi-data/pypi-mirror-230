# Utility function to help with dealing with json files + content.

import json
from pathlib import Path
from typing import Union
from typing import TypeVar, Type

from drewcopytools.filetools import _toStr
from drewcopytools.filetools import read_utf8_file

T = TypeVar('T')

# --------------------------------------------------------------------------------------------------------------
def load_json(path: Union[Path,str]) -> json:
    """
    Load a json file from the given path, returning a json instance.
    This function will load json data with or without a BOM in the data.
    """    
    data = read_utf8_file(path)
    res = json.loads(data)
    return res

# -----------------------------------------------------------------------------------------------
def map_json_to_class(json_data: dict, class_type: Type[T]) -> T:
    # Create an instance of the specified class
    instance = class_type()

    # Iterate over the JSON data
    for key, value in json_data.items():
        # Check if the instance has an attribute with the same name as the JSON key
        if hasattr(instance, key):
            # Set the attribute value on the instance
            setattr(instance, key, value)

    return instance

# -----------------------------------------------------------------------------------------------
def load_json_type(path: Union[Path,str],class_type: Type[T]) -> T:
    jsonData = load_json(path)
    res : T = map_json_to_class(jsonData, class_type)
    return res

# # -----------------------------------------------------------------------------------------------
# def 

# # -----------------------------------------------------------------------------------------------
# def map_json_to_class(json_data:json, instance:any) -> any:
#     # Iterate over the JSON data
#     for key, value in json_data.items():
#         # Check if the instance has an attribute with the same name as the JSON key
#         if hasattr(instance, key):
#             # Set the attribute value on the instance
#             setattr(instance, key, value)

#     return instance

