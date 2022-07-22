from rest_framework.serializers import ModelSerializer
from .models import Company


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "status", "application_link", "last_update", "notes"]
