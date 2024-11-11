
const urlParams = new URLSearchParams(window.location.search);
const cuentaID = urlParams.get('id');


async function cargarDatosConfirmacion() {
    try {
        const response = await fetch(`/api/confirmacion_datos?id=${cuentaID}`);
        const data = await response.json();

        if (data.error) {
            document.getElementById("clienteInfo").innerHTML = "<p class='text-red-500'>Error: No se encontraron los datos del cliente.</p>";
            return;
        }

      
        document.getElementById("nombre").textContent = data.nombre;
        document.getElementById("dni").textContent = data.dni;
        document.getElementById("email").textContent = data.email;
        document.getElementById("telefonofijo").textContent = data.telefonofijo;
        document.getElementById("telefonomovil").textContent = data.telefonomovil;
        document.getElementById("direccion").textContent = `${data.direccion}, ${data.poblacion}, ${data.codpostal}`;

        // productos seleccionados
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


function confirmarBaja() {
    alert("Baja confirmada (en desarrollo)");
}


function rechazarBaja() {
    alert("Baja rechazada (en desarrollo)");
}


cargarDatosConfirmacion();
