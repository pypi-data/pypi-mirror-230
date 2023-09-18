"""Response status steps."""
import json

from behave import then
from django.http import JsonResponse


@then("a response is available")
def response_is_available(context):
    """Check that a response is available."""
    context.test.assertTrue(getattr(context, "response", None) is not None)


@then('status code "{status_code}" is returned')
def response_status_code_is(context, status_code):
    """Check that the response status code is the given value."""
    context.execute_steps("Then a response is available")
    print(context.response)
    if hasattr(context.response, "data"):
        if not isinstance(context.response, JsonResponse):
            context.response.data = json.loads(context.response.content)
        print(context.response.data)
        print(context.response.content)
    context.test.assertEqual(context.response.status_code, int(status_code))
