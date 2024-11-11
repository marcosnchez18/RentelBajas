const urlParams = new URLSearchParams(window.location.search);
const cuentaID = urlParams.get('id');

// Cargar información del cliente desde localStorage
const clienteSeleccionado = JSON.parse(localStorage.getItem('clienteSeleccionado'));

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

// Obtener los productos del cliente por ID específico de cuenta
async function obtenerProductos(id) {
    try {
        const response = await fetch(`http://10.58.6.89:8082/cliente/${id}/products`);
        const productos = await response.json();
        let productosHTML = "";

        if (productos.lineas_moviles && Object.keys(productos.lineas_moviles).length > 0) {
            productosHTML += `<h4 class="text-lg font-semibold text-gray-700 mb-2">Líneas Móviles</h4><ul>`;
            Object.values(productos.lineas_moviles).forEach(linea => {
                productosHTML += `<li class="flex items-center p-2 bg-gray-200 rounded mb-2">
                    <input type="checkbox" class="mr-2"> 
                    <span class="font-semibold">Número:</span> ${linea.DDI}, 
                    <span class="font-semibold">Tarifa:</span> ${linea.NomTarifa}, 
                    <span class="font-semibold">Precio:</span> ${linea.PvpCuotaTarifa}€
                </li>`;
            });
            productosHTML += `</ul>`;
        }

        if (productos.servicios_adicionales && Object.keys(productos.servicios_adicionales).length > 0) {
            productosHTML += `<h4 class="text-lg font-semibold text-gray-700 mb-2">Servicios Adicionales</h4><ul>`;
            Object.values(productos.servicios_adicionales).forEach(servicio => {
                productosHTML += `<li class="flex items-center p-2 bg-gray-200 rounded mb-2">
                    <input type="checkbox" class="mr-2"> 
                    <span class="font-semibold">Descripción:</span> ${servicio.Descripcion}, 
                    <span class="font-semibold">Precio:</span> ${servicio.Precio}€
                </li>`;
            });
            productosHTML += `</ul>`;
        }

        document.getElementById("cuentasResumen").innerHTML = productosHTML || "<p class='text-gray-600'>No hay productos contratados.</p>";
    } catch (error) {
        console.error("Error al obtener productos:", error);
    }
}

obtenerProductos(cuentaID);
