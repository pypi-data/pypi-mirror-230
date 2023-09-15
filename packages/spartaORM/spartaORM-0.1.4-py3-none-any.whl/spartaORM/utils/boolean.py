from typing import Union

def str_to_bool(value: Union[str, bool]):
    if type(value) == bool:
        return value

    if str(value).lower() in ["true", "1"]:
        return True
    
    return False
