import django.apps
from behave import given, step


@given("models are available")
def models_are_available(context):
    models = django.apps.apps.get_models(
        include_auto_created=True, include_swapped=True
    )
    context.models = {
        **{model._meta.model_name: model for model in models},
        **{model._meta.object_name: model for model in models},
        **{model._meta.db_table: model for model in models},
        **{model._meta.verbose_name: model for model in models},
        **{model._meta.verbose_name_plural: model for model in models},
    }


@step('a "{model_name}" model is available')
def model_is_available(context, model_name):
    if not getattr(context, "models", None):
        context.execute_steps(f"Given models are available")
    model = context.models.get(model_name)
    context.test.assertTrue(model)
