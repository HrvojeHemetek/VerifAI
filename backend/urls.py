from django.urls import path
from .views.SurveyView import SurveyView


urlpatterns = [
    path('survey/', SurveyView.as_view(), name='survey-view'),
]
