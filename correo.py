import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Importa MIMEText para los mensajes de correo en formato HTML

def enviar_correo_confirmacion(email_cliente, enlace_confirmacion):
    smtp_server = "smtp.gmail.com"  
    smtp_port = 587
    smtp_user = "barbers18sanlucar@gmail.com"  
    smtp_password = "xjollzcifdpsekjz"

    mensaje = MIMEMultipart()
    mensaje["From"] = smtp_user
    mensaje["To"] = email_cliente
    mensaje["Subject"] = "Confirmación de Baja de Productos"

    # Contenido del mensaje simplificado
    body = f"""
    <p>Sentimos mucho que haya decidido dar de baja sus p.</p>
    <p>Ha solicitado la baja de algunos productos de Rentel Wifi.</p>
    <p>Para confirmarlos, haga clic en el siguiente enlace:</p>
    <a href="{enlace_confirmacion}">Confirmar Baja</a>
    """
    mensaje.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Inicia una conexión segura
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_cliente, mensaje.as_string())
            print("Correo enviado correctamente a:", email_cliente)
    except Exception as e:
        print("Error al enviar el correo:", e)
