function loginCheck(){


login = document.getElementById("log").value
pass = document.getElementById("pass").value
            $.ajax({
                url: '/loginCheck',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 'login':  login, "pass": pass}),
                success: function(response) {

                if (response == 'sumbit'){

                document.getElementById("form").submit()

                }
                else{
                document.getElementById("error").innerHTML = response

                }
                },
                error: function(error) {

                }
            });

}