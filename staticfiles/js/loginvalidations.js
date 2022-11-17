console.log("inside js vaidation")

$(document).ready(function()
{
console.log("hello");
buttonState();

//regno
$("#id_password").keyup(function()
{
if(pwdvalid())
{
	 $("#id_password").css("border","4px solid green");
	 $("#loginpassvalid").html("<p class='text-success'>VALID</p>");

}
else
{
	$("#id_password").css("border","3px solid red");
	$("#loginpassvalid").html("<p class='text-danger' >Incorrect password</p>");
	$("#login").hide();
}
buttonState();
});


//regno
$("#id_username").keyup(function()
{
if(emailvalid())
{
	 $("#id_username").css("border","4px solid green");
	 $("#loginemailvalid").html("<p class='text-success'>VALID</p>");

}
else
{
	$("#id_username").css("border","3px solid red");
	$("#loginemailvalid").html("<p class='text-danger'>Incorrect email</p>");
	$("#login").hide();
}
buttonState();
});


buttonState();
});
//button state 
function buttonState()
{ $("#login").hide();

	if (pwdvalid() && emailvalid()) {
		$("#login").show();
	}
	else
	{
		$("#login").hide();
	}
}

//+/s+[a-zA-Z]{5,20}
//password function 
function pwdvalid()
{
	var password=$("#id_password").val();
	var reg=/^(?=.*\d.*)(?=.*[a-zA-Z].*)(?=.*[!#\$@!%&.\?_].*).{8,}$/;
	
	if(reg.test(password)){
             return true;
         }
	else{
             return false;
         }
}

//email id function 
function emailvalid()
{
	var email=$("#id_username").val();
	var reg=/^[a-zA-Z]{3,20}[.][a-zA-Z]{1,20}[@]((((christuniversity)|(Christuniversity))[.]((in)|(com)))|([a-zA-Z]{2,8}[.])((christuniversity)|(Christuniversity))[.]((in)|(com)))$/;
	
	if(reg.test(email)){
             return true;
         }
	else{
             return false;
         }
}
