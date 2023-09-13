from django.db import models
from django.utils.translation import gettext_lazy as _

from huscy.project_design.models import DataAcquisitionMethod


def get_upload_path(instance, filename):
    project_id = instance.data_acquisition_method.session.experiment.project.id
    return f'projects/{project_id}/data_acquisition_methods/questionaires/{filename}'


class Questionaire(models.Model):
    data_acquisition_method = models.ForeignKey(DataAcquisitionMethod, on_delete=models.CASCADE)

    name = models.CharField(_('Name'), max_length=255)

    filehandle = models.FileField(upload_to=get_upload_path, verbose_name=_('Filehandle'))

    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False)
    uploaded_by = models.CharField(max_length=255, editable=False)
