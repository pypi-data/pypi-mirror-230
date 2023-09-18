"""Response data steps."""
from behave import then


@then("values exist in the response")
def response_values_exist(context):
    """Check that values exist in the response."""
    context.test.assertTrue(context.table)
    context.test.assertTrue(context.table[0].as_dict())
    for row in context.table:
        for key, value in row.as_dict().items():
            context.test.assertEqual(
                context.response.data[key], value, f"Key: {key}, Value: {value}"
            )


@then('values exist in "{response_key}" in the response')
def response_values_exist_at_key(context, response_key):
    """Check that values exist in the response."""
    context.test.assertTrue(context.table)
    context.test.assertTrue(context.table[0].as_dict())
    data = context.response.data.get(response_key, {})
    for row in context.table:
        for key, value in row.as_dict().items():
            context.test.assertEqual(data[key], value, f"Key: {key}, Value: {value}")
