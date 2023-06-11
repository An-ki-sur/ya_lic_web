function checkReg(){
name = document.getElementById("name").value
login = document.getElementById("log").value
pass = document.getElementById("pass").value
pass1 = document.getElementById("pass1").value

if (name == ""){
document.getElementById("error").innerHTML = "Введите имя"
return
}
if (login == ""){
document.getElementById("error").innerHTML = "Введите логин"
return
}
if (pass == ""){
document.getElementById("error").innerHTML = "Введите пароль"
return
}
if (pass != pass1){
document.getElementById("error").innerHTML = "Пароли не совпадают"
return
}
if (pass.length < 8){
document.getElementById("error").innerHTML = "Пароль слишком короткий"
return
}

            $.ajax({
                url: '/regCheck',
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