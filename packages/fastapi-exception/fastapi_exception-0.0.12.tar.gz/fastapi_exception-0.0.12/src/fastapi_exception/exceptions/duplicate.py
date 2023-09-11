from pydantic import PydanticValueError


class DuplicateError(PydanticValueError):
    code = 'duplicate'
    msg_template = '{property} is already in used'

    def __init__(self, property_name: str):
        super().__init__(property=property_name)
