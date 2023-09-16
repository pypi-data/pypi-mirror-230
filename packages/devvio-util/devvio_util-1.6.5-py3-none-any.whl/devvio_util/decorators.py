from functools import wraps
from marshmallow import ValidationError


def validate_with_schema(input_schema, output_schema):
    """Decorator to validate input with a given schema."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            input_data = input_schema().dump(args[1])
            errors = input_schema().validate(input_data)
            if errors:
                raise ValidationError(f"{errors}")
            output = f(*args, **kwargs)
            output_data = output_schema().dump(output)
            errors = output_schema().validate(output_data)
            if errors:
                raise ValidationError(f"{errors}")
            return output
        return wrapper
    return decorator
