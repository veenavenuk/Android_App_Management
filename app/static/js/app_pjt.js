
function showErrors(response) {
    const errors = response.responseJSON.errors;
    let message = '';

    for (const field in errors) {
        message += errors[field][0] + '\n';
    }

    return message;
}

function clearModal() {
    document.querySelector('input[name="app_name"]').value = '';
    document.querySelector('input[name="package_name"]').value = '';
    document.querySelector('input[name="app_version"]').value = '';
    document.querySelector('input[name="category"]').value = '';
    document.querySelector('input[name="contact_email"]').value = '';
    document.querySelector('textarea[name="description"]').value = '';

}

function login_handler(event) {
    event.preventDefault();
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;

    var login_data = {
    }
    login_data['username'] = username;
    login_data['password'] = password;
    
    var res = jQuery.ajax
        ({
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json',
            },
            type: "post",
            url: LOGIN_URL,
            dataType: "json",
            data: JSON.stringify(login_data),

            success: renderlist,

            error: function(response) {
                const errors = response.responseJSON;
                let message = '';
            
                for (const field in errors) {
                    message += errors[field][0] + '\n';
                }
                alert(message);
            }
        });

        function setCookie(name, value, days = 7) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));  
            const expires = `expires=${date.toUTCString()}`;
            
            document.cookie = `${name}=${value}; ${expires}; path=/; Secure; SameSite=Strict`;
            console.log(`Cookie set: ${name}=${value}`);
        }
        

        function renderlist(response) {
            alert(response.message);
            const baseUrl = window.location.origin; 
            // window.location.href = baseUrl + response.dashboard_url;
            const redirectUrl = baseUrl + response.dashboard_url + '?token=' + encodeURIComponent(response.token);
            window.location.href = redirectUrl;

            setCookie('auth_token', response.token);
        }
    
}

function signup(event) {
    event.preventDefault();
    const first_name = document.querySelector('input[name="first_name"]').value;
    const surname = document.querySelector('input[name="surname"]').value;
    const email = document.querySelector('input[name="email"]').value;
    const usrname = document.querySelector('input[name="username_data"]').value;
    const contact_number = document.querySelector('input[name="contact_number"]').value;
    const passwrd = document.querySelector('input[name="password_data"]').value;
    const confirm_password = document.querySelector('input[name="confirm_password"]').value;

    var signup_data = {
    }
    signup_data['first_name'] = first_name;
    signup_data['last_name'] = surname;
    signup_data['email'] = email;
    signup_data['username'] = usrname;
    signup_data['contact_number'] = contact_number;
    signup_data['password'] = passwrd;
    console.log(signup_data)
    var res = jQuery.ajax
        ({
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json',
            },
            type: "post",
            url: SIGNUP_URL,
            dataType: "json",
            data: JSON.stringify(signup_data),

            success: renderlist,

            error: function(response) {
                const errors = response.responseJSON;
                let message = '';
            
                for (const field in errors) {
                    message += errors[field][0] + '\n';
                }
                alert(message);
            }
        });

        function renderlist(response) {
            alert(response.message);
            const baseUrl = window.location.origin; 
            window.location.href = baseUrl;

        }
    
}


function addApp(event) {
    event.preventDefault();

    const appName = document.querySelector('input[name="app_name"]').value;
    const packageName = document.querySelector('input[name="package_name"]').value;
    const appVersion = document.querySelector('input[name="app_version"]').value;
    const category = document.querySelector('input[name="category"]').value;
    const contactEmail = document.querySelector('input[name="contact_email"]').value;
    const description = document.querySelector('textarea[name="description"]').value;

    var data = {
    }
    data['app_name'] = appName;
    data['package_name'] = packageName;
    data['app_version'] = appVersion;
    data['category'] = category;
    data['contact_email'] = contactEmail;
    data['description'] = description;

    var res = jQuery.ajax
        ({
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json',
            },
            type: "post",
            url: ADD_APP_URL,
            dataType: "json",
            data: JSON.stringify(data),

            success: renderlist,

            error: function(response) {
                let msg = showErrors(response);
                alert(msg);
            }
        });

        function renderlist(response) {
            alert(response.message);
            const baseUrl = window.location.origin; 
            window.location.href = baseUrl + "/add-app";
        }
    
}

$(document).ready(function () {

    // $(document).on('click', '#add-app-link', function (event) {
    //     event.preventDefault();
        const token = getCookie('auth_token');  
        
        if (!token) {
            console.log("No token found!");
            return; 
        }

        $.ajax({
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}` 
            },
            type: 'GET',
            url: APP_LIST,
            success: renderList,
            error: function (response) {
                alert("Oops! Something Went Wrong!")
            }
        });

        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null; 
        }
    

        function renderList(response) {
            const dataList = response.data;

            for (let i = 0; i < dataList.length; i++) {
                $('#admin-app-list').append(
                    '<tr id="' + dataList[i].id + '">' +
                    '<td class="text-center">' + (i + 1) + '</td>' +
                    '<td class="text-center">' + dataList[i].app_name + '</td>' +
                    '<td class="text-center">' + dataList[i].app_version + '</td>' +
                    '<td class="text-center">' + dataList[i].category + '</td>' +
                    '<td class="text-center">' + dataList[i].package_name + '</td>' +
                    '<td class="text-center">' + dataList[i].contact_email + '</td>' +
                    '<td class="text-center">' + dataList[i].description + '</td>' +
                    '</tr>'
                );
            }
            // const baseUrl = window.location.origin; 
            // window.location.href = baseUrl + "/add-app";

        }
    // });


});

function taskSubmit(event) {
    event.preventDefault();

    var selectedAppId = document.getElementById('taskOption').value;
    const token = getCookie('auth_token');  


    if (!selectedAppId) {
        alert("Please select an App first.");
        return;
    }

    var data = {
    }
    data['app_id'] = selectedAppId;

    var res = jQuery.ajax
        ({
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
            },
            type: "post",
            url: TASK_SUBMIT,
            dataType: "json",
            data: JSON.stringify(data),

            success: renderlist,

            error: function(response) {
                // let msg = showErrors(response);
                alert("Oops!Something went wrong!");
            }
        });

        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null; 
        }
        function renderlist(response) {
            alert("Sucessfully Added!")
            // alert(response.message);
            const baseUrl = window.location.origin; 
            const token = getCookie('auth_token');
            const redirectUrl = baseUrl + "/user-view" + '?token=' + encodeURIComponent(token);
            window.location.href = redirectUrl;
        }
    
}



