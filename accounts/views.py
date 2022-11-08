from turtle import update
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse

# password resetting
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

# from .forms import UserAddForm, VolunteerAddForm, UserEditForm, VolunteerEditForm
from .models import rolestbl,campustbl,depttbl,coursetbl,User,stuhead_vol_profiletbl
from .models import onetoonetickettbl, peergrouptickettbl,sessiontbl
from .forms import *

from .decorators import  superadmin_only, studenthead_only, volunteer_only, mentor_only
from accounts.decorators import unauthenticated_user

from django.urls import reverse
from django.utils.encoding import uri_to_iri
import urllib
import random, string
import datetime
from django.utils import timezone

# sending html template email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.html import strip_tags


def send_24_hr_delay_email():

    today = datetime.datetime.now()
    tempoto = onetoonetickettbl.objects.filter(Q(ticket_status="requested")|Q(ticket_status="assigned"))
    tempgroup = peergrouptickettbl.objects.filter(Q(ticket_status="requested")|Q(ticket_status="assigned"))
    otocount = groupcount = 0;
 
    for each in tempoto:
        result = datetime.datetime.now().astimezone() - each.request_datetime

        # if (result.seconds)>40:
        if(result.days>=1):
            otocount+=1
        

    for each in tempgroup:
        result = datetime.datetime.now().astimezone() - each.request_datetime
        if(result.days>=1):
            groupcount+=1

    if otocount>0 or groupcount>0:
        subject = 'CAPS sessions'
        msg = 'Hello, There is %d unhandled one to one session requests and %d unhandled Group session requests, which is more than 24 hours'
        email_from = settings.EMAIL_HOST_USER
        mentorset = User.objects.filter(roles__roles="mentor")
        mentorlist = []

        for each in mentorset:
            mentorlist.append(str(each.email))

        message2 = (subject, msg, email_from, mentorlist)
        send_mass_mail((message2,), fail_silently=True)

        print("mails sent")
    print("this function runs every 60 seconds")

# ================================== Basic views ========================== #
# 1 ---------------------Unauthorized view
def unauthorized_func(request):
    return HttpResponse("Bad gateway no access!")

# 2 --------------------- index page
# shudnt allow logged user to acces this page
def index_func(request):
    # update_something()
    return render(request, 'accounts/index.html',)

# 3 -------------------- Login function
# shudnt allow logged user to acces this page
# @unauthenticated_user
# def loginfunc(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, f"You are now logged in as {username}.")

#                 if user.is_superuser:
#                     return redirect("sa_dashboard_url")
#                 elif user.roles == rolestbl.objects.filter(roles='studenthead').first():
#                     return redirect("sh_dashboard_url")
#                 return redirect("home_url")
#             else:
#                 messages.error(request,"Invalid username or password.")
#         else:
#             messages.error(request,"Invalid username or password.")
#     form = AuthenticationForm()
#     return render(request=request, template_name="accounts/login.html", context={"form":form})

def loginfunc(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                 #redirecting based on roles
                temproles=rolestbl.objects.all()

                if not temproles.exists():
                    messages.error(request,"No roles contact admin")
                    return redirect("index_url")
                login(request, user)

                messages.success(request, f"You are now logged in as {username}.")

                if user.is_superuser:
                    return redirect("sa_dashboard_url")
                if user.roles.roles == 'mentor':
                    return redirect("mentor_dashboard_url")
                elif user.roles.roles == 'studenthead':
                    return redirect("sh_dashboard_url")
                elif user.roles.roles == 'volunteer':
                    return redirect ("vol_dashboard_url")
                else :
                    messages.error(request,"No roles contact admin")
                    return redirect("index_url")

            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render (request,"accounts/login.html", context={'form':form})

# 4 --------------------------Logout function
def logoutfunc(request):
    logout(request)
    return redirect("login_url")

# 5 -------------------------- password reset view
@unauthenticated_user
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "accounts/pwd_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
                    
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, settings.EMAIL_HOST_USER , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="accounts/pwd_reset.html", context={"password_reset_form":password_reset_form})




# ======================================  oto and group booking views ==============================#


# --------------------- oto student feedback submission view 
# def oto_s_feedback_func(request,uidb64):
def oto_s_feedback_func(request,pkid):
    # otoid = urlsafe_base64_decode(uidb64).decode()
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()
    form = OtoFeedbackForm(instance = tempoto)

    if request.method == "POST":
        form = OtoFeedbackForm(request.POST)
        if form.is_valid():
            # tempfeedback = form.save()
            tempfeedback = form.cleaned_data['s_feedback']
            tempoto.s_feedback = tempfeedback
            tempoto.save(update_fields=['s_feedback'])
            messages.success(request,"Your feedback has been successfully submitted! Thankyou.")
            return redirect("index_url")
    
    context = {"form":form, "tempoto":tempoto}
    return render(request,"accounts/feedback_s_oto.html", context)

# ------------------- groupsession feedback by faculty view
# def grp_s_feedback_func(request,uidb64):
def grp_s_feedback_func(request,pkid):
    # grpid = urlsafe_base64_decode(uidb64).decode()
    tempgrp = peergrouptickettbl.objects.filter(id=pkid).first()
    form = GroupFeedbackForm(instance = tempgrp)

    if request.method == "POST":
        form = GroupFeedbackForm(request.POST)
        if form.is_valid():
            # tempfeedback = form.save()
            tempfeedback = form.cleaned_data['s_feedback']
            tempgrp.s_feedback = tempfeedback
            tempgrp.save(update_fields=['s_feedback'])
            messages.success(request,"Your feedback has been successfully submitted! Thankyou.")
            return redirect("index_url")
    
    context = {"form":form, "tempgrp":tempgrp}
    return render(request,"accounts/feedback_s_grp.html", context)


#  -------------------- OTP generation --------------------
def generate_OTP():
    otp = random.randint(100000,999999)
    return otp

# --------------------- OTP form --------------------------
def feedback_otp_func(request,pkid):
    form = OtpForm
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()

    if request.method == "POST":
        form = OtpForm(request.POST)
        if form.is_valid():
            tempotp = form.cleaned_data['otp']
            print(tempotp)
            print(tempoto.feedback_otp)
            if tempoto.feedback_otp == tempotp:
                temppkid = urlsafe_base64_encode(force_bytes(tempoto.pk))
                
                return redirect("oto_s_feedback_url",temppkid)
            else:
                messages.error(request,"Entered OTP is invalid!")
                
    context = {"form":form}
    return render(request, "accounts/feedback_otp.html", context)

# ---------------------group OTP form --------------------------
def feedback_otp_grp_func(request,pkid):
    form = OtpForm
    tempoto = peergrouptickettbl.objects.filter(id=pkid).first()

    if request.method == "POST":
        form = OtpForm(request.POST)
        if form.is_valid():
            tempotp = form.cleaned_data['otp']
            print(tempotp)
            print(tempoto.feedback_otp)
            if tempoto.feedback_otp == tempotp:
                temppkid = urlsafe_base64_encode(force_bytes(tempoto.pk))
                
                return redirect("grp_s_feedback_url",temppkid)
            else:
                messages.error(request,"Entered OTP is invalid!")
                
    context = {"form":form}
    return render(request, "accounts/feedback_otp.html", context)


# --------------------- OTO student feedback verification form view
def feedback_verification_func(request):
    form = VerificationForm

    if request.method == "POST":
        form = VerificationForm(request.POST)
        
        if form.is_valid():
            tempticket = form.cleaned_data['ticket_no']
            tempemail = form.cleaned_data['email_id']
            tempwing = form.cleaned_data['session_type']
            print(tempwing)
            if tempwing == "One-to-One":
                tempoto = onetoonetickettbl.objects.filter(ticket_no = tempticket, stuemail = tempemail).first()

                if tempoto:
                    otp = generate_OTP()
                    print(otp)
                    tempoto.feedback_otp = otp
                    tempoto.save()
                    # send mail with OTP
                    subject = "CAPS feedback form OTP"
                    message = "This is your OTP - "+str(otp)
                    email_from = settings.EMAIL_HOST_USER

                    send_mail(subject, message, email_from, [tempoto.stuemail],fail_silently=True)
                    messages.success(request,"OTP has been sent to your mail. Please Enter the correct OTP!")
                    return redirect("feedback_otp_url",tempoto.id)
                    # return redirect OTP form
                else:
                    print("wrong")
                    messages.error(request,"Invalid Credentials! Please check the ticket number or the email id!")
                    return redirect("feedback_verification_url")
            else:
                tempgrp = peergrouptickettbl.objects.filter(ticket_no = tempticket, facultyemail = tempemail).first()
                if tempgrp:
                    otp = generate_OTP()
                    print(otp)
                    tempgrp.feedback_otp = otp
                    tempgrp.save()
                    # send mail with OTP
                    subject = "CAPS feedback form OTP"
                    message = "This is your OTP - "+str(otp)
                    email_from = settings.EMAIL_HOST_USER

                    send_mail(subject, message, email_from, [tempgrp.facultyemail],fail_silently=True)
                    messages.success(request,"OTP has been sent to your mail. Please Enter the correct OTP!")
                    return redirect("feedback_otp_grp_url",tempgrp.id)
                    # return redirect OTP form
                else:
                    print("wrong")
                    messages.error(request,"Invalid Credentials! Please check the ticket number or the email id!")
                    return redirect("feedback_verification_url")

            
            

    context = {"form":form}
    return render(request, 'accounts/feedback_request.html', context)





def oto_feedback_func(request,pk):
    form =  OtoFeedbackForm
    if request.method == 'POST':
        pass

    context = {'form':form}
    return render(request, 'onetoone/otofeedback.html', context)

#------------- Generate ticket number
def generate_unique_ticketno():
    tick = random.randint(100000,999999)
    ticket = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return ticket


#------------ One to one booking form
def oto_booking_func(request):
    form = OtoBookingForm

    if request.method == 'POST':
        form = OtoBookingForm(request.POST)
        if form.is_valid():
            tempsession = form.cleaned_data['session']
            tempother = form.cleaned_data['other']
            tempdesc = form.cleaned_data['other_desc']
            tempemail = form.cleaned_data['stuemail']

            if onetoonetickettbl.objects.filter(stuemail=tempemail, session = tempsession,ticket_status = "requested").exists():
                messages.error(request,"You have already submitted a request for "+str(tempsession))
                context = {'form':form}
                return render(request,'accounts/onetoonebooking.html', context)
            if tempother and tempdesc and tempsession:
                messages.error(request,"Please select either an existing session or other session. Not both")
                context = {'form':form}
                return render(request,'accounts/onetoonebooking.html', context)
            elif tempother and not tempdesc:
                messages.error(request,"Please fill the description of the new session that you are suggesting")
                context = {'form':form}
                return render(request,'accounts/onetoonebooking.html', context)
            elif tempother and tempdesc:
                tempsession = None
            elif tempsession:
                tempother = None
                tempdesc = None
            else:
                messages.error(request,"Please Select either session or other and provide description(for other session)")
                context = {'form':form}
                return render(request,'accounts/onetoonebooking.html', context)

            print(str(tempother)+"tempother")

            ticketno = generate_unique_ticketno()
            while(onetoonetickettbl.objects.filter(ticket_no = ticketno).exists()):
                ticketno = generate_unique_ticketno()
            
            tempform = form.save()

            tempform.ticket_no = ticketno
            tempform.ticket_status = 'requested'
            tempform.save()

            print(tempform.ticket_status)
            print("form saved")
            print(tempform.stuemail)
    
            messages.success(request,"Your request has been submitted successfully. We will reach you shortly")
        
            # send email to requested user, all the mentors, and to the assigned student head
            subject ="CAPS Session Booking"
            html_message = render_to_string('accounts/emailtemplates/email_booking.html', {'temp': tempform})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [str(tempform.stuemail)]
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

            tempname = str(tempform.name)
            rec_email = str(tempform.stuemail)

            message2 = "This email is to inform you that a new One-to-one session has been requested by "+rec_email+" name- "+tempname
            mentorset = User.objects.filter(Q(roles__roles="mentor",is_active=True,)|Q(roles__roles="studenthead"))
            mentorlist = []

            for each in mentorset:
                mentorlist.append(str(each.email))

            message2 = (subject, message2, email_from, mentorlist) 
            send_mass_mail((message2,), fail_silently=False)
            
            print("mails sent")
            return redirect("oto_booking_url")
    context = {'form':form}
    return render(request,'accounts/onetoonebooking.html', context)


#------------ Group booking functions ----------------
def grp_booking_func(request):
    form = GrpBookingForm
    print(datetime.datetime.now())

    print(datetime.datetime.today().date())

    if request.method == 'POST':
        form = GrpBookingForm(request.POST)
        if form.is_valid():
            tempsession = form.cleaned_data['session']
            tempother = form.cleaned_data['other']
            tempdesc = form.cleaned_data['other_desc']

            if not tempother and not tempdesc and not tempsession:
                messages.error(request,"Please Select either session or other and provide description(for other session)")
                context = {'form':form}
                return render(request,'grpbooking.html', context)
            elif tempother and tempdesc and tempsession:
                messages.error(request,"Please select either an existing session or other session. Not both")
                context = {'form':form}
                return render(request,'grpbooking.html', context)
            elif tempother and not tempdesc:
                messages.error(request,"Please fill the description of the new session that you are suggesting")
                context = {'form':form}
                return render(request,'grpbooking.html', context)
            elif tempother and tempdesc:
                tempsession = None
                print("-----------")
                print(tempother)
                print(tempdesc)
                
            elif tempsession:
                tempother = None
                tempdesc = None
                print("-----------")
                print(tempsession)

            print(str(tempother)+"tempother")

            ticketno = generate_unique_ticketno()
            while(onetoonetickettbl.objects.filter(ticket_no = ticketno).exists()):
                ticketno = generate_unique_ticketno()
            
            tempform = form.save()

            tempform.ticket_no = ticketno
            tempform.ticket_status = 'requested'
            tempform.save()

            print(tempform.ticket_status)
            print("form saved")

            # send email to requested user, all the mentors, and to the assigned student head
            subject ="CAPS Session Booking"
            html_message = render_to_string('accounts/emailtemplates/email_booking.html', {'temp': tempform})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [str(tempform.facultyemail)]
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

            tempname = str(tempform.name)

            message2 = "This email is to inform you that a new Group session has been requested by "+str(tempform.facultyemail)+" name- "+tempname
            mentorset = User.objects.filter(Q(roles__roles="mentor",is_active=True,)|Q(roles__roles="studenthead"))
            mentorlist = []

            for each in mentorset:
                mentorlist.append(str(each.email))

            message2 = (subject, message2, email_from, mentorlist) 
            send_mass_mail((message2,), fail_silently=False)
            messages.success(request,"Your request has been submitted successfully. We will reach you shortly")
            print("mails sent")
            return redirect("grp_booking_url")
    context = {'form':form}
    return render(request,'accounts/grpbooking.html', context)


#--------------------------------session list

def usersessionlistfunc(request):
    if sessiontbl.objects.exists():
        temp = sessiontbl.objects.all()
        context = {'temp':temp}
        return render(request, 'accounts/usersessionlist2.html', context)
    else:
        if not sessiontbl.objects.exists():
            return render(request, 'accounts/usersessionlist2.html',)
    return render(request, 'accounts/usersessionlist2.html', context)

