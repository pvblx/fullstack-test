from django.db import models
import uuid

class RegistroUsuario(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre_completo = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    ciudad = models.CharField(max_length=100)
    alergias = models.JSONField()  # Guardaremos la lista de alergias
    email = models.EmailField(unique=True)
    nivel_riesgo = models.CharField(max_length=50, default="Medio") # Nivel inventado
    creado_en = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.nombre_completo
