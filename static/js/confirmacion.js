// Obtener los parámetros de la URL
const urlParams = new URLSearchParams(window.location.search);
const cuentaID = urlParams.get('id');

// Cargar datos del cliente y productos seleccionados desde el backend
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
        document.getElementById("dni").textContent = data.dni;
        document.getElementById("email").textContent = data.email;
        document.getElementById("telefonofijo").textContent = data.telefonofijo;
        document.getElementById("telefonomovil").textContent = data.telefonomovil;
        document.getElementById("direccion").textContent = `${data.direccion}, ${data.poblacion}, ${data.codpostal}`;

        // Mostrar los productos seleccionados
        const productosList = document.getElementById("productosList");
        data.productos.forEach((producto) => {
            const li = document.createElement("li");
            li.textContent = producto;
            productosList.appendChild(li);
        });

    } catch (error) {
        console.error("Error al cargar datos:", error);
    }
}

// Función para manejar la confirmación
function confirmarBaja() {
    alert("Baja confirmada (en desarrollo)");
}

// Función para manejar el rechazo
function rechazarBaja() {
    alert("Baja rechazada (en desarrollo)");
}

// Llamar a la función para cargar los datos en la página
cargarDatosConfirmacion();
