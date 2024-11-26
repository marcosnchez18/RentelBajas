from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from itsdangerous import URLSafeTimedSerializer

# Configuración del token
SECRET_KEY = "clave_secreta_unica_para_tu_aplicacion"
serializer = URLSafeTimedSerializer(SECRET_KEY)


def generar_enlace(email_cliente, cuenta_id):
    token = serializer.dumps({"email": email_cliente, "cuenta_id": cuenta_id})
    return f"http://localhost:8000/confirmacion?token={token}"


def enviar_correo_confirmacion(email_cliente, enlace_confirmacion):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "barbers18sanlucar@gmail.com"
    smtp_password = "xjollzcifdpsekjz"

    mensaje = MIMEMultipart("related")  
    mensaje["From"] = smtp_user
    mensaje["To"] = email_cliente
    mensaje["Subject"] = "Confirmación de Baja de Productos"

    
    body_html = f"""
    <html>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9f9f9; color: #333;">
        <div style="background-color: #ffffff; width: 90%; margin: auto; padding: 20px; border-radius: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
            <!-- Logo -->
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="cid:logo" alt="Logo Rentel" style="width: 120px; height: auto;">
            </div>
            <!-- Mensaje principal -->
            <h2 style="text-align: center; color: #0a206c; font-weight: bold; margin-bottom: 15px;">Confirmación de Baja</h2>
            <p style="text-align: center; font-size: 16px; line-height: 1.5;">
                Sentimos mucho que hayas decidido dar de baja algunos de tus productos con <strong>Rentel Wifi</strong>.
                <br>Si deseas continuar, por favor confirma tu solicitud haciendo clic en el botón de abajo.
            </p>
            <!-- Botón de confirmación -->
            <div style="text-align: center; margin: 20px 0;">
                <a href="{enlace_confirmacion}" 
                    style="background-color: #0a206c; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; display: inline-block; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
                    Confirmar Baja
                </a>
            </div>
            <p style="text-align: center; font-size: 14px; color: #777; margin-bottom: 0;">
                Si no solicitaste esta acción, ignora este mensaje.
            </p>
        </div>

        <!-- Pie de página -->
        <div style="width: 90%; margin: 30px auto; padding: 20px; background-color: #0a206c; border-radius: 15px; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <!-- Oficina -->
                <div style="width: 30%; margin-bottom: 10px;">
                    <h4 style="margin-bottom: 10px; color: #ffd700;">Nuestra Oficina</h4>
                    <p style="font-size: 14px; line-height: 1.5;">
                        Av. Cabo Noval, 17<br>
                        11540 Sanlúcar de Barrameda<br>
                        Cádiz, España
                    </p>
                </div>
                <!-- Contacto -->
                <div style="width: 30%; margin-bottom: 10px;">
                    <h4 style="margin-bottom: 10px; color: #ffd700;">Contáctanos</h4>
                    <p style="font-size: 14px; line-height: 1.5;">
                        Teléfono: <a href="tel:+34856135158" style="color: #ffd700; text-decoration: none;">856 135 158</a><br>
                        Email: <a href="mailto:clientes@rentelwifi.com" style="color: #ffd700; text-decoration: none;">clientes@rentelwifi.com</a>
                    </p>
                </div>
                <!-- Redes sociales -->
                <div style="width: 30%; margin-bottom: 10px;">
                    <h4 style="margin-bottom: 10px; color: #ffd700;">Síguenos</h4>
                    <div style="display: flex; gap: 10px;">
                        <a href="https://api.whatsapp.com/send?phone={{movil_wassap}}&text={{text_wassap}}" target="_blank">
                            <img src="cid:logo-whatsapp" alt="WhatsApp" style="width: 32px; height: auto;">
                        </a>
                        <a href="mailto:{{destinatario}}">
                            <img src="cid:logo-email" alt="Email" style="width: 32px; height: auto;">
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
   
    mensaje.attach(MIMEText(body_html, "html"))

    
    imagenes = {
        "logo": "/static/img/logo.png",
        "logo-whatsapp": "/path/to/static/img/wasa.png",
        "logo-email": "/path/to/static/img/email.jpg"
    }

    for cid, img_path in imagenes.items():
        try:
            with open(img_path, "rb") as img_file:
                mime_img = MIMEImage(img_file.read())
                mime_img.add_header("Content-ID", f"<{cid}>")  
                mime_img.add_header("Content-Disposition", "inline", filename=img_path.split("/")[-1])
                mensaje.attach(mime_img)
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen en {img_path}")

    # Enviar correo
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
