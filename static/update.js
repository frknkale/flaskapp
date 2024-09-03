function submitUpdate() {
            const updateData = {
                username: document.getElementById('username').value,
                firstname: document.getElementById('firstname').value,
                middlename: document.getElementById('middlename').value,
                lastname: document.getElementById('lastname').value,
                birthdate: document.getElementById('birthdate').value,
                email: document.getElementById('email').value,
                new_password: document.getElementById('new_password').value,
                confirm_password: document.getElementById('confirm_password').value,
                password: document.getElementById('password').value,
            };

            fetch('/user/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = "/account_page";
                } else if (data.errors) {
                    for (const [key, message] of Object.entries(data.errors)) {
                        document.getElementById(`${key}-error`).textContent = message;
                    }
                }
            });
        }