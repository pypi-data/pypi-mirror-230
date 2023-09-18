"""Model filter steps."""
from behave import then


@then('a "{model_name}" with values exists')
def model_is_available_with_field_value(context, model_name):
    """Check if a model with the given values exists."""
    context.execute_steps(f'Given a "{model_name}" model is available')
    model = context.models[model_name]
    context.test.assertTrue(context.table)
    context.test.assertTrue(context.table[0].as_dict())
    setattr(
        context, model_name, model.objects.filter(**context.table[0].as_dict()).first()
    )
    context.test.assertTrue(getattr(context, model_name))


@then('a "{model_name}" with values does not exist')
def model_is_not_available_with_field_value(context, model_name):
    """Check if a model with the given values does not exist."""
    context.execute_steps(f'Given a "{model_name}" model is available')
    model = context.models[model_name]
    setattr(
        context, model_name, model.objects.filter(**context.table[0].as_dict()).first()
    )
    context.test.assertTrue(getattr(context, model_name) is None)
