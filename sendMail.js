const nodemailer = require("nodemailer");

async function sendConfirmationEmail(email) {
    // Configura tu cuenta de Gmail aquí
    const transporter = nodemailer.createTransport({
        service: "gmail",
        auth: {
            user: "your-email@gmail.com",
            pass: "your-app-password"  // Usa una contraseña de aplicación
        }
    });

    // Contenido del correo electrónico
    const mailOptions = {
        from: "your-email@gmail.com",
        to: email,
        subject: "Confirmación de Baja de Productos de Rentel",
        html: `
            <h3>Solicitud de Baja de Productos</h3>
            <p>Ha solicitado la baja de sus productos de Rentel. Por favor, haga clic en el siguiente enlace para confirmar su solicitud:</p>
            <a href="https://your-domain.com/confirmacion-baja">Confirmar Baja de Productos</a>
            <p>Gracias,</p>
            <p>El equipo de Rentel</p>
        `
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log("Correo de confirmación enviado a:", email);
    } catch (error) {
        console.error("Error al enviar el correo:", error);
    }
}

module.exports = sendConfirmationEmail;
