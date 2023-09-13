from django.apps import AppConfig


class HuscyApp(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'huscy.data_acquisition_methods.questionaire'

    class HuscyAppMeta:
        pass

    def ready(self):
        from huscy.project_design.models import DataAcquisitionMethodType

        DataAcquisitionMethodType.objects.get_or_create(
            short_name='questionaire',
            defaults=dict(
                name='Questionaire',
            ),
        )
