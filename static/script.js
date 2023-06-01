function refreshPage(){
    window.location.reload();
}


function showAlert(post_list)
{
var a = post_list;

for(let i = 0; i < a.length; i++)
 {
    fetch('/updateLikes/' + a[i]).then(response => response.json()).then(
        function(data)
        {
        document.getElementById("like" + a[i]).innerHTML = data["like" + a[i]];
        document.getElementById("com" + a[i]).innerHTML = data["com" + a[i]];
        document.getElementById("date" + a[i]).innerHTML = data["date" + a[i]];
        document.getElementById("rep" + a[i]).innerHTML = data["rep" + a[i]];
        document.getElementById("looks" + a[i]).innerHTML = data["looks" + a[i]];
        })}


const interval = setInterval(function()
{

for(let i = 0; i < a.length; i++)
 {

   fetch('/updateLikes/' + a[i]).then(response => response.json()).then(
    function(data)
    {
        document.getElementById("like" + a[i]).innerHTML = data["like" + a[i]];
        document.getElementById("com" + a[i]).innerHTML = data["com" + a[i]];
        document.getElementById("date" + a[i]).innerHTML = data["date" + a[i]];
        document.getElementById("rep" + a[i]).innerHTML = data["rep" + a[i]];
        document.getElementById("looks" + a[i]).innerHTML = data["looks" + a[i]];
    });
 }
}, 5000);
}


function liked(post){
    var a = post;
    fetch('/addLike/' + a)
    .then(response => response.json())
    .then(json => {
        document.getElementById("likepic" + a).src = '/static/images/' + json['img']
           fetch('/updateLikes/' + a).then(response => response.json()).then(
    function(data)
    {
        document.getElementById("like" + a).innerHTML = data["like" + a];
        document.getElementById("com" + a).innerHTML = data["com" + a];
        document.getElementById("date" + a).innerHTML = data["date" + a];
        document.getElementById("rep" + a).innerHTML = data["rep" + a];
        document.getElementById("looks" + a).innerHTML = data["looks" + a];
    })



    })
}

function redirect(link){
window.location.replace("/main");
let form = document.getElementById('form')
form.submit()
}



function pass(){
pass1 = document.getElementById('pas1').value
pass2 = document.getElementById('pas2').value
name = document.getElementById('name').value
ava = document.getElementById('ava').value
let form = document.getElementById('form')




if(pass1.length == 0 && pass2.length == 0){
    if (name.length != 0){
        if (ava.length != 0){
            form.submit();
            }
        else{
            form.submit();
            }


    }
    else{
        document.getElementById("error").innerHTML = "Введите имя!";
        }
}
else if(pass1 != pass2){
    document.getElementById("error").innerHTML = "Пароли не совпадают!";
}

else{
if(pass1.length < 8){
document.getElementById("error").innerHTML = "Пароль слишком короткий";
}
else{
    if (name.length != 0){
        if (ava.length != 0){
            form.submit();
        }
        else{
            form.submit();
        }
    }
    else{
document.getElementById("error").innerHTML = "Введите имя!";
}}

}


}