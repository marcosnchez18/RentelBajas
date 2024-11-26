const urlParams = new URLSearchParams(window.location.search);
const cuentaID = urlParams.get("id");

// Cargar datos para mostrar al cliente
async function cargarDatosConfirmacion() {
    try {
        const response = await fetch(`/api/confirmacion_datos?id=${cuentaID}`);
        const data = await response.json();

        if (data.error) {
            document.getElementById("clienteInfo").innerHTML = "<p class='text-red-500'>Error: No se encontraron los datos del cliente.</p>";
            return;
        }

        // Mostrar los datos del cliente
        document.getElementById("nombre").textContent = data.nombre;
        document.getElementById("email").textContent = data.email;
        document.getElementById("telefonofijo").textContent = data.telefonofijo;
        document.getElementById("telefonomovil").textContent = data.telefonomovil;
        document.getElementById("direccion").textContent = `${data.direccion}, ${data.poblacion}, ${data.codpostal}`;

        // Asignar el evento al botón de confirmar baja
        document.getElementById("confirmarBajaBtn").addEventListener("click", () => confirmarBaja(data.productos));

        // Mostrar productos seleccionados
        const productosList = document.getElementById("productosList");
        productosList.innerHTML = ""; // Limpiar lista en caso de recarga
        data.productos.forEach((producto) => {
            const li = document.createElement("li");
            li.textContent = producto;
            productosList.appendChild(li);
        });
    } catch (error) {
        console.error("Error al cargar datos:", error);
    }
}

// Función para confirmar baja e insertar en la tabla `bajas`
async function confirmarBaja(productosSeleccionados) {
    // Mostrar SweetAlert de confirmación
    const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: 'Estás a punto de dar de baja tus productos. ¿Quieres continuar?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, confirmar',
        cancelButtonText: 'No, cancelar'
    });

    if (result.isConfirmed) {
        // Preparar los datos para la solicitud
        const payload = {
            id_cliente: cuentaID,
            lineas_moviles: productosSeleccionados.filter(p => p.includes("Número:")), // Filtros dinámicos
            servicios_adicionales: productosSeleccionados.filter(p => p.includes("Descripción:"))
        };

        try {
            const response = await fetch('/confirmar_baja', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                await Swal.fire({
                    title: '¡Baja completada!',
                    text: 'Tu baja se ha completado exitosamente. Esperamos volver a verte en el futuro.',
                    icon: 'success',
                    confirmButtonText: 'Aceptar'
                });
            } else {
                const errorData = await response.json();
                Swal.fire({
                    title: 'Error',
                    text: `No se pudo registrar la baja: ${errorData.detail}`,
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        } catch (error) {
            console.error("Error al confirmar baja:", error);
            Swal.fire({
                title: 'Error',
                text: 'Hubo un problema al confirmar la baja. Inténtalo de nuevo más tarde.',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        }
    } else {
        // El usuario canceló
        Swal.fire({
            title: 'Cancelado',
            text: 'No se han realizado cambios.',
            icon: 'info',
            confirmButtonText: 'Aceptar'
        });
    }
}

// Inicializar carga de datos cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", cargarDatosConfirmacion);
