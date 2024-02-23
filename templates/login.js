function redirectToIntro() {
    window.location.href = '/intro';
}

$(document).ready(function() {
    $('#loginBtn').click(function() {
        var username = $('#username').val();
        var password = $('#password').val();
        
        $.ajax({
            type: 'POST',
            url: '/login',
            data: {
                username: username,
                password: password
            },
            success: function(response) {
                // Assuming server returns jwt_token in response
                var jwtToken = response.jwt_token;
                // Store the token in localStorage for subsequent requests
                localStorage.setItem('jwt_token', jwtToken);
                // Redirect to the intro page
                redirectToIntro();
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
                alert("Login failed. Please try again.");
            }
        });
    });
});