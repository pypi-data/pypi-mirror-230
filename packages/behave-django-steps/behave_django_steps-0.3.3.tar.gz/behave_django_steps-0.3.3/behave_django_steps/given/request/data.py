"""Request data steps."""
from behave import given


@given("request data is available")
def request_data_is_available(context):
    """Make sure request data is available."""
    if not hasattr(context, "request_data"):
        context.request_data = {}


@given('the request has "{key}" with "{value}"')
def request_has_key_with_value(context, key, value):
    """Add a key with a value to the request data."""
    context.execute_steps("Given request data is available")
    context.request_data[key] = value


@given('the request has "{key}" boolean {value}')
def request_has_key_with_boolean_value(context, key, value):
    """Add a key with a boolean value to the request data."""
    context.execute_steps("Given request data is available")
    value = value.lower()
    if value == "true":
        value = True
    elif value == "false":
        value = False
    else:
        raise ValueError(f"Invalid boolean value: {value}")
    context.request_data[key] = value


@given('the request has "{key}" with {value}')
def request_has_key_with_numeric_value(context, key, value):
    """Add a key with a value to the request data."""
    context.execute_steps("Given request data is available")
    if "." in value:
        value = float(value)
    else:
        value = int(value)
    context.request_data[key] = value


@given('the request has values in "{key}"')
def request_has_values_in_key(context, key):
    """Add a key with a value to the request data."""
    context.execute_steps("Given request data is available")
    context.request_data[key] = context.table.rows
