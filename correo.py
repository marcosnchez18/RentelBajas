from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def enviar_correo_confirmacion(email_cliente, enlace_confirmacion):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "barbers18sanlucar@gmail.com"
    smtp_password = "xjollzcifdpsekjz"

    mensaje = MIMEMultipart("alternative")
    mensaje["From"] = smtp_user
    mensaje["To"] = email_cliente
    mensaje["Subject"] = "Confirmación de Baja de Productos"

    
    body_text = "Para confirmar la baja, haga clic en el siguiente enlace."

    
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

    
    mensaje.attach(MIMEText(body_text, "plain"))
    mensaje.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_cliente, mensaje.as_string())
            print("Correo enviado correctamente a:", email_cliente)
    except Exception as e:
        print("Error al enviar el correo:", e)
