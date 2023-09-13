from django.shortcuts import get_object_or_404

from .models import Questionaire
from huscy.project_design.models import DataAcquisitionMethodType
from huscy.project_design.services import create_data_acquisition_method


def create_questionaire(session, name, filehandle, user, location=''):
    data_acquisition_method_type = get_object_or_404(DataAcquisitionMethodType, pk='questionaire')

    data_acquisition_method = create_data_acquisition_method(
        session=session,
        type=data_acquisition_method_type,
        location=location,
    )

    return Questionaire.objects.create(
        data_acquisition_method=data_acquisition_method,
        filehandle=filehandle,
        name=name,
        uploaded_by=user.get_full_name(),
    )


def delete_questionaire(questionaire):
    questionaire.data_acquisition_method.delete()


def get_questionaires(session):
    return (Questionaire.objects.filter(data_acquisition_method__session=session)
                                .order_by('data_acquisition_method__order'))


def update_questionaire(questionaire, name):
    questionaire.name = name
    questionaire.save()
    return questionaire
