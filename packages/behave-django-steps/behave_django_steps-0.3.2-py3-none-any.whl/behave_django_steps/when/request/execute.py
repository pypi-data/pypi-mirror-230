from behave import step, when


@step("api client is available")
def api_client_is_available(context):
    try:
        from rest_framework.test import APIClient

        context.test.api_client = APIClient()
    except ImportError:
        raise ImportError("Django REST Framework is not installed.")


@when('I make a "{method}" request to "{url}"')
def make_request(context, method, url):
    context.response = getattr(context.test.client, method.lower())(url)


@when('I make a "{method}" request to "{url}" with data')
def make_request_with_data(context, method, url):
    context.response = getattr(context.test.client, method.lower())(
        url, data=context.request_data
    )


@when('I make an API "{method}" request to "{url}"')
def make_api_request(context, method, url):
    context.execute_steps("Given api client is available")
    context.response = getattr(context.test.api_client, method.lower())(
        url, format="json"
    )


@when('I make an API "{method}" request to "{url}" with data')
def make_api_request_with_data(context, method, url):
    context.execute_steps("Given api client is available")
    context.response = getattr(context.test.api_client, method.lower())(
        url, data=context.request_data, format="json"
    )
