import os
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.generativeai as genai
from googleapiclient.http import MediaIoBaseDownload
import io
from datetime import date
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '10ujDCxoNBYFAd5Swrgw-wLW0GFkUSEZ7dd_h5A1LgUc' 
genai.configure(api_key="AIzaSyAMn4ruMJOHb7Hz0-k2Z8nUeAStdFNoNQs")

def sync_to_sheets(user_data):
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds) 
    sheet = service.spreadsheets()

    row = [
        str(user_data.id_unico),
        user_data.nombre_completo,
        user_data.nombre,
        user_data.apellidos,
        str(user_data.fecha_nacimiento),
        user_data.ciudad,
        user_data.nivel_riesgo,
        ", ".join(user_data.alergias),
        user_data.email
    ]

    body = {'values': [row]}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Hoja 1!A1",
        valueInputOption="RAW",
        body=body
    ).execute()


def get_pollen_data(city_name):
  
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=es&format=json"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json() #Como Meteo utiliza coordenadas, paso Nombre Ciudad a Coordenadas

        if 'results' not in geo_data:
            print(f"No se encontraron coordenadas")
            return None

        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        ciudad_detectada = geo_data['results'][0]['name']

        air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=olive_pollen,grass_pollen,mugwort_pollen,alder_pollen,birch_pollen&timezone=auto"
        air_response = requests.get(air_url)
        air_data = air_response.json()

        current_data = air_data.get('current', {})
        
        
        return current_data

    except Exception as e:
        print(f"Error Open-Meteo: {e}")
        return None


def obtener_estacion_actual():

    hoy = date.today()
    mes_dia = (hoy.month, hoy.day)

    if (3, 20) <= mes_dia <= (6, 20):
        return "Primavera"
    elif (6, 21) <= mes_dia <= (9, 21):
        return "Verano"
    elif (9, 22) <= mes_dia <= (12, 20):
        return "Otoño"
    else:
        return "Invierno"
    


def generar_pronostico_ia(usuario, clima):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    estacion = obtener_estacion_actual()
    prompt = f"""
    Eres un experto en salud y bienestar. Redacta un "Pronóstico de Estado de Ánimo y Salud" 
    personalizado para {usuario.nombre} que vive en {usuario.ciudad}.
    
    Contexto:
    - Estación: {estacion}.
    - Alergias del usuario: {", ".join(usuario.alergias)}.
    - Datos actuales de polen (µg/m³): {clima}.
    
    Instrucciones:
    1. Sé motivador pero profesional.
    2. Explica cómo el clima de hoy afectará su alergia.
    3. Da 3 consejos prácticos de salud para esta semana.
    4. Termina con una frase de ánimo.
    Escribe el texto en formato párrafo, máximo 200 palabras.
    """
    
    response = model.generate_content(prompt)
    return response.text

def generar_pdf_desde_template(usuario, texto_ia):

    TEMPLATE_ID = '1X-aeZW9XhHyL2Hdiv8nNRtKS_x2TAxNnjaL00v-QHDA'
    carpeta_reportes = "Reportes"
    
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents'])
    
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)

    
    requests_insert = [
        {
            'replaceAllText': {
                'containsText': {'text': '{{CONTENIDO_IA}}', 'matchCase': True},
                'replaceText': texto_ia,
            }
        },
        {
            'replaceAllText': {
                'containsText': {'text': '{{NOMBRE_USUARIO}}', 'matchCase': True},
                'replaceText': usuario.nombre,
            }
        }
    ]
    docs_service.documents().batchUpdate(documentId=TEMPLATE_ID, body={'requests': requests_insert}).execute()

    
    request_pdf = drive_service.files().export_media(fileId=TEMPLATE_ID, mimeType='application/pdf')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_pdf)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


    pdf_filename = os.path.join(carpeta_reportes, f"informe_{usuario.id_unico}.pdf")
    with open(pdf_filename, "wb") as f:
        f.write(fh.getvalue())


    requests_undo = [
        {
            'replaceAllText': {
                'containsText': {'text': texto_ia, 'matchCase': True},
                'replaceText': '{{CONTENIDO_IA}}',
            }
        },
        {
            'replaceAllText': {
                'containsText': {'text': usuario.nombre, 'matchCase': True},
                'replaceText': '{{NOMBRE_USUARIO}}',
            }
        }
    ]
    docs_service.documents().batchUpdate(documentId=TEMPLATE_ID, body={'requests': requests_undo}).execute()
    
    return pdf_filename


def enviar_email_bienvenida(usuario, clima, pdf_path):
    subject = f"¡Bienvenido a tualergiahoy, {usuario.nombre}!"
    remitente = 'tualergiahoy@gmail.com'
    destinatario = [usuario.email]

    polen_lista = ""
    for clave, valor in clima.items():
        if "pollen" in clave:
            nombre_limpio = clave.replace('_pollen', '').capitalize()
            polen_lista += f"<li style='margin-bottom: 5px;'><strong>{nombre_limpio}:</strong> {valor} µg/m³</li>"

    html_content = f"""
    <div style="font-family: sans-serif; color: #333333; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background-color: #1E1B4B; padding: 25px; text-align: center;">
            <h1 style="color: #FFFFFF; margin: 0; font-size: 24px; letter-spacing: 1px;">tualergiahoy.com</h1>
        </div>
        
        <div style="padding: 30px; background-color: #FFFFFF;">
            <h2 style="color: #FF6B5A; margin-top: 0;">¡Hola {usuario.nombre}!</h2>
            <p style="font-size: 16px; line-height: 1.5;">Gracias por registrarte en nuestra plataforma. Tu salud respiratoria es nuestra prioridad.</p>
            
            <div style="background-color: #f9fafb; border-left: 4px solid #FF6B5A; padding: 15px; margin: 25px 0;">
                <p style="margin-top: 0; font-weight: bold; font-size: 15px;">Niveles actuales de polen en {usuario.ciudad}:</p>
                <ul style="margin-bottom: 0; padding-left: 20px; font-size: 14px;">
                    {polen_lista}
                </ul>
            </div>
            
            <p style="font-size: 16px; line-height: 1.5;">Te hemos adjuntado tu <strong>pronóstico de salud y estado de ánimo</strong> para esta semana. Nuestro asistente de IA lo ha redactado teniendo en cuenta la estación actual y tus alergias específicas.</p>
            
            <div style="text-align: center; margin-top: 35px; margin-bottom: 10px;">
                <a href="http://localhost:3000" style="background-color: #FF6B5A; color: #FFFFFF; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Acceder a mi panel</a>
            </div>
        </div>
    </div>
    """

    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, remitente, destinatario)
    msg.attach_alternative(html_content, "text/html")

    if os.path.exists(pdf_path):
        msg.attach_file(pdf_path)
    
    msg.send()