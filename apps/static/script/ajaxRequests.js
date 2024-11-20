function postRequest(url, data, callback) {
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        dataType: 'json',
        contentType: 'application/json',
        timeout: 0,
        success: function (response) {
            callback(response.data);
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
        }
    });
}

function getRequest(url, callback) {
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            console.log(response);
            callback(response.data);
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
        }
    });
}