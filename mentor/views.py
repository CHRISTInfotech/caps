from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError

from accounts.models import rolestbl,campustbl,depttbl,coursetbl,User,stuhead_vol_profiletbl, sessiontbl
from accounts.models import onetoonetickettbl, peergrouptickettbl
from accounts.forms import OtoVolFeedbackForm, GroupVolFeedbackForm, OtoAssignForm, GroupAssignForm, GroupAssignForm2, sessionaddform
from accounts.forms import UserAddForm, VolunteerAddForm, UserEditForm, VolunteerEditForm, profileaddform, OtoReportForm, UserSearchForm
from accounts.decorators import  superadmin_only, studenthead_only, volunteer_only, mentor_only
from .filters import OtoFilter, GroupFilter, UserFilter

import datetime
from django.forms import *
from itertools import chain
from datetime import datetime,timedelta,timezone
import random
import string
from django.db.models import Count,Max,Sum
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# Create your views here.
# ========================================= MENTOR Views ==============================================#


# ---------------------------- checking for unattended requests that are more than 24 hours old
def check_unattended_request_func():

    today = datetime.now()
    print(today)
    tempoto = onetoonetickettbl.objects.filter(Q(ticket_status="requested")|Q(ticket_status="assigned"))
    tempgroup = peergrouptickettbl.objects.filter(Q(ticket_status="requested")|Q(ticket_status="assigned"))
    otocount = groupcount = 0;
 
    for each in tempoto:
        result = datetime.now().astimezone() - each.request_datetime

        if (result.days)>1:
            otocount+=1

    for each in tempgroup:
        result = datetime.now().astimezone() - each.request_datetime
        if (result.days)>1:
            groupcount+=1

    result = {"oto":otocount,"grp":groupcount}
    return result

# 1 -------------------------- Mentor dashboard view
@login_required(login_url="login_url")
@mentor_only
def mentor_dashboard_func(request):

    result = check_unattended_request_func()
    print(result)

    

    oto_requestcount = oto_assignedcount = oto_acceptedcount =oto_workcount = oto_rejectedcount = oto_closedcount = None
    group_requestcount = group_assignedcount = group_acceptedcount =group_workcount = group_rejectedcount = groupclosedcount = None
    
    oto_requestcount = onetoonetickettbl.objects.filter(ticket_status = 'requested').count()
    oto_assignedcount = onetoonetickettbl.objects.filter(ticket_status = 'assigned').count()
    oto_acceptedcount = onetoonetickettbl.objects.filter(ticket_status = 'accepted').count()
    oto_workcount = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress').count()
    oto_rejectedcount = onetoonetickettbl.objects.filter(ticket_status = 'rejected').count()
    oto_closedcount = onetoonetickettbl.objects.filter(ticket_status = 'closed').count()

    group_requestcount = peergrouptickettbl.objects.filter(ticket_status = 'requested').count()
    group_assignedcount = peergrouptickettbl.objects.filter(ticket_status = 'assigned').count()
    group_acceptedcount = peergrouptickettbl.objects.filter(ticket_status = 'accepted').count()
    group_workcount = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress').count()
    group_rejectedcount = peergrouptickettbl.objects.filter(ticket_status = 'rejected').count()
    group_closedcount = peergrouptickettbl.objects.filter(ticket_status = 'closed').count()

    context = {
        'oto_requestcount':oto_requestcount,
        'oto_assignedcount':oto_assignedcount,
        'oto_acceptedcount':oto_acceptedcount,
        'oto_workcount':oto_workcount,
        'oto_rejectedcount':oto_rejectedcount,
        'oto_closedcount':oto_closedcount,

        'group_requestcount':group_requestcount,
        'group_assignedcount':group_assignedcount,
        'group_acceptedcount':group_acceptedcount,
        'group_workcount':group_workcount,
        'group_rejectedcount':group_rejectedcount,
        'group_closedcount':group_closedcount,

        'result':result,
    }
    
    return render(request, 'mentor/mentor_dashboard.html', context)

# 2 -------------------------- Mentor volunteer list view
@login_required(login_url="login_url")
@mentor_only
def mentor_volunteer_list_func(request):
    try:
        templist = stuhead_vol_profiletbl.objects.filter(user__roles=3).order_by('id')
        print(templist)
        context = {'templist':templist,}
        return render(request, 'mentor/mentor_volunteer_list.html', context)
    except:
        messages.error(request,"Unable to fetch data! sorry!")
        return render(request, 'mentor/mentor_volunteer_list.html')

# 3 ---------------------------- Mentor - volunteer add view
@login_required(login_url="login_url")
@mentor_only
def mentor_volunteer_add_func(request):
    form1 = UserAddForm
    form2 = VolunteerAddForm

    if request.method == "POST":
        form1 = UserAddForm(request.POST)
        form2 = VolunteerAddForm(request.POST)

        if form1.is_valid() & form2.is_valid():
            tempuser = form1.save(commit=False)
            tempuser.roles = rolestbl.objects.filter(roles = 'volunteer').first()
            print(tempuser.roles)
            tempuser.save()
            tempvol = form2.save(commit=False)
            tempvol.user = tempuser
            tempvol.save()

            pwd = form1.cleaned_data['password1']
            email = form1.cleaned_data['email']
            print(pwd + email)
            # send email code with pwd and username to the registered email adress
            subject ="CAPS Registration"
            html_message = render_to_string('emailtemplates/email_registration.html', {'tempuser': tempuser,"pwd":pwd})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [tempuser.email]
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)
            
            messages.success(request, "Volunteer registered successfully")
            return redirect("mentor_volunteer_list_url")
        else:
            print(form1.errors)
            print(form2.errors)
            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,"form2":form2}
    return render(request, 'mentor/mentor_volunteer_add.html',context)


# 4 ------------------------ mentor - volunter update function
@login_required(login_url="login_url")
@mentor_only
def mentor_volunteer_update_func(request, pkid):
    record1=User.objects.get(id=pkid)
    print("id at start"+str(pkid))
    record2=stuhead_vol_profiletbl.objects.filter(user = record1).first()

    form1 = UserEditForm(instance=record1)
    form2 = VolunteerEditForm(instance=record2)

    if request.method == "POST":
        form1 = UserEditForm(request.POST,instance=record1)
        form2 = VolunteerEditForm(request.POST,instance=record2)

        if form1.is_valid() & form2.is_valid():
            # tempuser = form1.save(commit=False)
            # tempuser.save()
            form1.save()
            form2.save()
            # tempvol = form2.save(commit=False)
            # tempvol.user = tempuser
            # tempvol.save()
            
            return redirect("mentor_volunteer_list_url")
        else:
            print(form1.errors)
            print(form2.errors)
            messages.error(request, "Invalid data! please check the form.")


    context = {"form1":form1,"form2":form2}
    return render(request, 'mentor/mentor_volunteer_update.html',context)

# common function to disable both volunteers and studenthead
# 5 ------------------------ mentor - volunteer student heda disable function
@login_required(login_url="login_url")
@mentor_only
def mentor_set_user_inactive_func(request,pkid):
    tempuser=User.objects.filter(id=pkid).first()
    print(tempuser.is_active)
    print("inactive")
    tempuser.is_active=False
    tempuser.save()
    messages.success(request, "User is inactive")
    return redirect('mentor_dashboard_url')

@login_required(login_url="login_url")
@mentor_only
def mentor_set_user_active_func(request,pkid):
    tempuser=User.objects.filter(id=pkid).first()
    print(tempuser.is_active)
    tempuser.is_active=True
    tempuser.save()
    messages.success(request, "User is Active")
    return redirect('mentor_dashboard_url')

# 9 ----------------------Mentor -common method chnage role of volunteer to student head and vice versa
@login_required(login_url="login_url")
@mentor_only
def mentor_change_role_func(request, pkid):
    
    tempuser = User.objects.filter(id=pkid).first()
    tempvol = stuhead_vol_profiletbl.objects.filter(user=tempuser).first()
    tempwing = tempvol.wing
    no_oto = no_grp = False

    if tempwing == "One-to-One":

        no_oto = onetoonetickettbl.objects.filter(~Q(ticket_status = "closed")|~Q(ticket_status = "cancelled")&Q(assigned_by=tempuser)).exists()
        if not no_oto:
            no_oto = onetoonetickettbl.objects.filter(~Q(ticket_status = "closed")|~Q(ticket_status = "cancelled")&Q(accepted_by=tempuser)).exists()
    else:

        no_grp = peergrouptickettbl.objects.filter(~Q(ticket_status = "closed")|~Q(ticket_status = "cancelled")&Q(assigned_by=tempuser)).exists()
        if not no_grp:
            no_grp = peergrouptickettbl.objects.filter(~Q(ticket_status = "closed")|~Q(ticket_status = "cancelled")&Q(accepted_by=tempuser)).exists()

    print(no_oto)
    
    if not no_oto and no_grp:
        # change role to volunteer
        if tempuser.roles.roles == 'volunteer':
            tempuser.roles = rolestbl.object.filter(roles="studenthead").first()
            messages.success(request,"Successfully changed the role of "+tempuser.first_name+" to studenthead")
            return redirect("mentor_volunteer_list_url")

        elif tempuser.roles.roles == 'studenthead':
            tempuser.roles = rolestbl.object.filter(roles="volunteer").first()
            messages.success(request,"Successfully changed the role of "+tempuser.first_name+" to Volunteer")
            return redirect("mentor_sh_list_url")

    else:
        messages.error(request,"Can't change the role as there are unfinished sessions either assigned or accepted by "+tempuser.first_name)
        
        if tempuser.roles.roles == 'volunteer':
            return redirect("mentor_volunteer_list_url")
        else:
            return redirect("mentor_sh_list_url")

# 6 -------------------------- Mentor - studenthead list view
@login_required(login_url="login_url")
@mentor_only
def mentor_sh_list_func(request):
    try:
        templist = stuhead_vol_profiletbl.objects.filter(user__roles=2)
        print(templist)
        context = {'templist':templist,}
        return render(request, 'mentor/mentor_sh_list.html', context)
    except:
        messages.error(request,"Unable to fetch data! sorry!")
        return render(request, 'mentor/mentor_sh_list.html')

# 7 ---------------------------- Mentor - studenthead add view
@login_required(login_url="login_url")
@mentor_only
def mentor_sh_add_func(request):
    form1 = UserAddForm
    form2 = VolunteerAddForm

    if request.method == "POST":
        form1 = UserAddForm(request.POST)
        form2 = VolunteerAddForm(request.POST)

        if form1.is_valid() & form2.is_valid():
            tempuser = form1.save(commit=False)
            tempuser.roles = rolestbl.objects.filter(roles = 'studenthead').first()
            print(tempuser.roles)
            tempuser.save()
            tempvol = form2.save(commit=False)
            tempvol.user = tempuser
            tempvol.save()

            pwd = form1.cleaned_data['password1']
            email = form1.cleaned_data['email']
            print(pwd + email)
            # send email code with pwd and username to the registered email adress
            subject ="CAPS Registration"
            html_message = render_to_string('emailtemplates/email_registration.html', {'tempuser': tempuser,"pwd":pwd})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [tempuser.email]
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)

            messages.success(request, "Student head registered successfully")
            return redirect("mentor_sh_list_url")
        else:
            print(form1.errors)
            print(form2.errors)
            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,"form2":form2}
    return render(request, 'mentor/mentor_sh_add.html',context)


# 8 ------------------------ mentor - student head update
@login_required(login_url="login_url")
@mentor_only
def mentor_sh_update_func(request, pkid):
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
            return redirect("mentor_sh_list_url")
        else:
            print(form1.errors)
            print(form2.errors)
            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,"form2":form2}
    return render(request, 'mentor/mentor_sh_update.html',context)



# 9 ---------------------- Mentor oto and group list views---------------------------------------------->

# ------------------------ Mentor- Group list view
@login_required(login_url="login_url")
@mentor_only
def mentor_group_list_func(request):
    reqlist = asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None
 
    reqlist = peergrouptickettbl.objects.filter(ticket_status = 'requested', campus = request.user.campus)
    asglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', campus = request.user.campus)
    acclist = peergrouptickettbl.objects.filter(ticket_status = 'accepted', campus = request.user.campus)
    rejectlist = peergrouptickettbl.objects.filter(ticket_status = 'rejected', campus = request.user.campus)
    # need to work for half assigned list by chaning filters
    halfasglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', campus = request.user.campus, assigned_count__lt=3)
    worklist = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress', campus = request.user.campus)
    closedlist = peergrouptickettbl.objects.filter(ticket_status = 'closed', campus = request.user.campus)

    context = {
    "reqlist":reqlist,
    "asglist":asglist,
    "acclist":acclist,
    "rejectlist":rejectlist,
    "halfasglist":halfasglist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'mentor/mentor_group_list.html', context)

# 10 --------------------------- mentor - oto list view
@login_required(login_url="login_url")
@mentor_only
def mentor_oto_list_func(request):
    reqlist = asglist = acclist = rejectlist = worklist = closedlist =  None
    
    reqlist = onetoonetickettbl.objects.filter(ticket_status = 'requested', campus = request.user.campus)
    asglist = onetoonetickettbl.objects.filter(ticket_status = 'assigned', campus = request.user.campus)
    acclist = onetoonetickettbl.objects.filter(ticket_status = 'accepted', campus = request.user.campus)
    rejectlist = onetoonetickettbl.objects.filter(ticket_status = 'rejected', campus = request.user.campus)
    worklist = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress', campus = request.user.campus)
    closedlist = onetoonetickettbl.objects.filter(ticket_status = 'closed', campus = request.user.campus)
    
    context = {
    "reqlist":reqlist,
    "asglist":asglist,
    "acclist":acclist,
    "rejectlist":rejectlist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'mentor/mentor_oto_list.html', context)

# --------------------------------- Mentor - oto details view
def mentor_oto_detail_func(request,pkid):
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()
    context={"tempoto":tempoto}
    return render(request,"mentor/mentor_oto_details.html", context)

# --------------------------------- Mentor group details list
def mentor_grp_detail_func(request,pkid):
    tempgrp = peergrouptickettbl.objects.filter(id=pkid).first()
    print(tempgrp)
    context={"tempgrp":tempgrp}
    return render(request,"mentor/mentor_group_details.html", context)


# 11 ----------------------------- Mentor - group volunteer assign function
@login_required(login_url="login_url")
@mentor_only
def mentor_group_assign_func(request, pkid):
    record = peergrouptickettbl.objects.filter(id=pkid).first()
    templist = User.objects.filter(is_active=True, roles__roles="volunteer", campus = record.campus,)
    print(type(templist))
    userlist = []
    for each in templist:
        print(each)
        if each.stuhead_vol_profiletbl.wing == "group":
            userlist.append(each)



    context = {'userlist':userlist}
    print(userlist)
    if request.method=="POST":
        v1 = request.POST.get('vol1')
        v2 = request.POST.get('vol2')
        v3 = request.POST.get('vol3')
        v4 = request.POST.get('vol4')
        
        if not( v1 and v2 and v3 and v4):
            messages.error(request,"Minimum 4 volunteers are required !")
            return render(request,'mentor/mentor_group_assign_form.html',context)

        vlist = [v1,v2,v3, v4]
        print(vlist)
        if(len(set(vlist)) == len(vlist)):
            print("All volunteers are unique.")
        else:
            print("All volunteers are not unique.")
            messages.error(request,"Select unique Volunteers!")
            return render(request,'mentor/mentor_group_assign_form.html',context)

        # send mails to all the users 
        subject = "CAPS Group session request"
        msg = "Hello everyone, A group session reqest has been assigned to you! please accept it as soon as possible!"
        email_from = settings.EMAIL_HOST_USER
        vol_list =[]

        for each in vlist:
            if each != record.assigned_to:
                record.assigned_to.add(each)
                record.assigned_count = record.assigned_count + 1;
                vol_list.append(str(each))
                
        record.ticket_status = "assigned"
        record.assigned_by = request.user
        record.save()

        message1 = (subject, msg, email_from, vol_list)
        send_mass_mail((message1,), fail_silently=True)

        return redirect('mentor_group_list_url')

    context = {'userlist':userlist}
    return render(request,'mentor/mentor_group_assign_form.html',context)


# 12 ------------------------------ Mentor - oto assign function
@login_required(login_url="login_url")
@mentor_only
def mentor_oto_assign_func(request, pkid):
    temp = onetoonetickettbl.objects.filter(id = pkid).first()
    form = OtoAssignForm(instance=temp)

    if request.method == "POST":
        form = OtoAssignForm(request.POST)
        if form.is_valid():
            tempform = form.save(commit=False)
            tempuseremail = form.cleaned_data.get('assigned_to')
            tempuser = User.objects.filter(email=tempuseremail).first()
            tempvol = stuhead_vol_profiletbl.objects.filter(user = tempuser).first()

            print(temp.rejected_by)
            if tempuser == temp.rejected_by:
                messages.error(request,"The volunteer has already rejected this booking")
                context = {"form":form}
                return render(request,"mentor/mentor_oto_assignform.html", context)

            if tempvol is None:
                messages.error(request,"The volunteer doesn't belong to the same campus of the request.")
                context = {"form":form}
                return render(request,"mentor/mentor_oto_assignform.html", context)

            if tempuser.campus != temp.campus:
                messages.error(request,"The volunteer doesn't belong to the same campus of the request.")
                context = {"form":form}
                return render(request,"mentor/mentor_oto_assignform.html", context)
            else:
                temp.ticket_status = "assigned"
                temp.assigned_to = tempuser
                temp.assigned_by = request.user
                temp.save(update_fields=['assigned_to','ticket_status','assigned_by'])

                #send email to volunteer who has been assigned
                # rec_email = str(tempuser.email)
                subject = 'CAPS sessions'
                message = 'Hello, you have been assigned the One to one session.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [str(tempuser.email)]
                send_mail( subject, message, email_from, recipient_list )

   
                messages.success(request,"The request has been assigned to "+str(tempform.assigned_to))
                return redirect("mentor_oto_list_url")
            
    context = {"form":form}
    return render(request,"mentor/mentor_oto_assignform.html", context)

# ============================= MENTOR SESSION VIEWS =======================================>

#--------------------------------session list
@login_required(login_url="login_url")
@mentor_only
def mentor_session_add_func(request):
    form =sessionaddform()
    temp = None
    if sessiontbl.objects.exists():
        temp = sessiontbl.objects.all()
    
    context = {'temp':temp, 'form':form}
    if request.method == "POST":
        form = sessionaddform(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, "Session saved")
            a = form.save(commit = False)
            a.save()
            form = sessionaddform()
        else:
            messages.error(request, "cannot add session. Invalid information.")
    return render (request,"mentor/mentor_session_add.html", context)

@login_required(login_url="login_url")
@mentor_only
def mentor_session_delete_func(request, pkid):
    record=sessiontbl.objects.get(id=pkid)
    print(record)
    try:
        record.delete()
    except ProtectedError as e:
        messages.error(request,"Cannot delete Sessions.")
        return redirect("mentor_session_add_url")
    messages.success(request, "Session deleted")
    return redirect("mentor_session_add_url")



@login_required(login_url="login_url")
@mentor_only
def mentor_session_update_func(request, pkid):
    record=sessiontbl.objects.get(id=pkid)
    form = sessionaddform(instance=record)
    if request.method == "POST":
        form = sessionaddform(request.POST,request.FILES,instance=record)
        if form.is_valid():
            print("success")
            a = form.save(commit = False)
            a.save()
            messages.success(request, "Session Updated")
        else:
            messages.error(request, "cannot update session. Invalid info.")
        return redirect("mentor_session_add_url")
    
    context={'form':form}
    return render (request,"mentor/mentor_session_update.html", context)

@login_required(login_url="login_url")
@mentor_only
def mentor_session_list_func(request):
    if sessiontbl.objects.exists():
        templist = sessiontbl.objects.all()
        context = {'templist':templist}
        return render(request, 'mentor/mentor_session_list.html', context)
    else:
        if not sessiontbl.objects.exists():
            return render(request, 'mentor/mentor_session_list.html',)
    return render(request, 'mentor/mentor_session_list.html', context)


# --------------------- OTO report -------------------------------
@login_required(login_url="login_url")
@mentor_only
def oto_report_func(request):
    form = OtoReportForm

    context = {'form':form}
    return render(request, 'mentor/oto_report.html', context)


# ================================================ REPORTS ==============================================#
#***********************************user reports*******************************************

def userreports(request):
    roles=rolestbl.objects.all()
    if request.method == 'GET':
        query= request.GET.get('q')
        if query is None:
            query=""
        query2= request.GET.get('f')
        query3= request.GET.get('g')
        query4= request.GET.get('h')
        submitbutton= request.GET.get('done')
        form = UserEditForm()
        form2 = UserEditForm()
        myroles=list()
        depttot=depttbl.objects.all().count()
        coursetot=coursetbl.objects.all().count()
        roles = rolestbl.objects.all()
        rolescount=User.objects.values('roles','is_active').annotate(Count('roles')).order_by(('-roles__count'))
        rolescount2=User.objects.values('roles').annotate(Count('roles')).order_by(('-roles__count'))
        campus = campustbl.objects.all()
        campuscount=campustbl.objects.values('id','campus').annotate(Count('campus')).order_by(('-campus__count'))
        #print(campus)
        #print(campuscount)
        #print("list {}".format(roles))
        activeness = User.objects.all().values_list('is_active', flat=True).distinct()
        #print(activeness)
        user=User.objects.values('id','email','is_active','campus')
        maxuser=onetoonetickettbl.objects.values('accepted_by').annotate(Count('accepted_by')).order_by(('-accepted_by__count'))[:3]
        leastuser=onetoonetickettbl.objects.values('accepted_by').annotate(Count('accepted_by')).order_by(('accepted_by__count'))
        #print("user :\n\n{}\n\n\n maxusers :\n\n{}\n\n\n leastusers:{}".format(user,maxuser,leastuser))
        
        if query is not None and query2!="" and query3!="" and query4=="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  & Q(roles=query2) & Q(is_active=query3)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif query is not None and query2!="" and query3=="" and query4=="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  & Q(roles=query2) 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif query is not None and query2=="" and query3=="" and query4=="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif query is not None and query2=="" and query3!="" and query4=="":
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  & Q(is_active=query3)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)

        elif query ==""and query2=="" and query3!="" and query4=="":
            lookups=  Q(is_active=query3)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif query =="" and query2=="" and query3=="" and query4=="":
            
            results= User.objects.all()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}
            return render(request, 'mentor/userreports.html',context)
        elif query is not None and query2!="" and query3!="" and query4!="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  & Q(roles=query2) & Q(is_active=query3) & Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif not(query)  and query2=="" and query3=="" and query4!="":
            
            lookups=  Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}
            return render(request, 'mentor/userreports.html', context)
        elif query is not None and query2=="" and query3=="" and query4!="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  &  Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}
            return render(request, 'mentor/userreports.html', context)
        elif not(query) and query2!="" and query3=="" and query4!="":
            
            lookups=   Q(roles=query2) & Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif not(query) and query2=="" and query3!="" and query4!="":
            
            lookups=    Q(is_active=query3) & Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif query is not None and query2!="" and query3=="" and query4!="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  & Q(roles=query2) & Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif query is not None and query2=="" and query3!="" and query4!="":
            
            lookups=  ( Q(first_name=query) | Q(last_name=query) | Q(email=query) | Q(mobile=query) )  & Q(is_active=query3) & Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        elif not(query)  and query2!="" and query3!="" and query4!="":
            
            lookups=  Q(roles=query2) & Q(is_active=query3) & Q(campus=query4)
 
            results= User.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'roles':roles,'activeness':activeness,'roles':roles,'rolescount':rolescount,'maxuser':maxuser,'user':user,'leastuser':leastuser,'rolescount2':rolescount2,'campus':campus,'campuscount':campuscount,'depttot':depttot,'coursetot':coursetot}

            return render(request, 'mentor/userreports.html', context)
        else:
            return render(request, 'mentor/userreports.html')
     
    else:
        return render(request, 'mentor/userreports.html')

#***************************************************one to one reports ***************************

def peertopeerreports(request):

    if request.method == 'GET':

        query= request.GET.get('q')
        query2= request.GET.get('f')
        query3= request.GET.get('g')
        query4= request.GET.get('h')
        query5= request.GET.get('i')
        query6= request.GET.get('j')
        print(query6)
        submitbutton= request.GET.get('done')
        form = peergrouptickettbl()
        form2 = peergrouptickettbl()
        results=None
       
        campus=campustbl.objects.all()
        course=coursetbl.objects.all()
        session = sessiontbl.objects.all()
        department = depttbl.objects.all()
        testing=peergrouptickettbl._meta.get_field('ticket_status').choices
        
        #from django.db.models import Count
        maxsession=peergrouptickettbl.objects.values('session').annotate(Count('session')).order_by(('-session__count'))[:3]
        countcampus=peergrouptickettbl.objects.values('campus').annotate(Count('campus')).order_by(('-campus__count'))
        countdept=peergrouptickettbl.objects.values('dept').annotate(Count('dept')).order_by(('-dept__count'))
        countcourse=peergrouptickettbl.objects.values('course').annotate(Count('course')).order_by(('-course__count'))
        
        #from itertools import chain
        uniqueVal = tuple(set(chain.from_iterable(testing)))
        
        if query2!="" and not (query ) and (query3=="") and (query4=="") and (query5=="") and (query6==""):
            print("1")
            lookups=   Q(session=query2)
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)

        elif (query  is not None ) and  (query2=="" and query3=="" and query4=="" and query5=="" and (query6=="")) :
            print("2")
            #lookups=   Q(session=query)| Q(first_name=query) | Q(last_name=query) | Q(ticket_no=query) |  Q(facultyemail=query) | Q(assigned_by=query) | Q(accepted_by=query) | Q(mobile=query) | Q(assigned_to=query) | Q(rejected_by=query) 
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query is not None ) and query2!=""  and query3=="" and query4=="" and (query5=="") and (query6==""):
            print("3")
            #lookups=   Q(session=query)| Q(first_name=query) | Q(last_name=query) | Q(ticket_no=query) |  Q(facultyemail=query) | Q(assigned_by=query) | Q(accepted_by=query) | Q(mobile=query) | Q(assigned_to=query) | Q(rejected_by=query) 
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(session=query2)
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3!="" and query2!="" and (query4=="") and (query5=="") and (query6=="") and  not(query ):
            print("4")
            lookups=  (Q(session=query2)) & (Q(dept=query3))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3!="" and query2!="" and query4=="" and (query5=="") and (query6=="") and (query is not None):
            print("5")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & (Q(session=query2)) & (Q(dept=query3))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3!="" and (query2=="" ) and query4=="" and (query5=="") and (query6=="") and (not (query) ):
            print("6:")
            lookups=  (Q(dept=query3))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        
        elif query3!="" and (query2=="" ) and query4=="" and (query5=="") and (query6=="") and (query is not None ):
            print("7:")
            lookups=   (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &  (Q(dept=query3))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3!="" and query2!="" and query4!="" and (query5=="") and (query6=="") and (query is not None):
            print("8:")
            lookups=   (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &  (Q(session=query2)) & (Q(dept=query3)) & (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3!="" and query2=="" and query4!="" and (query5=="") and (query6=="") and not (query ):
            print("9")
            lookups=   (Q(dept=query3)) & (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3=="" and query2!="" and query4!="" and (query5=="") and (query6=="") and not(query):
            print("10")
            lookups=(Q(session=query2)) & (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif query3!="" and query2=="" and query4!="" and (query5=="") and (query6=="") and (query is not None):
            print("11")
            lookups=   (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &  (Q(dept=query3)) & (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}

            return render(request, 'mentor/peerreports.html', context)
        elif query4!="" and query3=="" and query2=="" and query5=="" and (not(query)):
            print("12")
            lookups= (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5=="") and (query6=="") and (query is not None):
            print("13")
            lookups=   (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &  (Q(session=query2)) & (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5=="") and (query6=="") and (query is not None):
            print("14")
            lookups=   (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &  (Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()           
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and not(query):
            print("15")
            lookups=  (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6=="") and not(query):
            print("16")
            lookups=  (Q(campus=query4)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and not(query):
            print("17")
            lookups=  (Q(dept=query3)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and not(query):
            print("18")
            lookups=  (Q(session=query2)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and (query is not None):
            print("18")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & (Q(course=query5))           
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6=="") and (query is not None):
            print("19")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &(Q(campus=query4)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and (query is not None):
            print("20")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &(Q(dept=query3)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and (query is not None):
            print("21")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) &(Q(session=query2)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and not(query ):
            print("22")
            lookups=  (Q(session=query2)) &(Q(dept=query3)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5!="") and (query6=="") and not(query ):
            print("23")
            lookups=  (Q(session=query2)) &(Q(campus=query4)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5!="") and (query6=="") and not(query ):
            print("24")
            lookups=  (Q(dept=query3)) &(Q(campus=query4)) & (Q(course=query5))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6=="") and not(query ):
            print("25")
            lookups=  (Q(dept=query3)) &(Q(campus=query4)) & (Q(course=query5)) &(Q(session=query2))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and  not(query ):
            print("33")
            lookups=  Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6)) &(Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)

        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query is not None ):
            print("26")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & (Q(dept=query3)) &(Q(campus=query4)) & (Q(course=query5)) &(Q(session=query2))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and (query is not None ):
            print("27")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & (Q(dept=query3))  & (Q(course=query5)) &(Q(session=query2))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and not (query ):
            print("28")
            lookups=  (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and (query is not None):
            print("29")
            lookups=  (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )  & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and not(query ):
            print("30")
            lookups=  Q(session=query2)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and not(query ):
            print("30")
            lookups=  Q(dept=query3)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and not(query ):
            print("31")
            lookups=  Q(campus=query4)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and not(query ):
            print("32")
            lookups=  Q(course=query5)& (Q(ticket_status=query6)) 
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        
        elif (query3=="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )& Q(session=query2)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        
        elif (query3!="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )& Q(dept=query3)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        
        elif (query3=="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )& Q(campus=query4)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )& Q(course=query5)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   )& Q(course=query5)& (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(dept=query3) & Q(session=query2) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(campus=query4) & Q(session=query2) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(course=query5) & Q(session=query2) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(campus=query4) & Q(dept=query3) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(course=query5) & Q(campus=query4) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(dept=query3) & Q(session=query2) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(campus=query4) & Q(session=query2) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(course=query5) & Q(session=query2) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(dept=query3) & Q(campus=query4) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(dept=query3) & Q(course=query5) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(campus=query4) & Q(course=query5) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(session=query2) & Q(campus=query4) & Q(dept=query3) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(session=query2) & Q(course=query5) & Q(campus=query4) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(dept=query3) & Q(course=query5) & Q(campus=query4) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(session=query2) & Q(campus=query4) & Q(dept=query3) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query)   ) & Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and  not (query ):
            print("33")
            lookups=  Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6)) &(Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  |  Q(facultyemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6)) &(Q(campus=query4))
            results= peergrouptickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/peerreports.html', context)



        context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}

        
        return render(request, 'mentor/peerreports.html',context)
     
    else:
        return render(request, 'mentor/peerreports.html')

#*****************************************group reports*********************************************



def onetoonereports(request):

    if request.method == 'GET':

        query= request.GET.get('q')
        query2= request.GET.get('f')
        query3= request.GET.get('g')
        query4= request.GET.get('h')
        query5= request.GET.get('i')
        query6= request.GET.get('j')
      
        """accepted_date"""
        print(query6)
        submitbutton= request.GET.get('done')
        form = onetoonetickettbl()
        form2 = onetoonetickettbl()
        results=None
       
        campus=campustbl.objects.all()
        course=coursetbl.objects.all()
        session = sessiontbl.objects.all()
        department = depttbl.objects.all()
        testing=onetoonetickettbl._meta.get_field('ticket_status').choices
        
        #from django.db.models import Count
        maxsession=onetoonetickettbl.objects.values('session').annotate(Count('session')).order_by(('-session__count'))[:3]
        countcampus=onetoonetickettbl.objects.values('campus').annotate(Count('campus')).order_by(('-campus__count'))
        countdept=onetoonetickettbl.objects.values('dept').annotate(Count('dept')).order_by(('-dept__count'))
        countcourse=onetoonetickettbl.objects.values('course').annotate(Count('course')).order_by(('-course__count'))
        
        #from itertools import chain
        uniqueVal = tuple(set(chain.from_iterable(testing)))
        
        
        if (query2!="" and not (query ) and (query3=="") and (query4=="") and (query5=="") and (query6=="") ) :
            print("1")
            lookups=   Q(session=query2)
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)

        elif (query  is not None ) and  (query2=="" and query3=="" and query4=="" and query5=="" and (query6=="")) :
            print("2")
            #lookups=   Q(session=query)| Q(first_name=query) | Q(last_name=query) | Q(ticket_no=query) | Q(stuemail=query) | Q(assigned_by=query) | Q(accepted_by=query) | Q(mobile=query) | Q(assigned_to=query) | Q(rejected_by=query) 
            lookups=  (Q(name=query)   | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query is not None ) and query2!=""  and query3=="" and query4=="" and (query5=="") and (query6==""):
            print("3")
            #lookups=   Q(session=query)| Q(first_name=query) | Q(last_name=query) | Q(ticket_no=query) | Q(stuemail=query) | Q(assigned_by=query) | Q(accepted_by=query) | Q(mobile=query) | Q(assigned_to=query) | Q(rejected_by=query) 
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(session=query2)
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3!="" and query2!="" and (query4=="") and (query5=="") and (query6=="") and  not(query ):
            print("4")
            lookups=  (Q(session=query2)) & (Q(dept=query3))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3!="" and query2!="" and query4=="" and (query5=="") and (query6=="") and (query is not None):
            print("5")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & (Q(session=query2)) & (Q(dept=query3))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3!="" and (query2=="" ) and query4=="" and (query5=="") and (query6=="") and (not (query) ):
            print("6:")
            lookups=  (Q(dept=query3))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        
        elif query3!="" and (query2=="" ) and query4=="" and (query5=="") and (query6=="") and (query is not None ):
            print("7:")
            lookups=   (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &  (Q(dept=query3))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3!="" and query2!="" and query4!="" and (query5=="") and (query6=="") and (query is not None):
            print("8:")
            lookups=   (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &  (Q(session=query2)) & (Q(dept=query3)) & (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3!="" and query2=="" and query4!="" and (query5=="") and (query6=="") and not (query ):
            print("9")
            lookups=   (Q(dept=query3)) & (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3=="" and query2!="" and query4!="" and (query5=="") and (query6=="") and not(query):
            print("10")
            lookups=(Q(session=query2)) & (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif query3!="" and query2=="" and query4!="" and (query5=="") and (query6=="") and (query is not None):
            print("11")
            lookups=   (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &  (Q(dept=query3)) & (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}

            return render(request, 'mentor/onetoonereports.html', context)
        elif query4!="" and query3=="" and query2=="" and query5=="" and (not(query)):
            print("12")
            lookups= (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5=="") and (query6=="") and (query is not None):
            print("13")
            lookups=   (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &  (Q(session=query2)) & (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5=="") and (query6=="") and (query is not None):
            print("14")
            lookups=   (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &  (Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()           
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and not(query):
            print("15")
            lookups=  (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6=="") and not(query):
            print("16")
            lookups=  (Q(campus=query4)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and not(query):
            print("17")
            lookups=  (Q(dept=query3)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and not(query):
            print("18")
            lookups=  (Q(session=query2)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and (query is not None):
            print("18")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & (Q(course=query5))           
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6=="") and (query is not None):
            print("19")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &(Q(campus=query4)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6=="") and (query is not None):
            print("20")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &(Q(dept=query3)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and (query is not None):
            print("21")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) &(Q(session=query2)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and not(query ):
            print("22")
            lookups=  (Q(session=query2)) &(Q(dept=query3)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5!="") and (query6=="") and not(query ):
            print("23")
            lookups=  (Q(session=query2)) &(Q(campus=query4)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5!="") and (query6=="") and not(query ):
            print("24")
            lookups=  (Q(dept=query3)) &(Q(campus=query4)) & (Q(course=query5))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6=="") and not(query ):
            print("25")
            lookups=  (Q(dept=query3)) &(Q(campus=query4)) & (Q(course=query5)) &(Q(session=query2))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and  not(query ):
            print("33")
            lookups=  Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6)) &(Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query is not None ):
            print("26")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & (Q(dept=query3)) &(Q(campus=query4)) & (Q(course=query5)) &(Q(session=query2))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6=="") and (query is not None ):
            print("27")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & (Q(dept=query3))  & (Q(course=query5)) &(Q(session=query2))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and not (query ):
            print("28")
            lookups=  (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and (query is not None):
            print("29")
            lookups=  (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )  & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and not(query ):
            print("30")
            lookups=  Q(session=query2)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and not(query ):
            print("30")
            lookups=  Q(dept=query3)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and not(query ):
            print("31")
            lookups=  Q(campus=query4)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and not(query ):
            print("32")
            lookups=  Q(course=query5)& (Q(ticket_status=query6)) 
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        
        elif (query3=="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )& Q(session=query2)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        
        elif (query3!="") and (query2=="") and (query4=="") and (query5=="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )& Q(dept=query3)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        
        elif (query3=="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )& Q(campus=query4)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )& Q(course=query5)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and (query is not None ):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) )& Q(course=query5)& (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(dept=query3) & Q(session=query2) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(campus=query4) & Q(session=query2) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(course=query5) & Q(session=query2) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(campus=query4) & Q(dept=query3) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(course=query5) & Q(campus=query4) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(dept=query3) & Q(session=query2) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(campus=query4) & Q(session=query2) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(course=query5) & Q(session=query2) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(dept=query3) & Q(campus=query4) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4=="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(dept=query3) & Q(course=query5) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2=="") and (query4!="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(campus=query4) & Q(course=query5) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(session=query2) & Q(campus=query4) & Q(dept=query3) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3=="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(session=query2) & Q(course=query5) & Q(campus=query4) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2=="") and (query4!="") and (query5!="") and (query6!="") and not (query ):
            print("33")
            lookups= Q(dept=query3) & Q(course=query5) & Q(campus=query4) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5=="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(session=query2) & Q(campus=query4) & Q(dept=query3) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4=="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and  not (query ):
            print("33")
            lookups=  Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6)) &(Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        elif (query3!="") and (query2!="") and (query4!="") and (query5!="") and (query6!="") and  (query is not None):
            print("33")
            lookups= (Q(name=query)  | Q(stuemail=query) | Q(mobile=query) | Q(ticket_no=query) | Q(regno=query) ) & Q(session=query2) & Q(course=query5) & Q(dept=query3) & (Q(ticket_status=query6)) &(Q(campus=query4))
            results= onetoonetickettbl.objects.filter(lookups).distinct()
            context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}
            return render(request, 'mentor/onetoonereports.html', context)
        


        context={'results': results,
                     'submitbutton': submitbutton,'form':form,'form2':form2,'session':session,'department':department,'countcampus':countcampus,'campus':campus,'countdept':countdept,'countcourse':countcourse,'course':course,'maxsession':maxsession,'uniqueVal':uniqueVal}

        
        return render(request, 'mentor/onetoonereports.html',context)
     
    else:
        return render(request, 'mentor/onetoonereports.html')

def twentyfourhours(request):
    form = profileaddform()
    temp = None
    Events=None
    if onetoonetickettbl.objects.exists():
        temp = onetoonetickettbl.objects.all()
    thetime = datetime.now() - timedelta(hours=24)
    results = onetoonetickettbl.objects.filter(Q(request_datetime__lte=thetime )& Q(ticket_status="requested" ))
    result = onetoonetickettbl.objects.filter(Q(request_datetime__lte=thetime )& Q(ticket_status="requested" )).values('ticket_no')
    print(result)
    context = {'temp':temp, 'form':form,'results':results}
    sub = profileaddform()
    
    mentors=rolestbl.objects.filter(roles='mentor').values('id')[0]
    dict(mentors)
    details=User.objects.filter(is_superuser=True )
    a=list(details)
    id=mentors.get('id')
    mentorslist=User.objects.filter(roles=id)
    a2=list(mentorslist)
    for i in range(0,len(a2)):
       a.append(a2[i])
    for i in range(0,len(a)):
       print("mentors and superadmins : {}".format(a[i]))
    #result are for ticket_no to and the below function is to convert the object into list
    b=list(result)
    twentyfourhoursdelay=list()
    for i in range(0,len(b)):
        twentyfourhoursdelay.append(b[i])
    string="please note that the following sessions are not assigned any volunteers and is in requested status : \n"
    for i in range(0,len(twentyfourhoursdelay)):
        string+=" "+str(twentyfourhoursdelay[i])+"\n"
        #print("string : "+string)
    print("string : "+string)
    
    if result is not None:
      for i in range(0,len(a)):
        send_mail('Response needed',string, settings.EMAIL_HOST_USER,[a[i]])
        print("sending mail")
    
    context = {'temp':temp, 'form':form,'results':results,'sub':sub}
    return render (request,"mentor/sendmail.html", context)



def feedback(request):
    if request.method == 'GET':
        N=8
        res = ''.join(random.choices(string.ascii_uppercase +string.digits, k = N))
        print("\n\n",res)
        with open('caps.txt', 'a+') as f:
          f.write(","+res)
        str=""
        str="our otp for feedback is "+res
        
        query= request.GET.get('q')
        query2= request.GET.get('f')
        query3=request.GET.get('g')
        query4=request.GET.get('feedback')
        submitbutton= request.GET.get('done')
        submitbutton2= request.GET.get('done2')
        feedback= request.GET.get('done3')
        lookups= Q(ticket_no=query2) & Q(stuemail=query)
        mentors=onetoonetickettbl.objects.filter(lookups).values('s_feedback').first()
        print("\n\nmentors :",mentors)
        if mentors:
            print("true")
        form = profileaddform()
        form2 = profileaddform()
        otps=list()
        stri=""
        with open('caps.txt') as f:
            line = f.readline()
            print(line)
            for line in line:
                stri+=line
        print(stri)
        
        
        i=0
        stri=""
        with open('caps.txt') as f:
            line = f.readline()
            print(line)
            for line in line:
                stri+=line
            # check if string present on a current line
        otps=stri.split(",")
        print(otps)
        p=0
        p={}
        if  query3 in otps:
            p=1
            with open('caps.txt', 'w') as f:
                f.write("     ")
                otps.clear()
                p={'id':1}
        
        elif submitbutton2 is not None:
            messages.success(request, 'IN-CORRECT OTP ')

        if feedback is not None:
            messages.error(request, 'SUBMITTED SUCCESFULLY')
       
        look= Q(ticket_no=query2) & Q(stuemail=query)
        studentfeedback=onetoonetickettbl.objects.filter(look).values('s_feedback').count()
        print("count : ",studentfeedback)
        if studentfeedback >0:
           if (query2 and query ) is not None:
             
              r= onetoonetickettbl.objects.get(ticket_no=query2)
              r.s_feedback=query4
              r.save()
           if (submitbutton is not None) and query and query2:
              messages.success(request, 'Check Your christ email and find the recent otp ')
        
        look= Q(ticket_no=query2) & Q(stuemail=query)
        studentfeedback=onetoonetickettbl.objects.filter(look).values('s_feedback')
        print("student feedback ",studentfeedback)
        lookups= Q(ticket_no=query2) & Q(stuemail=query) 
        results= onetoonetickettbl.objects.filter(lookups).values()
        if results:
            #send_mail('feedback otp',str, settings.EMAIL_HOST_USER, [query])
            print(otps)
            if len(otps)>0 :
                print("match")
                p={}
    
            else:
               print("mis")
               p={'id':1}
        else:
            return (render(request, 'mentor/feedback.html'))
        
        
        context={'results': results,'submitbutton': submitbutton,'submitbutton2': submitbutton2,'feedback':feedback,'form':form,'form2':form2,'p':p,'query3':query3}
        print(query4)
        return (render(request, 'mentor/feedback.html', context))

def volunteerreports(request):
    query= request.GET.get('q')
    print("\n\nquery : ",query)
    submitbutton= request.GET.get('done')
    results=None   
    users=User.objects.all()
    course=coursetbl.objects.all()
    session = sessiontbl.objects.all()
    department = depttbl.objects.all()
    activeness = User.objects.all().values()
    print("activeness: {}",activeness)
    #from django.db.models import Count
    maxsession=peergrouptickettbl.objects.values('session').annotate(Count('session')).order_by(('-session__count'))[:3]
    countcampus=peergrouptickettbl.objects.values('campus').annotate(Count('campus')).order_by(('-campus__count'))
    countdept=peergrouptickettbl.objects.values('dept').annotate(Count('dept')).order_by(('-dept__count'))
    countcourse=peergrouptickettbl.objects.values('course').annotate(Count('course')).order_by(('-course__count'))    
    #from itertools import chain
    #uniqueVal = tuple(set(chain.from_iterable(testing))) 
    lookups=  (Q(roles__roles="volunteer")) & (Q(email__iexact=query) | Q(first_name__iexact=query) | Q(last_name__iexact=query) | Q(mobile__iexact=query) )
    tempuser = User.objects.filter(lookups).first()
    print("temp user ",tempuser)
    
    lookups=  Q(roles="volunteer")
    getrolesid= rolestbl.objects.filter(lookups).all()
    #rolesid=getrolesid.get('id')
    print(getrolesid)
    """
    lookups=  Q(email=query) & Q(roles=rolesid)
    getuserid= User.objects.filter(lookups).values().first()
    print(getuserid)
    """

    #notclosed
    closedlookups=  (Q(accepted_by=tempuser))& ( ~Q(closed_date= None))
    results= onetoonetickettbl.objects.filter(closedlookups)
    print("is null :  ",results)
    #closed
    onprocesslookups=  Q(accepted_by=tempuser) & ( Q(closed_date=None) )
    result2= onetoonetickettbl.objects.filter(onprocesslookups).values()
    print("not null:  ",result2)
    #totalhours
    hourslookups=  Q(accepted_by=tempuser) 
    result3= onetoonetickettbl.objects.filter(hourslookups).aggregate(total=Sum('hours'))['total']
    print("hours :  ",result3)
    
    context={'results':results,'result2':result2,'result3':result3,'submitbutton':submitbutton,'tempuser':tempuser,'activeness':activeness}
    return render(request, 'mentor/volunteerreports.html',context )

def studentheadreports(request):
    query= request.GET.get('q')
    print("query : ",query)
    submitbutton= request.GET.get('done')
    results=None   
    users=User.objects.all()
    course=coursetbl.objects.all()
    session = sessiontbl.objects.all()
    department = depttbl.objects.all()
    activeness = User.objects.all().values()
    print("activeness: {}",activeness)
    #from django.db.models import Count
    maxsession=peergrouptickettbl.objects.values('session').annotate(Count('session')).order_by(('-session__count'))[:3]
    countcampus=peergrouptickettbl.objects.values('campus').annotate(Count('campus')).order_by(('-campus__count'))
    countdept=peergrouptickettbl.objects.values('dept').annotate(Count('dept')).order_by(('-dept__count'))
    countcourse=peergrouptickettbl.objects.values('course').annotate(Count('course')).order_by(('-course__count'))    
    #from itertools import chain
    #uniqueVal = tuple(set(chain.from_iterable(testing))) 
    lookups=  (Q(roles__roles="studenthead")) & (Q(email__iexact=query) | Q(first_name__iexact=query) | Q(last_name__iexact=query) | Q(mobile__iexact=query) ) 
    tempuser = User.objects.filter(lookups).first()
    print("temp user ",tempuser)
    
    lookups=  Q(roles="studenthead")
    getrolesid= rolestbl.objects.filter(lookups).all()
    #rolesid=getrolesid.get('id')
    print(getrolesid)
    """
    lookups=  Q(email=query) & Q(roles=rolesid)
    getuserid= User.objects.filter(lookups).values().first()
    print(getuserid)
    """
    if query is not None:
    #notclosed
      closedlookups=  (Q(accepted_by=tempuser) &  ~(Q(closed_date= None)) )
      results= onetoonetickettbl.objects.filter(closedlookups)
      resultscount= onetoonetickettbl.objects.filter(closedlookups).count()
      print("is null :  ",results)
      #closed
      onprocesslookups=  Q(accepted_by=tempuser) & ( Q(closed_date=None) )
      result2= onetoonetickettbl.objects.filter(onprocesslookups)
      results2count= onetoonetickettbl.objects.filter(onprocesslookups).values().count()
      print("not null:  ",result2)
      #totalhours
      hourslookups=  Q(accepted_by=tempuser) 
      result3= onetoonetickettbl.objects.filter(hourslookups).aggregate(total=Sum('hours'))['total']
      results3count= onetoonetickettbl.objects.filter(closedlookups).count()
      print("hours :  ",result3)
    
      print("hours :  ",result3)
      context={'results':results,'activeness':activeness ,'result2':result2,'result3':result3,'submitbutton':submitbutton,'tempuser':tempuser,'resultscount':resultscount,'results2count':results2count,'results3count':results3count}
      return render(request, 'mentor/studentheadreports.html',context )
    context={'activeness':activeness ,'submitbutton':submitbutton}
      
    return render(request, 'mentor/studentheadreports.html',context )


def sessions(request):
    session = sessiontbl.objects.all()
    users=User.objects.all().values()
    print("\n\nusers \n\n",users)
    closedandfeedback=  ( ~Q(closed_date= None)) & ( ~Q(s_feedback= ""))
    result= onetoonetickettbl.objects.filter(closedandfeedback).values().all()
    resultcount= onetoonetickettbl.objects.filter(closedandfeedback).values().all().count()
    print("\nresults   ",result)
    closedandnofeedback=  ( ~Q(closed_date= None)) & ( Q(s_feedback= ""))
    results2= onetoonetickettbl.objects.filter(closedandnofeedback).values().all()
    results2count= onetoonetickettbl.objects.filter(closedandnofeedback).values().all().count()
    print("\n\nresults   ",results2count)

    context={'result':result,'results2':results2,'session':session,'users':users,'resultcount':resultcount,'results2count':results2count}
    return render(request, 'mentor/sessions.html',context)


def sessions_group(request):
    session = sessiontbl.objects.all()
    users=User.objects.all().values()
    print("users : ",users)
    print("\n\nusers \n\n",users)
    closedandfeedback=  ( ~Q(closed_date= None)) & ( ~Q(s_feedback= ""))
    result= peergrouptickettbl.objects.filter(closedandfeedback)
    resultcount= peergrouptickettbl.objects.filter(closedandfeedback).values().all().count()
    print("\nresults   ",result)
    closedandnofeedback=  ( ~Q(closed_date= None)) & ( Q(s_feedback= ""))
    results2= peergrouptickettbl.objects.filter(closedandnofeedback)
    results2count= peergrouptickettbl.objects.filter(closedandnofeedback).values().all().count()
    print("\n\nresults2   ",results2)

    context={'result':result,'results2':results2,'session':session,'users':users,'resultcount':resultcount,'results2count':results2count}
    return render(request, 'mentor/sessions_group.html',context)



def group_volunteerreports(request):
    query= request.GET.get('q')
    print("\n\nquery : ",query)
    submitbutton= request.GET.get('done')
    results=None   
    users=User.objects.all()
    course=coursetbl.objects.all()
    session = sessiontbl.objects.all()
    department = depttbl.objects.all()
    activeness = User.objects.all().values()
    print("activeness: {}",activeness)
    #from django.db.models import Count
    maxsession=peergrouptickettbl.objects.values('session').annotate(Count('session')).order_by(('-session__count'))[:3]
    countcampus=peergrouptickettbl.objects.values('campus').annotate(Count('campus')).order_by(('-campus__count'))
    countdept=peergrouptickettbl.objects.values('dept').annotate(Count('dept')).order_by(('-dept__count'))
    countcourse=peergrouptickettbl.objects.values('course').annotate(Count('course')).order_by(('-course__count'))    
    #from itertools import chain
    #uniqueVal = tuple(set(chain.from_iterable(testing))) 
    lookups=  (Q(roles__roles="volunteer")) & (Q(email__iexact=query) | Q(first_name__iexact=query) | Q(last_name__iexact=query) | Q(mobile__iexact=query) )
    tempuser = User.objects.filter(lookups).first()
    print("temp user ",tempuser)
    print("\n")
    print("\n")
    
    lookups=  Q(roles="volunteer")
    getrolesid= rolestbl.objects.filter(lookups).all()
    #rolesid=getrolesid.get('id')
    print(getrolesid)
    """
    lookups=  Q(email=query) & Q(roles=rolesid)
    getuserid= User.objects.filter(lookups).values().first()
    print(getuserid)
    """

    #notclosed
    closedlookups=  (Q(accepted_by=tempuser))& ( ~Q(closed_date= None))
    results= peergrouptickettbl.objects.filter(closedlookups)
    print("is null :  ",results)
    print("\n")
    print("\n")
    #closed
    onprocesslookups=  Q(accepted_by=tempuser) & ( Q(closed_date=None) )
    result2= peergrouptickettbl.objects.filter(onprocesslookups).values()
    print("not null:  ",result2)
    print("\n")
    print("\n")

    #totalhours
    hourslookups=  Q(accepted_by=tempuser) 
    result3= peergrouptickettbl.objects.filter(hourslookups).aggregate(total=Sum('hours'))['total']
    print("hours :  ",result3)
    print("\n")
    print("\n")
    context={'results':results,'result2':result2,'result3':result3,'submitbutton':submitbutton,'tempuser':tempuser,'activeness':activeness}
    return render(request, 'mentor/group_volunteerreports.html',context )

def group_studentheadreports(request):
    query= request.GET.get('q')
    print("query : ",query)
    submitbutton= request.GET.get('done')
    results=None   
    users=User.objects.all()
    course=coursetbl.objects.all()
    session = sessiontbl.objects.all()
    department = depttbl.objects.all()
    activeness = User.objects.all().values()
    print("activeness: {}",activeness)
    #from django.db.models import Count
    maxsession=peergrouptickettbl.objects.values('session').annotate(Count('session')).order_by(('-session__count'))[:3]
    countcampus=peergrouptickettbl.objects.values('campus').annotate(Count('campus')).order_by(('-campus__count'))
    countdept=peergrouptickettbl.objects.values('dept').annotate(Count('dept')).order_by(('-dept__count'))
    countcourse=peergrouptickettbl.objects.values('course').annotate(Count('course')).order_by(('-course__count'))    
    #from itertools import chain
    #uniqueVal = tuple(set(chain.from_iterable(testing))) 
    lookups=  (Q(roles__roles="studenthead")) & (Q(email__iexact=query) | Q(first_name__iexact=query) | Q(last_name__iexact=query) | Q(mobile__iexact=query) ) 
    tempuser = User.objects.filter(lookups).first()
    print("temp user ",tempuser)
    
    lookups=  Q(roles="studenthead")
    getrolesid= rolestbl.objects.filter(lookups).all()
    #rolesid=getrolesid.get('id')
    print(getrolesid)
    """
    lookups=  Q(email=query) & Q(roles=rolesid)
    getuserid= User.objects.filter(lookups).values().first()
    print(getuserid)
    """
    if query is not None:
    #notclosed
      closedlookups=  Q(accepted_by=tempuser) &  ~Q(closed_date= None )
      results= peergrouptickettbl.objects.filter(closedlookups)
      resultscount= peergrouptickettbl.objects.filter(closedlookups).count()
      print("is null :  ",results)
      #closed
      onprocesslookups=  Q(accepted_by=tempuser) & ( Q(closed_date=None) )
      result2= peergrouptickettbl.objects.filter(onprocesslookups)
      results2count= peergrouptickettbl.objects.filter(onprocesslookups).values().count()
      print("not null:  ",result2)
      #totalhours
      hourslookups=  Q(accepted_by=tempuser) 
      result3= peergrouptickettbl.objects.filter(hourslookups).aggregate(total=Sum('hours'))['total']
      results3count= peergrouptickettbl.objects.filter(closedlookups).count()
      print("hours :  ",result3)
    
      print("hours :  ",result3)
      context={'results':results,'activeness':activeness ,'result2':result2,'result3':result3,'submitbutton':submitbutton,'tempuser':tempuser,'resultscount':resultscount,'results2count':results2count,'results3count':results3count}
      return render(request, 'mentor/group_studentheadreports.html',context )
    context={'activeness':activeness ,'submitbutton':submitbutton}
      
    return render(request, 'mentor/group_studentheadreports.html',context )

# ------------------ OTO reports new ---------------------
def oto_report_func(request):

    tempoto = onetoonetickettbl.objects.all()

    otofilter = OtoFilter(request.GET, queryset=tempoto)

    tempoto = otofilter.qs

    sessionlist = tempoto.values('session__session').annotate(total = Count('session__session')).order_by('total')
    deptlist = tempoto.values('dept__dept').annotate(total = Count('dept__dept')).order_by('total')

    context ={"otofilter":otofilter, "tempoto":tempoto, "sessionlist":sessionlist, "deptlist":deptlist}
    return render(request,"mentor/oto_report.html", context)

# ------------------ group session reports new ---------------------
def grp_report_func(request):

    tempgrp = peergrouptickettbl.objects.all()

    grpfilter = GroupFilter(request.GET, queryset=tempgrp)

    tempgrp = grpfilter.qs

    sessionlist = tempgrp.values('session__session').annotate(total = Count('session__session')).order_by('total')
    deptlist = tempgrp.values('dept__dept').annotate(total = Count('dept__dept')).order_by('total')

    print(tempgrp)
    context ={"grpfilter":grpfilter, "tempgrp":tempgrp,"sessionlist":sessionlist, "deptlist":deptlist}
    return render(request,"mentor/group_report.html", context)

# ------------------ User report view-----------------------
def user_report_gen_func(request,pkid):
    tempuser = User.objects.filter(id=pkid).first()
    tempvol = stuhead_vol_profiletbl.objects.filter(user=tempuser).first()

    otoacclist = onetoonetickettbl.objects.filter(accepted_by = tempuser,ticket_status="closed")
    otoasglist = onetoonetickettbl.objects.filter(assigned_by = tempuser,ticket_status="closed")

    grpacclist = peergrouptickettbl.objects.filter(accepted_by = tempuser,ticket_status="closed")
    grpasglist = peergrouptickettbl.objects.filter(assigned_by = tempuser,ticket_status="closed")

    print(otoacclist)
  
    context = {
        'tempvol':tempvol,
        'otoacclist':otoacclist,
        'otoasg_list':otoasglist,
        'grpacclist':grpacclist,
        'grpasglist':grpasglist,
         }
    return render(request,"mentor/user_report_gen.html", context)

# ------------------- USer stat reports --------------------------
def user_report_func(request):
    tempuser = User.objects.all()
    userfilter = UserFilter(request.GET, queryset=tempuser)
    tempuser = userfilter.qs

    context = {'userfilter':userfilter, 'tempuser':tempuser}
    return render(request,"mentor/user_report.html",context)

# ------------------- User search and generate report ------------
# def user_search_func(request):
#     form = UserSearchForm

#     if request.method == 'POST':
#         tempkey = request.POST.get('search_key')
#         lookup = (Q(email__icontains=tempkey) or Q(first_name__iconatins=tempkey) or Q(mobile__icontains=tempkey))
#         templist = User.objects.filter(lookup).first()
        

#     context = {'form':form}
#     return render(request,"mentor/user_search.html", context)