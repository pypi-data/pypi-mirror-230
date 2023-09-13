from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from . import serializer, services
from huscy.project_design.models import Session


class QuestionaireViewSet(CreateModelMixin, DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = IsAuthenticated,
    serializer_class = serializer.QuestionaireSerializer

    def initial(self, request, *args, **kwargs):
        self.session = get_object_or_404(
            Session,
            experiment=self.kwargs['experiment_pk'],
            experiment__project=self.kwargs['project_pk'],
            pk=self.kwargs['session_pk'],
        )
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_questionaires(self.session)

    def perform_create(self, serializer):
        serializer.save(session=self.session)

    def perform_destroy(self, questionaire):
        services.delete_questionaire(questionaire)
