function accept_registration(id, userId) { 
    $.ajax({
        url: '/api/accept_registration',
        type: 'POST',
        data: {
            id: id,
            userId: userId,
        },
        success: function (data) {
            window.location.reload();
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function reject_registration(id, userId) { 
    $.ajax({
        url: '/api/reject_registration',
        type: 'POST',
        data: {
            id: id,
            userId: userId,
        },
        success: function (data) {
            window.location.reload();
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function formatNum(angka) {
    return angka.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function logout() {
    $.removeCookie('token', { path: '/' });
    window.location.href = '/';
}

function showAlert() {
    $('#alertContainer').empty();
    let msg = $.cookie('msg');
    if (msg) {
        let alertHTML = `
            <div class="alert alert-dark alert-dismissible fade show" role="alert">
                ${msg}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        $('#alertContainer').append(alertHTML);
        $.removeCookie('msg', { path: '/' });
    }
}
