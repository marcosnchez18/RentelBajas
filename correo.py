from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from itsdangerous import URLSafeTimedSerializer

# Configuración del token
SECRET_KEY = "clave_secreta_unica_para_tu_aplicacion"
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Función para generar un enlace con token
def generar_enlace(email_cliente, cuenta_id):
    token = serializer.dumps({"email": email_cliente, "cuenta_id": cuenta_id})
    return f"http://localhost:8000/confirmacion?token={token}"

# Enviar correo
def enviar_correo_confirmacion(email_cliente, enlace_confirmacion):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "barbers18sanlucar@gmail.com"
    smtp_password = "xjollzcifdpsekjz"

    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = smtp_user
    mensaje["To"] = email_cliente
    mensaje["Subject"] = "Confirmación de Baja de Productos"

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
            <p>Sentimos mucho que haya decidido dar de baja algunos de sus productos de Rentel Wifi.</p>
            <p>Esperamos volver a verle en el futuro.</p>
            <p>Para confirmar la baja, por favor, haga clic en el siguiente enlace:</p>
            <a href="{enlace_confirmacion}" style="color: #1a73e8;">Confirmar Baja</a>
        </body>
    </html>
    """
    mensaje.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_cliente, mensaje.as_string())
            print("Correo enviado correctamente a:", email_cliente)
    except Exception as e:
        print("Error al enviar el correo:", e)

# Función para verificar el token
def verificar_token(token, max_age=86400):
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except Exception:
        return None
