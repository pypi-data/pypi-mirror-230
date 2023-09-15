from marshmallow import ValidationError


class SerializeError(ValueError):
    pass


class DeserializeError(ValueError):
    pass


class InputValidationError(ValidationError):
    def __init__(self, ve: ValidationError):
        super().__init__(
            ve.messages,
            ve.field_name,
            ve.data,
            ve.valid_data
        )


class OutputValidationError(ValidationError):
    def __init__(self, ve: ValidationError):
        super().__init__(
            ve.messages,
            ve.field_name,
            ve.data,
            ve.valid_data
        )


class InternalInputValidationError(ValidationError):
    pass


class InternalOutputValidationError(ValidationError):
    pass


class DevvError(Exception):
    def __init__(self, *args):
        if args:
            self._message = args[0]
        else:
            self._message = None

    def __str__(self):
        if self._message:
            return "DevvError: {}".format(self._message)
        return "Unspecified DevvError"

