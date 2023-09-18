"""Model create steps."""
from behave import given


@given('a "{model_name}" with values')
def create_model_with_fields(context, model_name):
    """Create a model with the given values."""
    context.execute_steps(f'Given a "{model_name}" model is available')
    model = context.models[model_name]
    context.test.assertTrue(context.table)
    context.test.assertTrue(context.table[0].as_dict())
    setattr(context, model_name, model.objects.create(**context.table[0].as_dict()))
    context.test.assertTrue(getattr(context, model_name))
