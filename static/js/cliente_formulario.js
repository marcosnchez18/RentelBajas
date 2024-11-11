// Obtener el ID de la cuenta desde la URL
const urlParams = new URLSearchParams(window.location.search);
const cuentaID = urlParams.get("id");

// Cargar información del cliente desde localStorage
const clienteSeleccionado = JSON.parse(localStorage.getItem("clienteSeleccionado"));

if (clienteSeleccionado) {
    document.getElementById("nombre").value = clienteSeleccionado.nombre;
    document.getElementById("dni").value = clienteSeleccionado.dni;
    document.getElementById("email").value = clienteSeleccionado.email || "No disponible";
    document.getElementById("telefonofijo").value = clienteSeleccionado.telefonofijo;
    document.getElementById("telefonomovil").value = clienteSeleccionado.telefonomovil;
    document.getElementById("direccion").value = `${clienteSeleccionado.direccion}, ${clienteSeleccionado.poblacion}, ${clienteSeleccionado.codpostal}`;
} else {
    document.getElementById("clienteInfo").innerHTML = "<p class='text-red-500'>Error: Cliente no encontrado.</p>";
}

// Función para obtener productos del cliente por ID específico de cuenta
async function obtenerProductos(id) {
    try {
        const response = await fetch(`http://10.58.6.89:8082/cliente/${id}/products`);
        const productos = await response.json();
        let productosHTML = "";

        // Líneas Móviles
        if (productos.lineas_moviles && Object.keys(productos.lineas_moviles).length > 0) {
            productosHTML += `<h4 class="text-lg font-semibold text-gray-700 mb-4">Líneas Móviles</h4><div class="grid grid-cols-3 gap-4 mb-6">`;
            Object.values(productos.lineas_moviles).forEach(linea => {
                productosHTML += `
                    <div class="flex flex-col items-start p-4 bg-gray-200 rounded">
                        <input type="checkbox" class="mr-2 mb-2" value="Número: ${linea.DDI} - Tarifa: ${linea.NomTarifa} - Precio: ${linea.PvpCuotaTarifa}€">
                        <span><strong>Número:</strong> ${linea.DDI}</span>
                        <span><strong>Tarifa:</strong> ${linea.NomTarifa}</span>
                        <span><strong>Precio:</strong> ${linea.PvpCuotaTarifa}€</span>
                    </div>`;
            });
            productosHTML += `</div>`;
        }

        // Servicios Adicionales
        if (productos.servicios_adicionales && Object.keys(productos.servicios_adicionales).length > 0) {
            productosHTML += `<h4 class="text-lg font-semibold text-gray-700 mb-4">Servicios Adicionales</h4><div class="grid grid-cols-3 gap-4">`;
            Object.values(productos.servicios_adicionales).forEach(servicio => {
                productosHTML += `
                    <div class="flex flex-col items-start p-4 bg-gray-200 rounded">
                        <input type="checkbox" class="mr-2 mb-2" value="Descripción: ${servicio.Descripcion} - Precio: ${servicio.Precio}€">
                        <span><strong>Descripción:</strong> ${servicio.Descripcion}</span>
                        <span><strong>Precio:</strong> ${servicio.Precio}€</span>
                    </div>`;
            });
            productosHTML += `</div>`;
        }

        document.getElementById("cuentasResumen").innerHTML = productosHTML || "<p class='text-gray-600'>No hay productos contratados.</p>";
    } catch (error) {
        console.error("Error al obtener productos:", error);
    }
}


// Llama a la función de obtención de productos con el ID de la cuenta
obtenerProductos(cuentaID);

// Función para confirmar la baja y enviar el correo de confirmación
function confirmarBaja() {
    const productosSeleccionados = Array.from(document.querySelectorAll("#cuentasResumen input[type='checkbox']:checked"))
        .map(checkbox => checkbox.value);

    const email = document.getElementById("email").value;

    if (productosSeleccionados.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Sin Productos Seleccionados',
            text: 'No has seleccionado ningún producto para dar de baja.',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    if (email === "No disponible" || email.trim() === "") {
        Swal.fire({
            icon: 'warning',
            title: 'Correo No Disponible',
            text: 'Por favor, introduzca el email del cliente para actualizar la información de contacto.',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    const cuentaId = cuentaID;
    const nombre = document.getElementById("nombre").value;
    const direccion = document.getElementById("direccion").value;
    const telefonoFijo = document.getElementById("telefonofijo").value;
    const telefonoMovil = document.getElementById("telefonomovil").value;
    const telefono = telefonoMovil || telefonoFijo;

    const payload = {
        email: email,
        productos: productosSeleccionados,
        cuenta_id: cuentaId,
        nombre: nombre,
        direccion: direccion,
        telefono: telefono
    };

    fetch("/confirmar_baja", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw new Error(data.detail); });
        }
        return response.json();
    })
    .then(data => {
        Swal.fire({
            icon: 'success',
            title: 'Correo Enviado',
            text: data.message,
            confirmButtonText: 'Aceptar'
        });
    })
    .catch(error => {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'Hubo un problema al enviar el correo de confirmación.',
            confirmButtonText: 'Aceptar'
        });
    });
}
