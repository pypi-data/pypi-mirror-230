"""Execute request steps."""
from behave import step, when


@step("api client is available")
def api_client_is_available(context):
    """API client is available."""
    try:
        from rest_framework.test import (  # pylint: disable=import-outside-toplevel
            APIClient,
        )

        context.test.api_client = APIClient()
    except ImportError as exc:
        raise ImportError("Django REST Framework is not installed.") from exc


@when('I make a "{method}" request to "{url}"')
def make_request(context, method, url):
    """Make a request."""
    context.response = getattr(context.test.client, method.lower())(url)


@when('I make a "{method}" request to "{url}" with data')
def make_request_with_data(context, method, url):
    """Make a request with data."""
    context.response = getattr(context.test.client, method.lower())(
        url, data=context.request_data
    )


@when('I make an API "{method}" request to "{url}"')
def make_api_request(context, method, url):
    """Make an API request."""
    context.execute_steps("Given api client is available")
    context.response = getattr(context.test.api_client, method.lower())(
        url, format="json"
    )


@when('I make an API "{method}" request to "{url}" with data')
def make_api_request_with_data(context, method, url):
    """Make an API request with data."""
    context.execute_steps("Given api client is available")
    context.response = getattr(context.test.api_client, method.lower())(
        url, data=context.request_data, format="json"
    )
