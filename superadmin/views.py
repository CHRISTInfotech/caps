from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError

from accounts.models import rolestbl,campustbl,depttbl,coursetbl,User,stuhead_vol_profiletbl
from accounts.models import onetoonetickettbl, peergrouptickettbl
# from accounts.forms import OtoVolFeedbackForm, GroupVolFeedbackForm, OtoAssignForm, GroupAssignForm, GroupAssignForm2
# from accounts.forms import UserAddForm, VolunteerAddForm, UserEditForm, VolunteerEditForm
from accounts.forms import *
from accounts.decorators import  superadmin_only, studenthead_only, volunteer_only, mentor_only, unauthenticated_user

import datetime


from django.urls import reverse
from django.utils.encoding import uri_to_iri
import urllib
import random, string

# for sending html template through email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
#-------superadmin dashboard views--------

@login_required(login_url="login_url")
@superadmin_only
def sa_dashboard_func(request):
    

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
    }
    
    return render(request, 'superadmin/sa_dashboard.html', context)

@login_required(login_url='login_url')
@superadmin_only
def sa_mentor_list_func(request):
    if User.objects.exists():
        li = User.objects.all()
        print(li)
        templist=User.objects.filter(roles__roles='mentor')
        print(templist)
        context = {'templist':templist}
        return render(request, 'superadmin/sa_mentor_list.html', context)
    else:
        messages.error(request,"Unable to fetch data! sorry!")
        return render(request, 'superadmin/sa_mentor_list.html')

@login_required(login_url='login_url')
@superadmin_only
def sa_mentor_add_func(request):
    form1 = UserAddForm

    if request.method == "POST":
        form1 = UserAddForm(request.POST)

        if form1.is_valid():
            tempuser = form1.save(commit=False)
            tempuser.roles = rolestbl.objects.filter(roles = 'mentor').first()
            print(tempuser.roles)
            pwd = tempuser.password
            print(pwd)
            tempuser.save()
            pwd = form1.cleaned_data['password1']
            print(pwd)
            
            # send email code with pwd and username to the registered email adress
            subject ="CAPS Registration"
            html_message = render_to_string('emailtemplates/email_registration.html', {'tempuser': tempuser,"pwd":pwd})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [tempuser.email]
            send_mail( subject, plain_message, email_from, email_to ,html_message=html_message,fail_silently=True)
            
            messages.success(request, "mentor registered successfully")
            return redirect("sa_mentor_list_url")
        else:
            print(form1.errors)
            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,}
    return render(request, 'superadmin/sa_mentor_add.html',context)

@login_required(login_url='login_url')
@superadmin_only
def sa_mentor_update_func(request, pkid):
    record1=User.objects.get(id=pkid)
    
    form1 = UserEditForm(instance=record1)
    
    if request.method == "POST":
        form1 = UserEditForm(request.POST,instance=record1)
        

        if form1.is_valid():
            tempuser = form1.save(commit=False)
            tempuser.roles = rolestbl.objects.filter(roles = 'mentor').first()
            print(tempuser.roles)
            tempuser.save()
            messages.success(request,"Mentor details updated successfully!")
            return redirect("sa_mentor_list_url")

        else:
            print(form1.errors)

            messages.error(request, "Invalid data! please check the form.")

    context = {"form1":form1,}
    return render(request, 'superadmin/sa_mentor_update.html',context)

@login_required(login_url='login_url')
@superadmin_only
def set_user_inactive_mentor_func(request,pkid):
    tempuser=User.objects.filter(id=pkid).first()
    tempuser.is_active=False
    tempuser.save()
    messages.success(request, "Mentor is inactive")
    return redirect('sa_mentor_list_url')

@login_required(login_url='login_url')
@superadmin_only
def set_user_active_mentor_func(request,pkid):
    tempuser=User.objects.filter(id=pkid).first()
    tempuser.is_active=True
    tempuser.save()
    messages.success(request, "Mentor is active")
    return redirect('sa_mentor_list_url')

#---------------------------------------------------campus views-----------------------------------------------------------------
@login_required(login_url='login_url')
@superadmin_only
def campusaddformfunc(request):
    form =campusaddform()
    templist = None
    if campustbl.objects.exists():
        templist = campustbl.objects.all()
    
    context = {'templist':templist, 'form':form}
    if request.method == "POST":
        form = campusaddform(request.POST)
        if form.is_valid():
            messages.success(request, "form saved")
            a = form.save(commit = False)
            a.save()
            form = campusaddform()
        else:
            messages.error(request, "cannot add campus. Invalid information.")

    return render (request,"superadmin/sa_campus_add.html", context)

@login_required(login_url='login_url')
@superadmin_only
def campusdeletefunc(request, pkid):
    record=campustbl.objects.get(id=pkid)
    print(record)
    try:
        record.delete()
    except ProtectedError as e:
        messages.error(request,"Cannot delete Campus!")
        return redirect("sa_session_add_url")
    messages.success(request, "record deleted")
    return redirect("sa_campus_add_url")

@login_required(login_url='login_url')
@superadmin_only
def campusupdatefunc(request, pkid):
    record=campustbl.objects.get(id=pkid)
    form = campusaddform(instance=record)
    if request.method == "POST":
        form = campusaddform(request.POST,instance=record)
        if form.is_valid():
            messages.success(request, "form saved")
            print("success")
            a = form.save(commit = False)
            a.save()
            messages.success(request, "Campus form saved")
        else:
            messages.error(request, "cannot update campus. Invalid info.")
        return redirect("sa_campus_add_url")
    
    context={'form':form}
    return render (request,"superadmin/sa_campus_update.html", context)

@login_required(login_url='login_url')
@superadmin_only
def campuslistfunc(request):
    if campustbl.objects.exists():
        templist = campustbl.objects.all()
        context = {'templist':templist}
        return render(request, 'superadmin/sa_campus_list.html', context)
    else:
        if not campustbl.objects.exists():
            return render(request, 'superadmin/sa_campus_list.html',)
    return render(request, 'superadmin/sa_campus_list.html', context)

#--------------------------------------------------- Department  views-----------------------------------------------------------------
@login_required(login_url='login_url')
@superadmin_only
def deptaddformfunc(request):
    form =deptaddform()
    templist=None
    if depttbl.objects.exists():
        templist = depttbl.objects.all()
    
    context = {'templist':templist, 'form':form}
    if request.method == "POST":
        form = deptaddform(request.POST)
        if form.is_valid():
            messages.success(request, "form saved")
            a = form.save(commit = False)
            a.save()
            form = deptaddform()
        else:
            messages.error(request, "cannot add dept. Invalid information.")
        
        return redirect("sa_dept_add_url")
    return render (request,"superadmin/sa_dept_add.html", context)

@login_required(login_url='login_url')
@superadmin_only
def deptdeletefunc(request, pkid):
    record=depttbl.objects.get(id=pkid)
    print(record)
    try:
        record.delete()
    except ProtectedError as e:
        messages.error(request,"Cannot delete Department.")
        return redirect("sa_session_add_url")
    messages.success(request, "record deleted")
    return redirect("sa_dept_add_url")

@login_required(login_url='login_url')
@superadmin_only
def deptupdatefunc(request, pkid):
    record=depttbl.objects.get(id=pkid)
    form = deptaddform(instance=record)
    if request.method == "POST":
        form = deptaddform(request.POST,instance=record)
        if form.is_valid():
            messages.success(request, "form saved")
            print("success")
            a = form.save(commit = False)
            a.save()
            messages.success(request, "Department got updated")
        else:
            messages.error(request, "cannot update department. Invalid info.")
        return redirect("sa_dept_add_url")
    
    context={'form':form}
    return render (request,"superadmin/sa_dept_update.html", context)

@login_required(login_url='login_url')
@superadmin_only
def deptlistfunc(request):
    if depttbl.objects.exists():
        templist = depttbl.objects.all()
        context = {'templist':templist}
        return render(request, 'superadmin/sa_dept_list.html', context)
    else:
        if not depttbl.objects.exists():
            return render(request, 'superadmin/sa_dept_list.html',)
    return render(request, 'superadmin/sa_dept_list.html', context)

#--------------------------------------------------- Course  views-----------------------------------------------------------------
@login_required(login_url='login_url')
@superadmin_only
def courseaddformfunc(request):
    form =courseaddform()
    templist = None
    if coursetbl.objects.exists():
        templist = coursetbl.objects.all()
    
    context = {'templist':templist, 'form':form}
    if request.method == "POST":
        form = courseaddform(request.POST)
        if form.is_valid():
            messages.success(request, "form saved")
            a = form.save(commit = False)
            a.save()
            form = courseaddform()
        else:
            messages.error(request, "cannot add course. Invalid information.")

    return render (request,"superadmin/sa_course_add.html", context)

@login_required(login_url='login_url')
@superadmin_only
def coursedeletefunc(request, pkid):
    record=coursetbl.objects.get(id=pkid)
    print(record)
    record.delete()
    messages.success(request, "record deleted")
    return redirect("superadmin/sa_course_add_url")

@login_required(login_url='login_url')
@superadmin_only
def courseupdatefunc(request, pkid):
    record=coursetbl.objects.get(id=pkid)
    form = courseaddform(instance=record)
    if request.method == "POST":
        form = courseaddform(request.POST,instance=record)
        if form.is_valid():
            messages.success(request, "form saved")
            print("success")
            a = form.save(commit = False)
            a.save()
            messages.success(request, "manga form saved")
        else:
            messages.error(request, "cannot update department. Invalid info.")
        return redirect("sa_course_add_url")
    
    context={'form':form}
    return render (request,"superadmin/sa_course_update.html", context)


@login_required(login_url="login_url")
@superadmin_only
def courselistfunc(request):
    if coursetbl.objects.exists():
        templist = coursetbl.objects.all()
        context = {'templist':templist}
        return render(request, 'superadmin/sa_course_list.html', context)
    else:
        if not coursetbl.objects.exists():
            return render(request, 'superadmin/sa_course_list.html',)
    return render(request, 'superadmin/sa_course_list.html', context)

#---------------------------------------------------SESSION views-----------------------------------------------------------------

#--------------------------------session list
@login_required(login_url="login_url")
@superadmin_only
def sa_session_add_func(request):
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
    return render (request,"superadmin/sa_session_add.html", context)

@login_required(login_url="login_url")
@superadmin_only
def sa_session_delete_func(request, pkid):
    record=sessiontbl.objects.get(id=pkid)
    print(record)
    try:
        record.delete()
    except ProtectedError as e:
        messages.error(request,"Cannot delete Sessions.")
        return redirect("sa_session_add_url")
    messages.success(request, "Session deleted")
    return redirect("sa_session_add_url")



@login_required(login_url="login_url")
@superadmin_only
def sa_session_update_func(request, pkid):
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
        return redirect("sa_session_add_url")
    
    context={'form':form}
    return render (request,"superadmin/sa_session_update.html", context)

@login_required(login_url="login_url")
@superadmin_only
def sa_session_list_func(request):
    if sessiontbl.objects.exists():
        templist = sessiontbl.objects.all()
        context = {'templist':templist}
        return render(request, 'superadmin/sa_session_list.html', context)
    else:
        if not sessiontbl.objects.exists():
            return render(request, 'superadmin/sa_session_list.html',)
    return render(request, 'superadmin/sa_session_list.html', context)



# 9 ---------------------- Superadmin grouplist function
@login_required(login_url="login_url")
@superadmin_only
def sa_group_list_func(request):
    reqlist = asglist = acclist = rejectlist = worklist = closedlist = halfasglist =  None
 
    reqlist = peergrouptickettbl.objects.filter(ticket_status = 'requested')
    asglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned')
    acclist = peergrouptickettbl.objects.filter(ticket_status = 'accepted')
    rejectlist = peergrouptickettbl.objects.filter(ticket_status = 'rejected')
    # need to work for half assigned list by chaning filters
    halfasglist = peergrouptickettbl.objects.filter(ticket_status = 'assigned', assigned_count__lt=3)
    worklist = peergrouptickettbl.objects.filter(ticket_status = 'work-in-progress')
    closedlist = peergrouptickettbl.objects.filter(ticket_status = 'closed')

    context = {
    "reqlist":reqlist,
    "asglist":asglist,
    "acclist":acclist,
    "rejectlist":rejectlist,
    "halfasglist":halfasglist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'superadmin/sa_group_list.html', context)

# 10 --------------------------- Superadmin - oto list view
@login_required(login_url="login_url")
@superadmin_only
def sa_oto_list_func(request):
    reqlist = asglist = acclist = rejectlist = worklist = closedlist =  None
    
    reqlist = onetoonetickettbl.objects.filter(ticket_status = 'requested')
    asglist = onetoonetickettbl.objects.filter(ticket_status = 'assigned')
    acclist = onetoonetickettbl.objects.filter(ticket_status = 'accepted')
    rejectlist = onetoonetickettbl.objects.filter(ticket_status = 'rejected')
    worklist = onetoonetickettbl.objects.filter(ticket_status = 'work-in-progress')
    closedlist = onetoonetickettbl.objects.filter(ticket_status = 'closed')
    
    context = {
    "reqlist":reqlist,
    "asglist":asglist,
    "acclist":acclist,
    "rejectlist":rejectlist,
    "worklist":worklist,
    "closedlist":closedlist,
    }
    return render(request, 'superadmin/sa_oto_list.html', context)


    
# ------------------------ superadmin oto details list
def sa_oto_detail_func(request,pkid):
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()
    context={"tempoto":tempoto}
    return render(request,"superadmin/sa_oto_details.html", context)

# ------------------------ superadmin oto details list
def sa_grp_detail_func(request,pkid):
    tempgrp = peergrouptickettbl.objects.filter(id=pkid).first()
    context={"tempgrp":tempgrp}
    return render(request,"superadmin/sa_group_details.html", context)



# # 11 ----------------------------- Mentor - group volunteer assign function
# @login_required(login_url="login_url")
# @superadmin_only
# def sa_group_assign_func(request, pkid):
#     record = peergrouptickettbl.objects.filter(id=pkid).first()
#     userlist = User.objects.filter(is_active=True, roles=3)
#     context = {'userlist':userlist}
#     print(userlist)
#     if request.method=="POST":
#         v1 = request.POST.get('vol1')
#         v2 = request.POST.get('vol2')
#         v3 = request.POST.get('vol3')
#         v4 = request.POST.get('vol4')
        
#         if not( v1 and v2 and v3 and v4):
#             messages.error(request,"Minimum 4 volunteers are required !")
#             return render(request,'superadmin/sa_group_assign_form.html',context)

#         vlist = [v1,v2,v3, v4]
#         print(vlist)
#         if(len(set(vlist)) == len(vlist)):
#             print("All elements are unique.")
#         else:
#             print("All elements are not unique.")
#             messages.error(request,"Select unique Volunteers!")
#             return render(request,'superadmin/sa_group_assign_form.html',context)

#         for each in vlist:
#             if each != record.assigned_to:
#                 record.assigned_to.add(each)
#                 record.assigned_count = record.assigned_count + 1;
                
#         record.ticket_status = "assigned"
#         record.assigned_by = request.user
#         record.save()
#         return redirect('sa_group_list_url')

#     context = {'userlist':userlist}
#     return render(request,'superadmin/sa_group_assign_form.html',context)


# # 12 ------------------------------ Mentor - oto assign function
# @login_required(login_url="login_url")
# @superadmin_only
# def mentor_oto_assign_func(request, pkid):
#     temp = onetoonetickettbl.objects.filter(id = pkid).first()
#     form = OtoAssignForm(instance=temp)

#     if request.method == "POST":
#         form = OtoAssignForm(request.POST)
#         if form.is_valid():
#             tempform = form.save(commit=False)
#             tempuseremail = form.cleaned_data.get('assigned_to')
#             tempuser = User.objects.filter(email=tempuseremail).first()
#             tempvol = stuhead_vol_profiletbl.objects.filter(user = tempuser).first()

#             print(temp.rejected_by)
#             if tempuser == temp.rejected_by:
#                 messages.error(request,"The volunteer has already rejected this booking")
#                 context = {"form":form}
#                 return render(request,"superadmin/sa_oto_assignform.html", context)

#             if tempvol is None:
#                 messages.error(request,"The volunteer doesn't belong to the same campus of the request.")
#                 context = {"form":form}
#                 return render(request,"superadmin/sa_oto_assignform.html", context)

#             if tempvol.campus != temp.campus:
#                 messages.error(request,"The volunteer doesn't belong to the same campus of the request.")
#                 context = {"form":form}
#                 return render(request,"superadmin/sa_oto_assignform.html", context)
#             else:
#                 temp.ticket_status = "assigned"
#                 temp.assigned_to = tempuser
#                 temp.assigned_by = request.user
#                 temp.save(update_fields=['assigned_to'])
#                 #send email to volunteer who has been assigned
#                 messages.success(request,"The request has been assigned to "+str(tempform.assigned_to))
#                 return redirect("sa_oto_list_url")
            
#     context = {"form":form}
#     return render(request,"superadmin/sa_oto_assignform.html", context)
