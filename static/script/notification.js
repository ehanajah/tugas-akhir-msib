let notifications = [];

function getNotifications() {
    let notificationsContainer = $('#notification-drop-down');
    let notificationBadge = $('#notification-badge');
    let clearDivider = $('#clearDivider');
    let clearBtn = $('#clearBtn');
    $.ajax({
        url: '/api/get_notifications',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let newNotifications = data["notifications"];
            if (JSON.stringify(newNotifications) !== JSON.stringify(notifications)) {
                notificationsContainer.empty();
                if (newNotifications.length === 0) {
                    noNotifHTML = `
                        <div class="media my-5 mx-3">
                            <p class="text-sm text-truncate text-secondary" style="opacity: 80%;">Tidak ada notifikasi</p>
                        </div>
                    `;
                    clearDivider.hide();
                    clearBtn.hide();
                    notificationBadge.hide();
                    notificationsContainer.append(noNotifHTML);
                } else {
                    notifications = newNotifications;
                    console.log(notifications);
                    let unreadCount = 0;
                    for (const index in notifications) {
                        let notification = notifications[index];
                        if (!notification["isRead"]) {
                            unreadCount++;
                            let notifHTML = `
                                <a class="dropdown-item" style="cursor: pointer;" data-bs-toggle="modal"
                                    data-bs-target="#notifModal" data-id="${notification["_id"]}" data-message="${notification["message"]}">
                                    <div class="media">
                                        <p class="text-sm text-truncate"><b>${notification["message"]}</b></p>
                                    </div>
                                </a>
                            `;
                            clearDivider.show();
                            clearBtn.show();
                            notificationsContainer.append(notifHTML);
                        } else {
                            let notifHTML = `
                                <a class="dropdown-item" style="cursor: pointer;" data-bs-toggle="modal"
                                    data-bs-target="#notifModal" data-id="${notification["_id"]}" data-message="${notification["message"]}">
                                    <div class="media">
                                        <p class="text-sm text-truncate">${notification["message"]}</p>
                                    </div>
                                </a>
                            `;
                            clearDivider.show();
                            clearBtn.show();
                            notificationsContainer.append(notifHTML);
                        }
                    }
                    if (unreadCount > 0) {
                        notificationBadge.show();
                    } else {
                        notificationBadge.hide();
                    }
                }
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}


$(document).ready(function() {
    let notificationBadge = $('#notification-badge');
    let clearDivider = $('#clearDivider');
    let clearBtn = $('#clearBtn');

    notificationBadge.hide();
    clearDivider.hide();
    clearBtn.hide();
    getNotifications();
    setInterval(getNotifications, 3000);
});


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

$('#notifModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget);
    let message = button.data('message');
    let id = button.data('id');
    let modal = $(this);
    modal.find('.modal-body').text(message);
    updateNotification(id);
})