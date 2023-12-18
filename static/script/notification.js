function getNotifications() {
    notifications = [];
    $.ajax({
        url: '/api/get_notifications',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log(data);
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function updateNotification(notification_id) {
    $.ajax({
        url: '/api/update_status_notification',
        type: 'POST',
        data: { notification_id: notification_id },
        success: function (data) {
            console.log(data);
        },
        error: function (error) {
            console.log(error);
        }
    });
    getNotifications()
}

function clearNotifications() {
    $.ajax({
        url: '/api/delete_notifications',
        type: 'POST',
        data: {},
        success: function (data) {
            console.log(data);
        },
        error: function (error) {
            console.log(error);
        }
    });
    getNotifications()
}