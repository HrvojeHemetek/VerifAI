from rest_framework import serializers
from .models import *


class SurveysSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveysModel
        fields = ['id', 'file', 'sample_size', 'relevant_factors','country', 'created_at']
