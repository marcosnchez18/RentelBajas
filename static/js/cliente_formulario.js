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

        if (productos.lineas_moviles && Object.keys(productos.lineas_moviles).length > 0) {
            productosHTML += `<h4 class="text-lg font-semibold text-gray-700 mb-2">Líneas Móviles</h4><ul>`;
            Object.values(productos.lineas_moviles).forEach(linea => {
                const productoDetalles = `Número: ${linea.DDI}, Tarifa: ${linea.NomTarifa}, Precio: ${linea.PvpCuotaTarifa}€`;
                productosHTML += `<li class="flex items-center p-2 bg-gray-200 rounded mb-2">
                    <input type="checkbox" class="mr-2" value="${productoDetalles}"> 
                    <span>${productoDetalles}</span>
                </li>`;
            });
            productosHTML += `</ul>`;
        }

        if (productos.servicios_adicionales && Object.keys(productos.servicios_adicionales).length > 0) {
            productosHTML += `<h4 class="text-lg font-semibold text-gray-700 mb-2">Servicios Adicionales</h4><ul>`;
            Object.values(productos.servicios_adicionales).forEach(servicio => {
                const productoDetalles = `Descripción: ${servicio.Descripcion}, Precio: ${servicio.Precio}€`;
                productosHTML += `<li class="flex items-center p-2 bg-gray-200 rounded mb-2">
                    <input type="checkbox" class="mr-2" value="${productoDetalles}"> 
                    <span>${productoDetalles}</span>
                </li>`;
            });
            productosHTML += `</ul>`;
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
    // Obtener los productos seleccionados con toda su información
    const productosSeleccionados = Array.from(document.querySelectorAll("#cuentasResumen input[type='checkbox']:checked"))
        .map(checkbox => checkbox.value);

    // Obtener información del cliente desde el formulario
    const email = document.getElementById("email").value;
    const cuentaId = cuentaID;
    const nombre = document.getElementById("nombre").value;
    const direccion = document.getElementById("direccion").value;
    const telefonoFijo = document.getElementById("telefonofijo").value;
    const telefonoMovil = document.getElementById("telefonomovil").value;
    const telefono = telefonoMovil || telefonoFijo;  // Priorizar móvil si está disponible

    // Enviar la solicitud POST a confirmar_baja
    fetch("/confirmar_baja", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: email,
            productos: productosSeleccionados,
            cuenta_id: cuentaId,
            nombre: nombre,
            direccion: direccion,
            telefono: telefono
        })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error("Error:", error));
}
