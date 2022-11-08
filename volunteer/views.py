from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse

# sending feedback link to users
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from accounts.models import rolestbl,campustbl,depttbl,coursetbl,User,stuhead_vol_profiletbl
from accounts.models import onetoonetickettbl, peergrouptickettbl
from accounts.forms import OtoVolFeedbackForm, GroupVolFeedbackForm, OtoAssignForm, GroupAssignForm, GroupAssignForm2
from accounts.forms import UserAddForm, VolunteerAddForm, UserEditForm, VolunteerEditForm
from accounts.decorators import  superadmin_only, studenthead_only, volunteer_only, mentor_only

import datetime

# for sending html template through email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.core import mail
from django.utils.html import strip_tags

# ==================================== STUDENT HEAD views ================================ #
# 1 ------------------------------ Student head dashboard 
@login_required(login_url="login_url")
@studenthead_only
def sh_dashboard_func(request):
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing
    requestcount = assignedcount = acceptedcount =workcount = rejectedcount = closedcount = None
    

    if tempwing == "group":
        requestcount = peergrouptickettbl.objects.filter(ticket_status = 'requested').count()
        assignedcount = peergrouptickettbl.objects.filter(ticket_status = 'assigned',assigned_by=request.user).count()
        acceptedcount = peergrouptickettbl.objects.filter(ticket_status = 'accepted',assigned_by=request.user).count()
        workcount = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress',assigned_by=request.user).count()
        rejectedcount = peergrouptickettbl.objects.filter(ticket_status = 'rejected',assigned_by=request.user).count()
        closedcount = peergrouptickettbl.objects.filter(ticket_status = 'closed',assigned_by=request.user).count()


        context = {
                'requestcount':requestcount,
                'assignedcount':assignedcount,
                'acceptedcount':acceptedcount,
                'workcount':workcount,
                'rejectedcount':rejectedcount,
                'closedcount':closedcount,
        }        
        return render(request, 'studenthead/sh_dashboard.html', context)

    elif tempwing == "One-to-One":
        requestcount = onetoonetickettbl.objects.filter(ticket_status = 'requested').count()
        assignedcount = onetoonetickettbl.objects.filter(ticket_status = 'assigned',assigned_by=request.user).count()
        acceptedcount = onetoonetickettbl.objects.filter(ticket_status = 'accepted',assigned_by=request.user).count()
        workcount = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress',assigned_by=request.user).count()
        rejectedcount = onetoonetickettbl.objects.filter(ticket_status = 'rejected',assigned_by=request.user).count()
        closedcount = onetoonetickettbl.objects.filter(ticket_status = 'closed',assigned_by=request.user).count()

        context = {
                'requestcount':requestcount,
                'assignedcount':assignedcount,
                'acceptedcount':acceptedcount,
                'workcount':workcount,
                'rejectedcount':rejectedcount,
                'closedcount':closedcount,
        }        
        return render(request, 'studenthead/sh_dashboard.html', context)
        
# 2 ---------------------- student head list function
@login_required(login_url="login_url")
@studenthead_only
def sh_group_list_func(request):
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing

    reqlist = asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None

    
    reqlist = peergrouptickettbl.objects.filter(ticket_status = 'requested', campus = request.user.campus, assigned_by = request.user)
    asglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', campus = request.user.campus, accepted_count = 0, assigned_by = request.user)
    acclist = peergrouptickettbl.objects.filter(ticket_status = 'accepted', campus = request.user.campus, assigned_by = request.user)
    rejectlist = peergrouptickettbl.objects.filter(ticket_status = 'rejected', campus = request.user.campus, assigned_by = request.user)
    # need to work for half assigned list by chaning filters
    halfasglist = peergrouptickettbl.objects.filter(
        Q(ticket_status = 'assigned') &
        Q(campus = request.user.campus) &
        Q(accepted_count__lt=3) & 
        Q(accepted_count__gt=0) &
        Q(assigned_by = request.user)
    )
    worklist = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress', campus = request.user.campus, assigned_by = request.user)
    closedlist = peergrouptickettbl.objects.filter(ticket_status = 'closed', campus = request.user.campus, assigned_by = request.user)

    accepted = False

    # if reqlist.accepted_by == request.user:
    #     accepted = True

    context = {
    "reqlist":reqlist,
    "asglist":asglist,
    "acclist":acclist,
    "rejectlist":rejectlist,
    "halfasglist":halfasglist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'studenthead/sh_group_list.html', context)

# ------------------------ volunteer group session in deatils view
def sh_grp_detail_func(request,pkid):
    tempgrp = peergrouptickettbl.objects.filter(id=pkid).first()
    context={"tempgrp":tempgrp}
    return render(request,"studenthead/sh_group_details.html", context)

@login_required(login_url="login_url")
@studenthead_only
def sh_oto_list_func(request):
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing

    reqlist = asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None

 
    reqlist = onetoonetickettbl.objects.filter(ticket_status = 'requested', campus = request.user.campus)
    asglist = onetoonetickettbl.objects.filter(ticket_status = 'assigned', campus = request.user.campus, assigned_by = request.user)
    acclist = onetoonetickettbl.objects.filter(ticket_status = 'accepted', campus = request.user.campus, assigned_by = request.user)
    rejectlist = onetoonetickettbl.objects.filter(ticket_status = 'rejected', campus = request.user.campus, assigned_by = request.user)
    worklist = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress', campus = request.user.campus, assigned_by = request.user)
    closedlist = onetoonetickettbl.objects.filter(ticket_status = 'closed', campus = request.user.campus, assigned_by = request.user)
    
    context = {
    "reqlist":reqlist,
    "asglist":asglist,
    "acclist":acclist,
    "rejectlist":rejectlist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'studenthead/sh_oto_list.html', context)

# 3 ----------------------------- student head assign function
@login_required(login_url="login_url")
@studenthead_only
def sh_group_assign_func(request, pkid):
    record = peergrouptickettbl.objects.filter(id=pkid).first()
    userlist = User.objects.filter(is_active=True, roles=3, campus = record.campus)
    context = {'userlist':userlist}
    print(userlist)
    if request.method=="POST":
        v1 = request.POST.get('vol1')
        v2 = request.POST.get('vol2')
        v3 = request.POST.get('vol3')
        v4 = request.POST.get('vol4')
        
        if not( v1 and v2 and v3 and v4):
            messages.error(request,"Minimum 4 volunteers are required !")
            return render(request,'studenthead/sh_group_assign_form.html',context)

        vlist = [v1,v2,v3, v4]
        print(vlist)
        if(len(set(vlist)) == len(vlist)):
            print("All volunteers are unique.")
        else:
            print("All volunteers are not unique.")
            messages.error(request,"Select unique Volunteers!")
            return render(request,'studenthead/sh_group_assign_form.html',context)

        # send mails to all the users 
        subject = "CAPS Group session request"
        msg = "Hello everyone, A group session reqest has been assigned to you! please accept it as soon as possible!"
        email_from = settings.EMAIL_HOST_USER
        vol_list = []

        for each in vlist:
            if each != record.assigned_to:
                record.assigned_to.add(each)
                record.assigned_count = record.assigned_count + 1;
                vol_list.append(str(each))

        record.ticket_status = "assigned"
        record.assigned_by = request.user
        record.assigned_date = datetime.datetime.now()  
        record.save()

        message1 = (subject, msg, email_from, vol_list)
        send_mass_mail((message1,), fail_silently=True)

        messages.success("Assigned successfully!")
        return redirect('sh_group_list_url')

    context = {'userlist':userlist}
    return render(request,'studenthead/sh_group_assign_form.html',context)


# -------------------------------- student head assign and accept the group session request
@login_required(login_url="login_url")
@studenthead_only
def sh_group_assign_and_accept_func(request, pkid):
    record = peergrouptickettbl.objects.filter(id=pkid).first()
    userlist = User.objects.filter(is_active=True, roles=3, campus = record.campus)
    context = {'userlist':userlist}
    print(userlist)
    if request.method=="POST":
        v1 = request.POST.get('vol1')
        v2 = request.POST.get('vol2')
        v3 = request.POST.get('vol3')
        v4 = request.POST.get('vol4')
        
        if not( v1 and v2 and v3 and v4):
            messages.error(request,"Minimum 4 volunteers are required !")
            return render(request,'studenthead/sh_group_assign_form.html',context)

        vlist = [v1,v2,v3, v4]
        print(vlist)
        if(len(set(vlist)) == len(vlist)):
            print("All volunteers are unique.")
        else:
            print("All volunteers are not unique.")
            messages.error(request,"Select unique Volunteers!")
            return render(request,'studenthead/sh_group_assign_form.html',context)

        # send mails to all the users 
        subject = "CAPS Group session request"
        msg = "Hello everyone, A group session reqest has been assigned to you! please accept it as soon as possible!"
        email_from = settings.EMAIL_HOST_USER
        vol_list = []

        for each in vlist:
            if each != record.assigned_to:
                record.assigned_to.add(each)
                record.assigned_count = record.assigned_count + 1;
                vol_list.append(str(each))

        # Add the student head also to accepted list and increase the count!
        record.assigned_to.add(request.user)
        record.accepted_by.add(request.user)
        record.assigned_count = record.assigned_count + 1;

        # Change the status to assigned
        record.ticket_status = "assigned"
        record.assigned_by = request.user
        record.assigned_date = datetime.datetime.now()  
        record.save()

        message1 = (subject, msg, email_from, vol_list)
        send_mass_mail((message1,), fail_silently=True)

        messages.success("Assigned successfully!")
        return redirect('sh_group_list_url')

    context = {'userlist':userlist,"accept":"and self accept"}
    return render(request,'studenthead/sh_group_assign_form.html',context)


# 4 ------------------------------ student head oto assign function
@login_required(login_url="login_url")
@studenthead_only
def sh_oto_assign_func(request, pkid):
    temp = onetoonetickettbl.objects.filter(id = pkid).first()
    form = OtoAssignForm(instance=temp)

    if request.method == "POST":
        form = OtoAssignForm(request.POST)
        if form.is_valid():
            tempform = form.save(commit=False)
            tempuseremail = form.cleaned_data.get('assigned_to')
            tempuser = User.objects.filter(email=tempuseremail).first()
            tempvol = stuhead_vol_profiletbl.objects.filter(user = tempuser).first()

            if tempuser == temp.rejected_by:
                messages.error(request,"The volunteer has already rejected this booking")
                context = {"form":form}
                return render(request,"studenthead/sh_oto_assign_form.html", context)

            if tempvol is None:
                messages.error(request,"The volunteer doesn't belong to the same campus of the request.")
                context = {"form":form}
                return render(request,"studenthead/sh_oto_assign_form.html", context)

            if tempuser.campus != temp.campus or tempvol.wing != 'One-to-One':
                messages.error(request,"The volunteer doesn't belong to the same campus of the request or wing")
                context = {"form":form}
                return render(request,"studenthead/sh_oto_assign_form.html", context)

            if tempuser.roles.roles != "volunteer":
                messages.error(request,"You can't assign to another student head!.")
                context = {"form":form}
                return render(request,"studenthead/sh_oto_assign_form.html", context)
            else:
                temp.ticket_status = "assigned"
                temp.assigned_date = datetime.datetime.now()  
                temp.assigned_to = tempuser
                temp.assigned_by = request.user
                temp.save(update_fields=['assigned_to','assigned_by','ticket_status'])
                #send email to volunteer who has been assigned
                subject = 'CAPS sessions'
                message = 'Hello, you have been assigned the One to one session.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [str(tempuser.email)]
                send_mail( subject, message, email_from, recipient_list )

                messages.success(request,"The request has been assigned to "+str(tempform.assigned_to))
                return redirect("sh_oto_list_url")
            
    context = {"form":form}
    return render(request,"studenthead/sh_oto_assign_form.html", context)


# 5 ----------------------------- student head - oto reassign view
@login_required(login_url="login_url")
@studenthead_only
def sh_oto_reassign_func(request,pkid):

    print("hello")
    return render(request,'studenthead/sh_oto_reassign.html')
# 6 ----------------------------- student head - group reassign view
# call group assign form only

# 7 ----------------------------- student head - volunteer list view
@login_required(login_url="login_url")
@studenthead_only
def sh_volunteer_list_func(request):
    try:
        print(request.user)
        tempuser = stuhead_vol_profiletbl.objects.get(user = request.user)
        print(tempuser.wing)
        if tempuser.wing:
            currentwing = tempuser.wing
            print(currentwing)

        templist = stuhead_vol_profiletbl.objects.filter(wing=currentwing,user__roles=3)
        print(templist)
        context = {'templist':templist,'currentwing':currentwing}
        return render(request, 'studenthead/sh_volunteer_list.html', context)
    except:
        messages.error(request,"Unable to fetch data! sorry!")
        return render(request, 'studenthead/sh_volunteer_list.html')

# ------------------------------ student head - volunteer detail view
@login_required(login_url="login_url")
@studenthead_only
def sh_volunteer_detail_func(request,pkid):
    try:
        tempvol = stuhead_vol_profiletbl.objects.get(id = pkid)
        context = {'tempvol':tempvol}
        return render(request, 'studenthead/sh_volunteer_details.html', context)
    except:
        messages.error(request,"Unable to fetch data! sorry!")
        return render(request, 'studenthead/sh_volunteer_list.html')


# 8 ----------------------------student head - volunteer add view
@login_required(login_url="login_url")
@studenthead_only
def sh_volunteer_add_func(request):
    form1 = UserAddForm
    form2 = VolunteerAddForm

    if request.method == "POST":
        form1 = UserAddForm(request.POST)
        form2 = VolunteerAddForm(request.POST)

        if form1.is_valid() & form2.is_valid():
            tempuser = form1.save(commit=False)
            tempuser.roles = rolestbl.objects.filter(roles = 'volunteer').first()
            tempuser.save()
            tempvol = form2.save(commit=False)
            tempvol.user = tempuser
            tempvol.save()

            pwd = form1.cleaned_data['password1']
            email = form1.cleaned_data['email']
            # send email code with pwd and username to the registered email adress
            subject ="CAPS Registration"
            html_message = render_to_string('emailtemplates/email_registration.html', {'tempuser': tempuser,"pwd":pwd})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [tempuser.email]
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)
        
            messages.success(request, "Volunteer registered successfully")
            return redirect("sh_volunteer_list_url")
        else:
            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,"form2":form2}
    return render(request, 'studenthead/sh_volunteer_add.html',context)

# 9 ------------------------ student head - disable function
@login_required(login_url="login_url")
@studenthead_only
def sh_volunteer_update_func(request, pkid):
    record1=User.objects.get(id=pkid)
    print(record1)
    record2=stuhead_vol_profiletbl.objects.filter(user = record1).first()

    form1 = UserEditForm(instance=record1)
    form2 = VolunteerEditForm(instance=record2)

    if request.method == "POST":
        form1 = UserEditForm(request.POST,instance=record1)
        form2 = VolunteerEditForm(request.POST,instance=record2)

        if form1.is_valid() & form2.is_valid():
            tempuser = form1.save(commit=False)
            #tempuser.roles = rolestbl.objects.filter(roles = 'volunteer').first()
            print(tempuser.roles)
            tempuser.save()
            tempvol = form2.save(commit=False)
            tempvol.user = tempuser
            tempvol.save()
            return redirect("sh_volunteer_list_url")
        else:
            print(form1.errors)
            print(form2.errors)
            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,"form2":form2}
    return render(request, 'studenthead/sh_volunteer_update.html',context)

# 10 ------------------------ student head - disable function
@login_required(login_url="login_url")
@studenthead_only
def set_user_inactive_volunteer_func(request,pkid):
    tempuser=User.objects.filter(id=pkid).first()
    tempuser.is_active=False
    tempuser.save()
    messages.success(request, "Volunteer is inactive")
    return redirect('sh_volunteer_list_url')



# 11 ------------------------- student head my oto sessions ---------------------------------------->
@login_required(login_url="login_url")
@studenthead_only
def sh_my_oto_list_func(request):
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing

    asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None

    asglist = onetoonetickettbl.objects.filter(ticket_status = 'assigned', assigned_to = request.user)
    acclist = onetoonetickettbl.objects.filter(ticket_status = 'accepted', accepted_by = request.user)
    worklist = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress', accepted_by = request.user)
    closedlist = onetoonetickettbl.objects.filter(ticket_status = 'closed', accepted_by = request.user)
    rejectedlist = onetoonetickettbl.objects.filter(ticket_status = 'rejected', assigned_by = request.user)

    print(asglist)
    context = {
    "asglist":asglist,
    "acclist":acclist,
    "worklist":worklist,
    "closedlist":closedlist,
    "rejectedlist":rejectedlist,
    }
    return render(request, 'studenthead/sh_my_oto_list.html', context)

# 2 ---------------------- student head list function
@login_required(login_url="login_url")
@studenthead_only
def sh_my_group_list_func(request):
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing
    reqlist =  peergrouptickettbl.objects.filter(ticket_status = 'requested', assigned_to = request.user).exclude(accepted_by=request.user)
    asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None

    asglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', assigned_to = request.user).exclude(accepted_by=request.user)
    acclist = peergrouptickettbl.objects.filter(ticket_status = 'accepted', accepted_by = request.user)
    # rejectlist = peergrouptickettbl.objects.filter(ticket_status = 'rejected', campus = request.user.campus)assigned_count less than 3 is rejected
    # need to work for half assigned list by chaning filters
    halfasglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', accepted_by = request.user, accepted_count__lt=3)
    worklist = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress', accepted_by = request.user)
    closedlist = peergrouptickettbl.objects.filter(ticket_status = 'closed', accepted_by = request.user)

    print(asglist)

    context = {

    "asglist":asglist,
    "acclist":acclist,
    "halfasglist":halfasglist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'studenthead/sh_my_group_list.html', context)


# ================================================================================================= #
# =========================================  Volunteer functions  ================================= #

# 1 --------------------- volunteer dashboard function
@login_required(login_url="login_url")
@volunteer_only
def vol_dashboard_func(request):
    tempvol = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    print(tempvol)
    if tempvol is not None:
        tempwing = tempvol.wing

    asglist = acclist = worklist = closedlist = halfasglist =  None


    print(tempwing)
    if tempwing == "One-to-One":
        asglist = onetoonetickettbl.objects.filter(ticket_status="assigned",assigned_to=request.user).exclude(rejected_by=request.user).count()
        acclist = onetoonetickettbl.objects.filter(ticket_status="accepted", accepted_by=request.user).count()
        worklist = onetoonetickettbl.objects.filter(ticket_status="work-in-progress", accepted_by=request.user).count()
        closedlist = onetoonetickettbl.objects.filter(ticket_status="closed", accepted_by = request.user).count()
        context = {
        "asglist":asglist,
        "acclist":acclist,
        "worklist":worklist,
        "closedlist":closedlist,
        }
        return render(request, 'volunteer/vol_dashboard.html', context)


    elif tempwing == "group":
        asglist = peergrouptickettbl.objects.filter(ticket_status="assigned",assigned_to=request.user).exclude(rejected_by=request.user).count()
        halfasglist = peergrouptickettbl.objects.filter(Q(ticket_status="assigned") & Q(accepted_by=request.user)).count()
        acclist = peergrouptickettbl.objects.filter(ticket_status="accepted", accepted_by=request.user).count()
        worklist = peergrouptickettbl.objects.filter(ticket_status="work-in-progress", accepted_by=request.user).count()
        closedlist = peergrouptickettbl.objects.filter(ticket_status="closed", accepted_by = request.user).count()

        # asglist = peergrouptickettbl.objects.filter(Q(ticket_status="assigned")).exclude(Q(rejected_by=request.user) |   Q(assigned_to=request.user))
        context = {
        "asglist":asglist,
        "halfasglist":halfasglist,
        "acclist":acclist,
        "worklist":worklist,
        "closedlist":closedlist,
        }
        return render(request, 'volunteer/vol_dashboard.html', context)


# 2 --------------------------- volunteer oto list view
@login_required(login_url="login_url")
@volunteer_only
def vol_oto_list_func(request):
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing

    asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None

    asglist = onetoonetickettbl.objects.filter(ticket_status = 'assigned', assigned_to = request.user)
    acclist = onetoonetickettbl.objects.filter(ticket_status = 'accepted', accepted_by = request.user)
    worklist = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress', accepted_by = request.user)
    closedlist = onetoonetickettbl.objects.filter(ticket_status = 'closed', accepted_by = request.user)
    
    print(asglist)
    context = {
    "asglist":asglist,
    "acclist":acclist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'volunteer/vol_oto_list.html', context)

# 2 ---------------------- student head list function
@login_required(login_url="login_url")
@volunteer_only
def vol_group_list_func(request):
 
    tempsh = stuhead_vol_profiletbl.objects.filter(user = request.user).first()
    tempwing = tempsh.wing

    asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None

    asglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', assigned_to = request.user).exclude(accepted_by=request.user)
    acclist = peergrouptickettbl.objects.filter(ticket_status = 'accepted', accepted_by = request.user)
    rejectlist = peergrouptickettbl.objects.filter(ticket_status = 'rejected', accepted_by = request.user)
    # need to work for half assigned list by chaning filters
    halfasglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', accepted_by = request.user, accepted_count__lt=3)
    worklist = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress', accepted_by = request.user)
    closedlist = peergrouptickettbl.objects.filter(ticket_status = 'closed', accepted_by = request.user)

    print(asglist)

    context = {

    "asglist":asglist,
    "acclist":acclist,
    "halfasglist":halfasglist,
    "rejectlist":rejectlist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'volunteer/vol_group_list.html', context)


# 2 --------------------------- volunteer oto accept view
def vol_oto_accept_func(request,pkid):

    # if request.user.roles=="studenthead":
    #     tempoto = onetoonetickettbl.objects.filter(id = pkid, ticket_status = "requested").first();
    # else:
    #     tempoto = onetoonetickettbl.objects.filter(id = pkid, ticket_status = "assigned").first();

    tempoto = onetoonetickettbl.objects.filter(id = pkid).first();
    print(tempoto)
    tempoto.ticket_status = "accepted"
    tempoto.accepted_date = datetime.datetime.now()  
    tempoto.accepted_by = request.user

    if request.user.roles.roles == "studenthead":
        tempoto.assigned_by = request.user
        tempoto.assigned_date = datetime.datetime.now()  

    tempoto.save()

    # send email to requested user, all the mentors, and to the assigned student head
    tempuser = User.objects.filter(id=request.user.id)

    # send email to requested user, all the mentors, and to the assigned student head
    subject ="CAPS Session Booking"
    html_message = render_to_string('accounts/emailtemplates/email_accepted.html', {'temp': tempoto,"tempuser":tempuser})
    plain_message = strip_tags(html_message)
    email_from = settings.EMAIL_HOST_USER
    email_to = str([tempoto.stuemail])
    send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

    tempname = str(tempoto.name)
    tempemail = str([tempuser.email])
    message2 = "The One to one session has been accepted by "+tempemail+" name- "+tempname
    mentorset = User.objects.filter(Q(roles__roles="mentor",is_active=True,)|Q(roles_roles="studenthead"))
    mentorlist = []

    for each in mentorset:
        mentorlist.append(str(each.email))

    message2 = (subject, message2, email_from, mentorlist) 
    send_mass_mail((message2), fail_silently=False)

    # subject = 'CAPS Session Booking'
    # message1 = 'Hello, Your session request has been accepted. please contact -'+tempemail+' name:'+tempname
    # message2 = "The One to one session has been accepted by "+tempemail+" name- "+tempname
    # email_from = settings.EMAIL_HOST_USER

    # mentorset = User.objects.filter(roles__roles="mentor")
    # mentorlist = []

    # for each in mentorset:
    #     mentorlist.append(str(each.email))
    # print(mentorlist)
    # message1 = (subject, message1, email_from, [tempoto.stuemail,])
    # message2 = (subject, message2, email_from, mentorlist)
    # send_mass_mail((message1, message2), fail_silently=False)

    print("mails sent")

    if request.user.roles.roles == 'studenthead':
        tempoto.assigned_by = request.user
        tempoto.assigned_to = request.user
        tempoto.save(update_fields=['assigned_to', 'assigned_by'])
        return redirect('sh_dashboard_url')
    else:
        return redirect('vol_dashboard_url')

# 3 --------------------------- volunteer oto reject view
def vol_oto_reject_func(request,pkid):

    tempoto = onetoonetickettbl.objects.filter(id = pkid).first();
    print(tempoto)
    tempoto.rejected_by.add(request.user)
    # test this function
    tempoto.ticket_status = "rejected"
    tempoto.assigned_to = None
    tempoto.save()

    # sending email to mentor and student heads after rejecting
    subject = 'CAPS sessions'
    msg = 'Hello, Your session request has been Rejected. '
    email_from = settings.EMAIL_HOST_USER
    mentorset = User.objects.filter(Q(roles__roles="mentor") | Q(roles__roles="volunteer") & Q(is_active=True))
    mentorlist = []

    for each in mentorset:
        mentorlist.append(str(each.email))
    print(mentorlist)
    message2 = (subject, msg, email_from, mentorlist)
    send_mass_mail((message2,), fail_silently=False)

    print("mails sent")


    # send email to requested user, all the mentors, and to the assigned student head
    return redirect('vol_dashboard_url')

# 4 --------------------------- volunteer oto workinprogress view
def vol_oto_work_func(request,pkid):

    tempoto = onetoonetickettbl.objects.filter(id = pkid, ticket_status = "accepted").first();
    print(tempoto)
    tempoto.ticket_status = "work-in-progress"
    tempoto.save()
    # send email to requested user, all the mentors, and to the assigned student head
    if request.user.roles.roles == 'studenthead':
        return redirect('sh_dashboard_url')
    else:
        return redirect('vol_dashboard_url')

# 5 --------------------------- volunteer oto closed view
def vol_oto_feedback_func(request,pkid):
    form = OtoVolFeedbackForm
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()

    if tempoto.v_feedback != None:
        if request.user.roles.roles == 'studenthead':
            return redirect('sh_dashboard_url')
        else:
            return redirect('vol_dashboard_url')
    
    if request.method == 'POST':
        form = OtoVolFeedbackForm(request.POST, instance = tempoto)
        if form.is_valid():
            tempform = form.save(commit=False)
            tempform.s_feedback = form.cleaned_data.get('s_feedback')
            tempform.hours = form.cleaned_data.get('hours')
            tempform.save()

            tempvol = stuhead_vol_profiletbl.objects.filter(user= request.user).first()
            tempvol.total_session_hrs = tempvol.total_session_hrs + tempform.hours
            tempvol.no_of_sessions_conducted += 1
            tempvol.save()
            messages.success(request,"Feedback submited successfully")
            # tempoto = onetoonetickettbl.objects.filter(id=pkid, ticket_status="accepted").first();
            print(tempform)

           
            tempoto.ticket_status = "closed"
            tempoto.closed_date = datetime.datetime.now()
            tempoto.save()
            
            # # -----------------------send feedback link to the user - student
            # email_template_name = "volunteer/oto_feedback.txt"
            # c = {
            # "email":tempoto.stuemail,
            # 'domain':'127.0.0.1:8000',
            # 'site_name': 'Website',
            # "uid": urlsafe_base64_encode(force_bytes(tempoto.pk)),
            # "user": tempoto,
            # 'protocol': 'http',
            # }
            # feedbacklink = render_to_string(email_template_name, c)
            
            # # send email to requested user, all the mentors, and to the assigned student head
            # subject = 'CAPS session update'
            # message = 'Hello, The requested session is closed by the volunteer. Hope you had a wonderful learning experience! Thankyou for choosing our CAPS sessions!'
            # email_from = settings.EMAIL_HOST_USER
            # recipient_list = [tempoto.stuemail]
            # msg = "one to one session is closed"
            # mentorset = User.objects.filter(Q(roles__roles="mentor") | Q(roles__roles="volunteer") & Q(is_active=True))
            # mentorlist = []
            # rec_email = str(tempoto.stuemail)
            # for each in mentorset:
            #     mentorlist.append(str(each.email))

            # message1 = (subject, feedbacklink, email_from, [rec_email,])
            # message2 = (subject, msg, email_from, mentorlist)

            # send_mass_mail((message1, message2), fail_silently=False)

            # send email to requested user, all the mentors, and to the assigned student head
            tempuser = User.objects.filter(id=request.user.id)
            subject ="CAPS Session Booking"
            html_message = render_to_string('accounts/emailtemplates/email_accepted.html', {'temp': tempoto,"tempuser":tempuser})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = str([tempoto.stuemail])
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

            tempname = str(tempoto.name)
            tempemail = str([tempuser.email])
            message2 = "The One to one session has been Closed by "+tempemail+" name- "+tempname
            mentorset = User.objects.filter(Q(roles__roles="mentor",is_active=True,)|Q(roles_roles="studenthead"))
            mentorlist = []

            for each in mentorset:
                mentorlist.append(str(each.email))

            message2 = (subject, message2, email_from, mentorlist) 
            send_mass_mail((message2), fail_silently=False)


            if request.user.roles.roles == 'studenthead':
                return redirect('sh_dashboard_url')
            else:
                return redirect('vol_dashboard_url')

    context = {"form":form}
    if request.user.roles.roles == 'studenthead':
        return render(request,'studenthead/sh_my_oto_feedback.html', context)
    else:
        return render(request,'volunteer/vol_oto_feedback.html', context)

# ------------------------ volunteer group session in deatils view
def vol_grp_detail_func(request,pkid):
    tempgrp = peergrouptickettbl.objects.filter(id=pkid).first()
    context={"tempgrp":tempgrp}
    return render(request,"volunteer/vol_group_details.html", context)
    

# 6 --------------------------- volunteer group accept view
def vol_group_accept_func(request,pkid):
    tempgroup = peergrouptickettbl.objects.filter(id = pkid).first();
    print(tempgroup)
    acceptedcount = tempgroup.accepted_by.count()

    if acceptedcount > 3:
        messages.error(request, "The number of acceptance is already full")
        return redirect('vol_dashboard_url')

    if request.user.roles.roles == "studenthead":
        tempgroup.ticket_status = "assigned"
    
    tempgroup.accepted_by.add(request.user)
    tempgroup.accepted_count = tempgroup.accepted_count+1
    if acceptedcount == 2:
        tempgroup.ticket_status = "accepted"
        tempgroup.accepted_date = datetime.datetime.now()

    
    tempgroup.save()
    # send email to requested user, all the mentors, and to the assigned student head
     # send email to requested user, all the mentors, and to the assigned student head
    tempuser = User.objects.filter(id=request.user.id)
    subject ="CAPS Session Booking"
    html_message = render_to_string('accounts/emailtemplates/email_accepted.html', {'temp': tempgroup,"tempuser":tempuser})
    plain_message = strip_tags(html_message)
    email_from = settings.EMAIL_HOST_USER
    email_to = str([tempgroup.facultyemail])
    send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

    tempname = str(tempgroup.name)
    tempemail = str([tempuser.email])
    message2 = "The One to one session has been accepted by "+tempemail+" name- "+tempname
    mentorset = User.objects.filter(Q(roles__roles="mentor",is_active=True,)|Q(roles_roles="studenthead"))
    mentorlist = []

    for each in mentorset:
        mentorlist.append(str(each.email))

    message2 = (subject, message2, email_from, mentorlist) 
    send_mass_mail((message2), fail_silently=False)

    if request.user.roles.roles == 'studenthead':
        return redirect('sh_dashboard_url')
    else:
        return redirect('vol_dashboard_url')


# 7 --------------------------- volunteer group reject view
def vol_group_reject_func(request,pkid):

    tempgroup = peergrouptickettbl.objects.filter(id = pkid, ticket_status = "assigned").first();
    print(tempgroup)
    tempgroup.rejected_by.add(request.user)
    tempgroup.assigned_to.remove(request.user)
    tempgroup.assigned_count = tempgroup.assigned_count - 1
    if tempgroup.assigned_count < 3:
        tempgroup.ticket_status = "rejected" 
    tempgroup.save()
    # send email to requested user, all the mentors, and to the assigned student head

    return redirect('vol_dashboard_url')

# 8 --------------------------- volunteer group workinprogress view
def vol_group_work_func(request,pkid):

    tempgroup = peergrouptickettbl.objects.filter(id = pkid, ticket_status = "accepted").first();
    print(tempgroup)
    tempgroup.ticket_status = "work-in-progress"
    tempgroup.save()
    # send email to requested user, all the mentors, and to the assigned student head
    if request.user.roles.roles == 'studenthead':
        return redirect('sh_dashboard_url')
    else:
        return redirect('vol_dashboard_url')


# 9 --------------------------- volunteer group closed view
def vol_group_feedback_func(request,pkid):
    form = GroupVolFeedbackForm
    tempgroup = peergrouptickettbl.objects.filter(id=pkid).first()

    if request.method == 'POST':
        form = GroupVolFeedbackForm(request.POST, instance = tempgroup)
        if form.is_valid():
            tempform = form.save(commit=False)
            tempform.s_feedback = form.cleaned_data.get('s_feedback')
            tempform.hours = form.cleaned_data.get('hours')
            tempform.closed_date = datetime.datetime.now()
            tempform.ticket_status = "closed"
            tempform.save()
            messages.success(request,"Feedback submited successfully")

        for each in tempform.accepted_by.all():
            print(each)
            tempuser = stuhead_vol_profiletbl.objects.filter(user=each).first()
            print(tempuser)
            tempuser.total_session_hrs += tempform.hours
            tempuser.no_of_sessions_conducted +=1
            tempuser.save()

        # send feedback link to the user - student
        # email_template_name = "volunteer/oto_feedback.txt"
        # c = {
        # "email":tempform.facultyemail,
        # 'domain':'127.0.0.1:8000',
        # 'site_name': 'Website',
        # "uid": urlsafe_base64_encode(force_bytes(tempform.pk)),
        # "user": tempform,
        # # 'token': default_token_generator.make_token(tempoto),
        # 'protocol': 'http',
        # }
        # feedbacklink = render_to_string(email_template_name, c)
        
        # # send email to requested user, all the mentors, and to the assigned student head
        # subject = 'CAPS session update'
        # message = 'Hello, The requested session is closed by the volunteer. Hope you had a wonderful learning experience! Thankyou for choosing our CAPS sessions!'
        # email_from = settings.EMAIL_HOST_USER
        # recipient_list = [tempform.facultyemail]
        # msg = "one to one session is closed"
        # mentorset = User.objects.filter(Q(roles__roles="mentor") | Q(roles__roles="volunteer") & Q(is_active=True))
        # mentorlist = []
        # rec_email = str(tempform.facultyemail)
        # for each in mentorset:
        #     mentorlist.append(str(each.email))

        # message1 = (subject, feedbacklink, email_from, [rec_email,])
        # message2 = (subject, msg, email_from, mentorlist)

        # send_mass_mail((message1, message2), fail_silently=False)
        # send email to requested user, all the mentors, and to the assigned student head
        tempuser = User.objects.filter(id=request.user.id)
        subject ="CAPS Session Booking"
        html_message = render_to_string('accounts/emailtemplates/email_accepted.html', {'temp': tempoto,"tempuser":tempuser})
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        email_to = str([tempgroup.facultyemail])
        send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

        tempname = str(tempgroup.name)
        tempemail = str([tempuser.email])
        message2 = "The Group peer session has been Closed by "+tempemail+" name- "+tempname
        mentorset = User.objects.filter(Q(roles__roles="mentor",is_active=True,)|Q(roles_roles="studenthead"))
        mentorlist = []

        for each in mentorset:
            mentorlist.append(str(each.email))

        message2 = (subject, message2, email_from, mentorlist) 
        send_mass_mail((message2), fail_silently=False)

        tempgroup = peergrouptickettbl.objects.filter(id = pkid).first();
        print(tempgroup)

        # send an email to the faculty with feedback link
        # send email to requested user, all the mentors, and to the assigned student head

        return redirect('vol_dashboard_url')

    context = {"form":form}
    return render(request,'volunteer/vol_peer_feedback.html', context)


# ############################  student head and volunteer comon functions
# ------------------------ studenthead oto details list
def sh_oto_detail_func(request,pkid):
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()
    context={"tempoto":tempoto}
    return render(request,"studenthead/sh_oto_details.html", context)

def vol_oto_detail_func(request,pkid):
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()
    context={"tempoto":tempoto}
    return render(request,"volunteer/vol_oto_details.html", context)
