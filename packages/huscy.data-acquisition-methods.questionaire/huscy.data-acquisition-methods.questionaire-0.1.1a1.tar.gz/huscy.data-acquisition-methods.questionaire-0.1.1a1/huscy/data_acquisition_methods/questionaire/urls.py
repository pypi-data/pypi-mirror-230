from django.urls import include, path

from . import views
from huscy.project_design.urls import session_router


session_router.register('questionaires', views.QuestionaireViewSet, basename='questionaire')


urlpatterns = (
    path('api/', include(session_router.urls)),
)
