document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.content-section');
    const profileLinks = document.querySelectorAll('.profile-link');
    const profileSections = document.querySelectorAll('.profile-info-section');

    // Maneja el cambio de secciones de navegación principal
    links.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = link.id + '-content';

            sections.forEach(section => {
                section.classList.remove('active');
            });

            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });

    // Maneja el cambio de secciones dentro del perfil
    profileLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = link.getAttribute('data-target') + '-info';

            profileSections.forEach(section => {
                section.classList.remove('active');
            });

            // Carga datos desde el servidor
            fetch(`/load_${link.getAttribute('data-target')}_data`)
                .then(response => response.json())
                .then(data => {
                    if (targetId === 'personal-info') {
                        document.getElementById('calle').value = data.calle || '';
                        document.getElementById('nombre').value = data.nombre || '';
                        document.getElementById('celular').value = data.celular || '';
                        document.getElementById('correo').value = data.correo || '';
                    } else if (targetId === 'laboral-info') {
                        document.getElementById('puestoTrabajo').value = data.puestoTrabajo || '';
                        document.getElementById('departamento').value = data.departamento || '';
                        document.getElementById('supervisor').value = data.supervisor || '';
                        document.getElementById('fechaIngreso').value = data.fechaIngreso || '';
                        document.getElementById('horarioTrabajo').value = data.horarioTrabajo || '';
                    }

                    const targetSection = document.getElementById(targetId);
                    if (targetSection) {
                        targetSection.classList.add('active');
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });

    // Maneja el envío del formulario de Información Personal
    document.getElementById('form-infoP').addEventListener('submit', function(event) {
        event.preventDefault();
        submitInfoP();
    });

    // Maneja el envío del formulario de Información Laboral
    document.getElementById('form-infoL').addEventListener('submit', function(event) {
        event.preventDefault();
        submitInfoL();
    });
});

function submitInfoP() {
    const idTrabajador = document.getElementById('profile-id').textContent;
    const calle = document.getElementById('calle').value;
    const nombre = document.getElementById('nombre').value;
    const celular = document.getElementById('celular').value;
    const correo = document.getElementById('correo').value;

    fetch(`/submit_infoP`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idTrabajador, calle, nombre, celular, correo }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('Información Personal Guardada Exitosamente');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un error al guardar la información');
        });
}

function submitInfoL() {
    const idTrabajador = document.getElementById('profile-id').textContent;
    const puestoTrabajo = document.getElementById('puestoTrabajo').value;
    const departamento = document.getElementById('departamento').value;
    const supervisor = document.getElementById('supervisor').value;
    const fechaIngreso = document.getElementById('fechaIngreso').value;
    const horarioTrabajo = document.getElementById('horarioTrabajo').value;

    fetch(`/submit_infoL`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idTrabajador, puestoTrabajo, departamento, supervisor, fechaIngreso, horarioTrabajo }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('Información Laboral Guardada Exitosamente');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un error al guardar la información');
        });
}
document.addEventListener('DOMContentLoaded', function() {
    const accordions = document.querySelectorAll('.accordion-button');

    // Maneja el comportamiento del acordeón
    accordions.forEach(button => {
        button.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.classList.contains('active')) {
                content.classList.remove('active');
            } else {
                document.querySelectorAll('.accordion-content').forEach(el => el.classList.remove('active'));
                content.classList.add('active');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el ID del trabajador desde la sesión o desde algún otro lugar
    const idTrabajador = '{{ session.get("id_trabajador") }}';

    // Función para cargar información laboral
    function loadInfoL() {
        fetch(`/load_laboral_data?idTrabajador=${idTrabajador}`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    document.getElementById('puestoTrabajoo').value = data.puestoTrabajo || '';
                    document.getElementById('deparltamento').value = data.departamento || '';
                    document.getElementById('supervisorr').value = data.supervisor || '';
                    document.getElementById('fechaIngresoo').value = data.fechaIngreso || '';
                    document.getElementById('horarioTrabajoo').value = data.horarioTrabajo || '';
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Función para cargar información personal
    function loadInfoP() {
        fetch(`/load_personal_data?idTrabajador=${idTrabajador}`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    document.getElementById('callee').value = data.calle || '';
                    document.getElementById('nombree').value = data.nombre || '';
                    document.getElementById('cel').value = data.celular || '';
                    document.getElementById('correoE').value = data.correo || '';
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Cargar la información cuando el documento esté listo
    loadInfoL();
    loadInfoP();
});





