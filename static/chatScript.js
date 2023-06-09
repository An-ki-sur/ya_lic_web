function find(){
text = document.getElementById('text').value



fetch('/funder/' + text).then(response => response.json()).then(
function(data){
document.getElementById("result").innerHTML = data['data'];
})
}
//    text = document.getElementById('text').value
//
 //   fetch('/funder/' + text).then(response => response.json()).then(
 //       function(data)
 //       {
 //           alert(data['res'])
 //       }
 //  }


function scroll(){
document.getElementById('chatscroll').scrollTop = 10000
}

function chatUpdate(start)
{

var c = 0;
var start = start

changeChat(start)



//for(let i = 0; i < a.length; i++)
// {
//    fetch('/updateLikes/' + a[i]).then(response => response.json()).then(
//        function(data)
//        {
//        document.getElementById("like" + a[i]).innerHTML = data["like" + a[i]];
//        document.getElementById("com" + a[i]).innerHTML = data["com" + a[i]];
//        document.getElementById("date" + a[i]).innerHTML = data["date" + a[i]];
//        document.getElementById("rep" + a[i]).innerHTML = data["rep" + a[i]];
//        document.getElementById("looks" + a[i]).innerHTML = data["looks" + a[i]];
//        })}
//
//
const interval = setInterval(function()
{

update()
if (c == 0){
scroll()}
c = 1

}, 500);
}


function update(){

   fetch('/getchat').then(response => response.json()).then(
    function(data)
    {
        document.getElementById("chat").innerHTML = data['data'];
    });

}


function changeChat(id){
var id = id;
var old_id = getCookie('chat')

if(id != old_id){


document.getElementById("chat_" + id).classList.add('u-group-2')
document.getElementById("chat_" + id).classList.remove('u-group-3')


document.getElementById("chat_" + old_id).classList.add('u-group-3')
document.getElementById("chat_" + old_id).classList.remove('u-group-2')
setCookie('chat', id, 7)}
update()
}

function sendMessage(){
message = document.getElementById('message').value




            $.ajax({
                url: '/newMes',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 'value': message }),
                success: function(response) {

                },
                error: function(error) {

                }
            });




update()


 document.getElementById('message').value = ''


}



function getCookie(c_name)
{
   var i,x,y,ARRcookies=document.cookie.split(";");
   for (i=0; i<ARRcookies.length; i++)
   {
      x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
      y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
      x=x.replace(/^\s+|\s+$/g,"");
      if (x==c_name)
      {
        return unescape(y);
      }
   }
}



function setCookie(c_name,value,exdays)
{
   var exdate=new Date();
   exdate.setDate(exdate.getDate() + exdays);
   var c_value=escape(value) + ((exdays==null) ? "" : ("; expires="+exdate.toUTCString()));
   document.cookie=c_name + "=" + c_value;
}