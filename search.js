document.getElementById("searchForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const searchType = document.getElementById("searchType").value;
    const searchValue = document.getElementById("searchValue").value;

    try {
        const response = await fetch("http://10.58.6.89:8082/get_data_client_baja_for_dni", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ [searchType]: searchValue })
        });
        const data = await response.json();

        if (data.length === 0 || data.error) {
            document.getElementById("error").classList.remove("hidden");
            document.getElementById("error").textContent = data.error || "No se encontraron datos para la búsqueda proporcionada.";
            document.getElementById("clienteData").classList.add("hidden");
        } else {
            document.getElementById("error").classList.add("hidden");
            document.getElementById("clienteData").classList.remove("hidden");
            mostrarClientes(data);
        }
    } catch (error) {
        document.getElementById("error").classList.remove("hidden");
        document.getElementById("error").textContent = "Error al conectar con la API.";
        document.getElementById("clienteData").classList.add("hidden");
    }
});

function mostrarClientes(clientes) {
    const clienteTableBody = document.getElementById("clienteTableBody");
    clienteTableBody.innerHTML = "";

    clientes.forEach((cliente) => {
        const productosContratados = `
            <div class="flex justify-between items-center">
                <span class="left ${cliente.fechaFin < new Date().toISOString().split("T")[0] ? "text-red-600 relative" : ""}">
                    ${cliente.Pfibra || cliente.Pint ? '<i class="fas fa-wifi"></i>' : ''}
                </span>
                <span>${cliente.Pfijo ? '<i class="fas fa-phone"></i>' : ''}</span>
                <span>
                    ${cliente.PMovil ? '<i class="fas fa-mobile-alt"></i>' : ''}
                    ${cliente.Pcentralita ? '<i class="fas fa-phone-office"></i>' : ''}
                    ${cliente.Ptv ? '<i class="fas fa-tv"></i>' : ''}
                </span>
            </div>
        `;

        const row = `
            <tr data-id="${cliente.id}" class="cursor-pointer hover:bg-gray-100 cliente-row">
                <td class="border px-4 py-2">${cliente.dni}</td>
                <td class="border px-4 py-2 text-left whitespace-nowrap">${cliente.nombre}</td>
                <td class="border px-4 py-2 text-left">${cliente.email || "No disponible"}</td>
                <td class="border px-4 py-2">${cliente.telefonofijo}</td>
                <td class="border px-4 py-2">${cliente.telefonomovil}</td>
                <td class="border px-4 py-2 text-left whitespace-nowrap">${cliente.direccion}, ${cliente.poblacion}, ${cliente.codpostal}</td>
                <td class="border px-4 py-2">${cliente.NFacPendientes || 0}</td>
                <td class="border px-4 py-2">${productosContratados}</td>
                <td class="border px-4 py-2">${cliente.Baja ? "Baja" : "Alta"}</td>
                <td class="border px-4 py-2 whitespace-nowrap">${cliente.fechaFin}</td>
            </tr>
        `;
        clienteTableBody.innerHTML += row;
    });

    // Agrega el evento a cada fila
    document.querySelectorAll('.cliente-row').forEach(row => {
        row.addEventListener('click', function() {
            const clienteId = this.getAttribute('data-id');
            const cliente = clientes.find(c => c.id === parseInt(clienteId));

            if (cliente) {
                // Guarda el cliente en localStorage
                localStorage.setItem('clienteSeleccionado', JSON.stringify(cliente));
                
                // Redirige a la página de detalles del cliente
                window.location.href = `cliente_formulario.html?id=${clienteId}`;
            }
        });
    });
}
