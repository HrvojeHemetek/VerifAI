from django.db import models

class SurveysModel(models.Model):
    file = models.FileField(upload_to='surveys/')
    sample_size = models.IntegerField()
    relevant_factors = models.JSONField()
    country = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)