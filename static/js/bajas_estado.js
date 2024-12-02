function verLineasMoviles(buttonElement) {
    const lineasJson = buttonElement.dataset.lineas;
    if (!lineasJson || lineasJson.trim() === "") {
        Swal.fire('Error', 'No se encontraron líneas móviles', 'error');
        return;
    }
    try {
        const lineas = JSON.parse(lineasJson);
        let htmlContent = "<ul>";
        lineas.forEach(linea => {
            htmlContent += `<li><strong>- DDI:</strong> ${linea.DDI}, <strong>ID:</strong> ${linea.ID}</li>`;
        });
        htmlContent += "</ul>";
        Swal.fire({ title: 'Líneas Móviles', html: htmlContent, confirmButtonText: 'Cerrar' });
    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'Error al procesar las líneas móviles', 'error');
    }
}

function verServiciosAdicionales(buttonElement) {
    const serviciosJson = buttonElement.dataset.servicios;
    if (!serviciosJson || serviciosJson.trim() === "") {
        Swal.fire('Error', 'No se encontraron servicios adicionales', 'error');
        return;
    }
    try {
        const servicios = JSON.parse(serviciosJson);
        let htmlContent = "<ul>";
        servicios.forEach(servicio => {
            htmlContent += `<li><strong>- ID:</strong> ${servicio.ID}, <strong>Descripción:</strong> ${servicio.Descripcion}, <strong>Referencia:</strong> ${servicio.Referencia}</li>`;
        });
        htmlContent += "</ul>";
        Swal.fire({ title: 'Servicios Adicionales', html: htmlContent, confirmButtonText: 'Cerrar' });
    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'Error al procesar los servicios adicionales', 'error');
    }
}


    function mostrarAlerta(event) {
        event.preventDefault(); // Prevenir el comportamiento predeterminado del formulario
        const form = event.target; // Referencia al formulario

        // Opcional: puedes enviar el formulario con JavaScript
        fetch(form.action, {
            method: form.method,
            body: new FormData(form),
        })
            .then((response) => {
                if (response.ok) {
                    // Mostrar alerta al usuario
                    Swal.fire({
                        title: 'Estado actualizado',
                        text: 'El estado ha sido cambiado correctamente.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar',
                    });
                } else {
                    // Mostrar error en caso de que la petición falle
                    Swal.fire({
                        title: 'Error',
                        text: 'Hubo un problema al actualizar el estado.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar',
                    });
                }
            })
            .catch((error) => {
                console.error('Error al enviar el formulario:', error);
                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrió un error inesperado.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar',
                });
            });
    }

    document.getElementById('filtroEstado').addEventListener('change', function () {
        const estadoSeleccionado = this.value;
        const filas = document.querySelectorAll('#tablaBajas tbody tr');
    
        filas.forEach(fila => {
            const estado = fila.getAttribute('data-estado');
            if (estadoSeleccionado === 'todos' || estado === estadoSeleccionado) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    });
    

    document.getElementById('filtroFecha').addEventListener('change', function () {
        const fechaSeleccionada = this.value;
    
        if (!fechaSeleccionada) {
            Swal.fire('Error', 'Por favor selecciona una fecha', 'warning');
            return;
        }
    
        const filas = document.querySelectorAll('#tablaBajas tbody tr');
    
        filas.forEach(fila => {
            const fechaBaja = fila.querySelector('td:nth-child(7)').textContent.trim();
            const [dia, mes, anio] = fechaBaja.split('-'); // Asume formato DD-MM-YYYY
            const fechaBajaFormateada = `${anio}-${mes}-${dia}`;
    
            if (fechaBajaFormateada === fechaSeleccionada) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    });
    
