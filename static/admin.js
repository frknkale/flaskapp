function loadUsers() {
    // document.getElementById('logs-container').classList.add('hidden');
    fetch('/user/list')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('user-table-body');
            tbody.innerHTML = '';
            data.user_list.forEach(user => {
                const row = `<tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.firstname}</td>
                    <td>${user.middlename}</td>
                    <td>${user.lastname}</td>
                    <td>${user.email}</td>
                    <td>${user.birthdate}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        });
}

function loadOnlineUsers() {
    // document.getElementById('logs-container').classList.add('hidden');
    fetch('/onlineusers')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('online-user-table-body');
            tbody.innerHTML = '';
            data.online_user_list.forEach(user => {
                const row = `<tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.ipaddress}</td>
                    <td>${user.logindatetime}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        });
}

function getLogs() {
    // document.getElementById('user-list').classList.add('hidden');
    // document.getElementById('online-users').classList.add('hidden');
    fetch('/show_logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs-container');
            logsContainer.innerHTML = '';
            data.logs.forEach(log => {
                const logEntry = document.createElement('p');
                logEntry.textContent = log;
                logsContainer.appendChild(logEntry);
            });
        });
}

function logout() {
    fetch('/logout', { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/login_page';
            }
        });
}


window.onload = function() {
    loadUsers();
    loadOnlineUsers();
};

function toggleView(view) {
    document.getElementById('user-list').classList.add('hidden');
    document.getElementById('online-users').classList.add('hidden');
    document.getElementById('logs-container').classList.add('hidden');
    document.getElementById(view).classList.remove('hidden');
}
