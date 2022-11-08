$(document).ready(function()
{

buttonState();
//Password re-enter 
$("#pwdagain").keyup(function()
{
if(confirmpassword())
{
	 $("#pwdagain").css("border","4px solid green");
	 $("#pwdvalid2").html("<p class='text-success'>Password matching</p>");

}
else
{
	$("#pwdagain").css("border","4px solid red");
	$("#pwdvalid2").html("<p class='text-danger'>Incorrect Password Matching</p>");
	$("#regbtn").hide();
}
//responsiveness on key press
if(pwdvalid())
{
	 $("#pwd").css("border","4px solid green");
	 $("#pwdvalid").html("<p class='text-success'>VALID</p>");
	 
}
else
{
	$("#pwd").css("border","4px solid red");
	$("#pwdvalid").html("<p class='text-danger'>Incorrect Password</p>");
	$("#regbtn").hide();
}
buttonState();
});
//firstname
$("#regbtn").hide();
$("#fname").keyup(function()
{
if(fnamevalid())
{
	 $("#fname").css("border","4px solid green");
	 $("#fnamevalid").html("<p class='text-success'>VALID</p>");

}
else
{
	$("#fname").css("border","4px solid red");
	$("#fnamevalid").html("<p class='text-danger'>Incorrect First Name</p>");
	$("#regbtn").hide();
}
buttonState();
});
//regno
$("#reg").keyup(function()
{
if(regvalid())
{
	 $("#reg").css("border","4px solid green");
	 $("#regvalid").html("<p class='text-success'>VALID</p>");

}
else
{
	$("#reg").css("border","4px solid red");
	$("#regvalid").html("<p class='text-danger'>Incorrect First Name</p>");
	$("#regbtn").hide();
}
buttonState();
});
//lastname
$("#lname").keyup(function()
{
if(lnamevalid())
{
	 $("#lname").css("border","4px solid green");
	 $("#lnamevalid").html("<p class='text-success'>VALID</p>");

}
else
{
	$("#lname").css("border","4px solid red");
	$("#lnamevalid").html("<p class='text-danger'>INCORRECT LAST NAME</p>");
	$("#regbtn").hide();

}
buttonState();
});
//email
$("#email").keyup(function()
{
if(emailvalid())
{
	 $("#email").css("border","4px solid green");
	 $("#emailvalid").html("<p class='text-success'>VALID</p>");
	
}
else
{
	$("#email").css("border","4px solid red");
	$("#emailvalid").html("<p class='text-danger'>Incorrect Email id</p>");
	$("#regbtn").hide();
}
buttonState();
});
//password
$("#pwd").keyup(function()
{
if(pwdvalid())
{
	 $("#pwd").css("border","4px solid green");
	 $("#pwdvalid").html("<p class='text-success'>VALID</p>");
	 
}

else
{
	$("#pwd").css("border","4px solid red");
	$("#pwdvalid").html("<p class='text-danger'>Incorrect Password </p>");
	$("#regbtn").hide();
}if(confirmpassword())
{
	 $("#pwdagain").css("border","4px solid green");
	 $("#pwdvalid2").html("<p class='text-success'>Password matching </p>");

}
else
{
	$("#pwdagain").css("border","4px solid red");
	$("#pwdvalid2").html("<p class='text-danger'>INCORRECT Password</p>");
	$("#regbtn").hide();
}
buttonState();
});

buttonState();
});
//button state 
function buttonState()
{ $("#regbtn").hide();

	if (pwdvalid && fnamevalid() && lnamevalid() &&emailvalid() && regvalid()) {
		$("#regbtn").show();
	}
	else
	{
		$("#regbtn").hide();
	}
}

//+/s+[a-zA-Z]{5,20}
//password function 
function pwdvalid()
{
	var password=$("#pwd").val();
	var reg=/^(?=.*\d.*)(?=.*[a-zA-Z].*)(?=.*[!#\$@!%&.\?_].*).{8,}$/;
	
	if(reg.test(password)){
             return true;
         }
	else{
             return false;
         }
}

//reenter password function
function pwd2valid()
{
	var password2=$("#pwd").val();
	
	if(reg.test(password2)){
             return password2;
         }
	else{
             return false;
         }
}
//firstname function
function fnamevalid()
{
	var fname=$("#fname").val();
	var reg=/^([A-Za-z]{1,30}[ ]{1}|[A-Za-z]{1,30})*$/;
	
	if(reg.test(fname)){
             return true;
         }
	else{
             return false;
         }
}
//email id function 
function emailvalid()
{
	var email=$("#email").val();
	var reg=/^[a-zA-Z]{3,20}[.][a-zA-Z]{1,20}[@]((((christuniversity)|(Christuniversity))[.]((in)|(com)))|([a-zA-Z]{2,8}[.])((christuniversity)|(Christuniversity))[.]((in)|(com)))$/;
	
	if(reg.test(email)){
             return true;
         }
	else{
             return false;
         }
}
//lastname fuction
function lnamevalid()
{
	var lname=$("#lname").val();
	var reg=/^([A-Za-z]{1,30}[ ]{1}|[A-Za-z]{1,30})*$/;
	
	if(reg.test(lname)){
             return true;
         }
	else{
             return false;
         }
}
//regno  invalid function
function regvalid()
{
	var register=$("#reg").val();
	var reg=/^[1-9]{1}[0-9]{6}$/;
	
	if(reg.test(register)){
             return true;
         }
	else{
             return false;
         }
}
//password confirm fuction
function confirmpassword()
{
	var n = $("#pwd").val();
	 var m = $("#pwdagain").val();
 
	if(n===m)
	{
		return true;
	}
	else 
	{
		return false;
	}
	 
}