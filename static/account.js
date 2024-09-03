function deleteAccount() {
    fetch('/user/delete/', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = "/login_page";
        } else {
            window.location.href = "/login_page";
            showAlert("There is no account logged in.");
        }
    });
}
function logout(){
    fetch('/logout', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = "/login_page";
        } else {
            showAlert("There is no account logged in.")
        }
    });
}

async function showAlert(message) {
    const alertDiv = document.getElementById('alert');
    alertDiv.querySelector('.alert-message').textContent = message;
    alertDiv.style.opacity = "1";
    alertDiv.style.display = "block";

    setTimeout(async function () {
        alertDiv.style.opacity = "0";
        await delay(1000);
        window.location.href = "/login_page";
    }, 4000);

    document.getElementById('closebtn').onclick = function () {
        alertDiv.style.opacity = "0";
        setTimeout(function () {
            window.location.href = "/login_page";
        }, 1000);
    }


}

function showConfirm(action) {
    const confirmDiv = document.getElementById('confirm');
    const confirmMessage = document.getElementById('confirm-message');

    if (action === 'delete') {
        confirmMessage.textContent = "Are you sure you want to delete your account?";
    } else if (action === 'logout') {
        confirmMessage.textContent = "Are you sure you want to logout?";
    }

    confirmDiv.style.display = 'block';

    document.getElementById('confirm-ok-btn').onclick = function() {
        confirmDiv.style.display = 'none';
        if (action === 'delete') {
            deleteAccount();
        } else if (action === 'logout') {
            logout();
        }
    };
    document.getElementById('confirm-cancel-btn').onclick = function() {
        confirmDiv.style.display = 'none';
    };
}
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
function navigateToUpdatePage(userId){
    window.location.href = `/update_page/${userId}`;



}
