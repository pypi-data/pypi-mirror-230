from pydantic import BaseModel
from xcloud.utils.logging import configure_logger
from typing import List

logger = configure_logger(__name__)

def map_pydantic_class_to_dict(pydantic_object: BaseModel):
    dict_result = {}

    for key_str in pydantic_object.__fields__.keys():
        property_value = getattr(pydantic_object, key_str)
        new_key = "{}_{}".format(pydantic_object.__class__.__name__.upper(), key_str.upper())
        
        # Will pick the default value
        if property_value is not None:
            if isinstance(property_value, BaseModel):
                nested_object_dict = map_pydantic_class_to_dict(property_value)
                dict_result = {**dict_result, **nested_object_dict}
            else:
                dict_result[new_key] = property_value

    logger.debug("Dict of values: {}".format(dict_result))

    return dict_result