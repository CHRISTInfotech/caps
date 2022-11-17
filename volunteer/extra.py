# 12 --------------------------- studenthead - my oto accept view ---------------------->
def sh_my_oto_accept_func(request,pkid):

    tempoto = onetoonetickettbl.objects.filter(id = pkid, ticket_status = "assigned").first();
    print(tempoto)
    tempoto.ticket_status = "accepted"
    tempoto.accepted_date = datetime.datetime.now()  
    tempoto.accepted_by = request.user
    tempoto.save()

    # send email to requested user, all the mentors, and to the assigned student head
    return redirect('sh_dashboard_url')

# 13 --------------------------- studenthead oto reject view
def sh_my_oto_reject_func(request,pkid):

    tempoto = onetoonetickettbl.objects.filter(id = pkid, ticket_status = "assigned").first();
    print(tempoto)
    tempoto.rejected_by.add(request.user)
    # test this function
    tempoto.ticket_status = "rejected"
    tempoto.assigned_to = None
    tempoto.save()

    # send email to requested user, all the mentors, and to the assigned student head
    return redirect('sh_dashboard_url')

# 14 --------------------------- studenthead oto workinprogress view
def sh_my_oto_work_func(request,pkid):

    tempoto = onetoonetickettbl.objects.filter(id = pkid, ticket_status = "accepted").first();
    print(tempoto)
    tempoto.ticket_status = "work-in-progress"
    tempoto.save()
    # send email to requested user, all the mentors, and to the assigned student head
    return redirect('sh_dashboard_url')

# 15 --------------------------- studenthead oto closed view
def sh_my_oto_feedback_func(request,pkid):
    form = OtoVolFeedbackForm
    tempoto = onetoonetickettbl.objects.filter(id=pkid).first()
    print(pkid)
    if request.method == 'POST':
        form = OtoVolFeedbackForm(request.POST, instance = tempoto)
        if form.is_valid():
            tempform = form.save(commit=False)
            tempform.s_feedback = form.cleaned_data.get('s_feedback')
            tempform.save()

            messages.success(request,"Feedback submited successfully")
            # tempoto = onetoonetickettbl.objects.filter(id=pkid, ticket_status="accepted").first();
            print(tempoto)
        
            tempoto.ticket_status = "closed"
            tempoto.closed_date = datetime.datetime.now()
            tempoto.save()

        # send email to requested user, all the mentors, and to the assigned student head

            # send email code with pwd and OTP and link to login page
            subject = 'CAPS session update'
            message = 'Hello, The requested session is closed by the volunteer. Hope you had a wonderful learning experience! Thankyou for choosing our CAPS sessions!'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [tempoto.stuemail]
            send_mail( subject, message, email_from, recipient_list )
            return redirect('sh_dashboard_url')

    context = {"form":form}
    return render(request,'studenthead/sh_my_oto_feedback.html', context)


