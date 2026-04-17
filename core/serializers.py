from rest_framework import serializers
from .models import RegistroUsuario

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroUsuario
        fields = '__all__'

