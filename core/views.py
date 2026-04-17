from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistroSerializer
from .utils import sync_to_sheets, get_pollen_data, generar_pronostico_ia, generar_pdf_desde_template
import random

class RegistroAPIView(APIView):

    def post(self, request):
    
        data = request.data
        ciudad = data.get('ubicacion', '')
        
        datos_meteorologicos = get_pollen_data(ciudad)
        print(f"Datos de Open-Meteo: {datos_meteorologicos}")

        full_name = data.get('nombre', '')
        parts = full_name.split(' ', 1)
        nombre = parts[0]
        apellidos = parts[1] if len(parts) > 1 else ''

        riesgos = ['Bajo', 'Moderado', 'Alto', 'Muy Alto']
        nivel = random.choice(riesgos)

        processed_data = {
            'nombre_completo': full_name,
            'nombre': nombre,
            'apellidos': apellidos,
            'fecha_nacimiento': data.get('fechaNacimiento'),
            'ciudad': ciudad,
            'alergias': data.get('alergias'),
            'email': data.get('email'),
            'nivel_riesgo': nivel
        }

        serializer = RegistroSerializer(data=processed_data)
        if serializer.is_valid():
            usuario = serializer.save()
            clima = get_pollen_data(usuario.ciudad)
            texto_ia = generar_pronostico_ia(usuario, clima)

            try:
                pdf_path = generar_pdf_desde_template(usuario, texto_ia)
            except Exception as e:
                print(f"Fallo al generar el PDF: {e}")

            try:
                sync_to_sheets(usuario)
            except Exception as e:
                print(f"{e}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)         

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    