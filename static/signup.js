function submitSignup() {
    document.querySelectorAll('.error-message').forEach(function(e) {
        e.textContent = '';
    });

    const userData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        firstname: document.getElementById('firstname').value,
        middlename: document.getElementById('middlename').value,
        lastname: document.getElementById('lastname').value,
        birthdate: document.getElementById('birthdate').value,
        email: document.getElementById('email').value,
    };

    fetch('/user/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = "/login_page";
        } else if (data.errors) {
            for (const [key, message] of Object.entries(data.errors)) {
                document.getElementById(`${key}-error`).textContent = message;
            }
        }
    });
}