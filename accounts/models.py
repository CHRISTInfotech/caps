from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError

from .managers import UserManager

import re
import datetime

from_date = datetime.datetime(2019, 10, 21)

to_date   = datetime.datetime(2019, 10, 25)

result = to_date - from_date
print(result.days)
#-------------------------------------------- Validations ---------------------
def validate_fname(value):
    if re.match(r'^[A-Za-z]{1,30}$', value):
        return True
    else:
        raise ValidationError('Enter Valid First name')

def validate_lname(value):
    if re.match(r'^([A-Za-z]{1,30}[ ]{1}|[A-Za-z]{1,30})*$', value):
        return True
    else:
        raise ValidationError('Enter Valid Last name')


def validate_name(value):
    if re.match(r'^([A-Za-z]{1,30}[ ]{1}|[A-Za-z]{1,30})*$', value):
        return True
    else:
        raise ValidationError('Enter Valid Name')

def validate_christ_email(value):
    if re.match(r'^[a-zA-Z]{3,20}[.][a-zA-Z]{1,20}[@][a-zA-Z]{2,8}.(((christuniversity)|(Christuniversity)).((in)|(com)))$', value) or re.match(r'^[a-zA-Z]{3,20}[.][a-zA-Z]{1,20}[@](((christuniversity)|(Christuniversity)).((in)|(com)))$', value) :
        return True
    else:
        raise ValidationError('Enter valid Christ email address!')

def validate_mobile(value):
    if re.match(r'^[6-9]{1}[0-9]{9}$', value):
        return True
    else:
        raise ValidationError('Enter Valid mobile number')

def validate_regno(value):
    if re.match(r'^[2-9]{1}[0-9]{6,8}$', value):
        return True
    else:
        raise ValidationError('Enter Valid Register number')

def validate_class_section(value):
    if re.match(r'^([1-9]( )[a-zA-Z]{3,4}( )[a-zA-Z]{1})$|^([1-9]( )[a-zA-Z]{3,4}( )*)$', value):
        return True
    else:
        raise ValidationError('Enter the Semester number class and section (optional) with one space in between')

def validate_class_section(value):
    if re.match(r'^([1-9]( )[a-zA-Z]{3,4}( )[a-zA-Z]{1})$|^([1-9]( )[a-zA-Z]{3,4}( )*)$', value):
        return True
    else:
        raise ValidationError('Enter the Semester number class and section (optional) with one space in between')

def validate_seven_days(value):
    print(datetime.datetime.now())

    from_date = datetime.datetime.today().date()
    to_date   = value
    print(to_date)
    result = to_date - from_date

    if result.days>7:
        return True
    else:
        raise ValidationError('Select a date 7 ahead days from today !')


#_________________________________________________________________roles table____________________________________________________________
class rolestbl(models.Model):
    roles = models.CharField(max_length=30,null=False,unique=True)

    def __str__(self):
        return (self.roles)

#_________________________________________________________________campus table____________________________________________________________
class campustbl(models.Model):
    campus= models.CharField(max_length=50,null=False,verbose_name="Campus")

    def __str__(self):
        return (self.campus)

#_________________________________________________________________department table_______________________________________________________
class depttbl(models.Model):
    dept = models.CharField(max_length=50,null=False,verbose_name="Department")

    def __str__(self):
        return (self.dept)

#_________________________________________________________________course table___________________________________________________________
class coursetbl(models.Model):
    course=models.CharField(max_length=70,null=False, verbose_name="coursename")

    def __str__(self):
        return (self.course)

#_______________________________________________________________customizing user table________________________________________________
class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(('first name'), max_length=30, null=False, validators =[validate_fname])
    last_name = models.CharField(('last name'), max_length=30, null=False, validators =[validate_lname])
    mobile = models.CharField(max_length=10, verbose_name="mobile", null=False, validators =[validate_mobile])
    email = models.EmailField(('email address'), unique=True, null=False, validators =[validate_christ_email])
    usercreated_date = models.DateTimeField(('date joined'), auto_now_add=True)
    is_active = models.BooleanField(('active'), default=True)
    roles = models.ForeignKey(rolestbl,null=True, on_delete=models.SET_NULL )
    campus =models.ForeignKey(campustbl,null=True, on_delete=models.SET_NULL )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


#_________________________________________________________________student head and volunteer profile table___________________________________________________________
#(common profile table used for both studenthead and volunteer)
class stuhead_vol_profiletbl(models.Model):

    WING_CHOICES= (
        ('One-to-One', 'One-To-One'),
        ('group', 'group'),
        )

    user = models.OneToOneField(User,on_delete=models.PROTECT)
    regno = models.CharField(max_length=10, verbose_name="Register number" ,blank = False, validators =[validate_regno] )
    course =models.ForeignKey(coursetbl,null=True, on_delete=models.SET_NULL )
    wing=models.CharField(max_length=20, choices=WING_CHOICES, verbose_name="Wing")
    sh_year=models.DateField(verbose_name="Year of being Studenthead", null=True)
    v_year=models.DateField(verbose_name="Year of being Volunteer", null=True)
    class_sec=models.CharField(max_length=20, verbose_name="Class & section" ,validators =[validate_class_section])
    passout=models.PositiveIntegerField(default=0,blank=True, verbose_name="Passout")
    total_session_hrs=models.PositiveIntegerField(default=0, verbose_name="Total_session_hrs_taken")
    no_of_sessions_conducted=models.PositiveIntegerField(default=0,verbose_name="Numberofsessionsconducted")

    def __str__(self):
        return self.user.email

# -------------------------------------------------- Session table ------------------------------------------------------
class sessiontbl(models.Model):
    session= models.CharField(max_length=30, verbose_name="session")
    description= models.CharField(max_length=200, verbose_name="description")
    session_pic=models.ImageField(null=True, blank=True,upload_to='media/sessionimages', verbose_name="Photo")
    uploaded_date=models.DateTimeField( auto_now_add=True, verbose_name="Uploaded_date")

    def __str__(self):
        return self.session

#___________________________________________________ one to one session request table____________________________________________________________
class onetoonetickettbl(models.Model):
    ONETICKET_STATUS_CHOICES= (
        ('requested', 'requested'),
        ('assigned', 'assigned'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('work-in-progress', 'work-in-progress'),
        ('closed', 'closed'),
        )

    session = models.ForeignKey(sessiontbl,null=True, blank=True, on_delete=models.PROTECT )
    other = models.BooleanField(default=False,verbose_name="Need a new session other than the listed sessions?")
    other_desc = models.TextField(max_length=500, null=True, blank=True,verbose_name="The new session description")
    
    name = models.CharField(('Name'), max_length=30, null=False, validators =[validate_name])
    stuemail =models.EmailField(('email address'), null=False, validators =[validate_christ_email])
    mobile = models.CharField( max_length=10, null=False, validators =[validate_mobile])

    course=models.ForeignKey(coursetbl,null=True, on_delete=models.PROTECT )
    dept=models.ForeignKey(depttbl,null=True, on_delete=models.PROTECT )
    campus=models.ForeignKey(campustbl,null=True, on_delete=models.PROTECT )
    regno= models.CharField( max_length=8, null=False, validators =[validate_regno],verbose_name="Register Number")

    hours=models.PositiveIntegerField( blank=True, default = 0, verbose_name="Hours of session conducted")
    ticket_no=models.CharField(max_length=10, null=True, blank=True)
    ticket_status=models.CharField(max_length=50, choices=ONETICKET_STATUS_CHOICES, verbose_name="Status")
    request_datetime=models.DateTimeField( auto_now_add=True, verbose_name="Request datetime")
    v_feedback=models.TextField(max_length=500, null=True, blank=True, verbose_name="Volunteer Feedback")
    s_feedback=models.TextField(max_length=500, null=True, blank=True, verbose_name="Student Feedback")
    feedback_otp = models.CharField(max_length=6, null=True, blank=True, verbose_name="Feedback OTP")

    accepted_date=models.DateTimeField( auto_now_add=False, verbose_name="Accepted_date", null=True, blank= True)

    accepted_by=models.ForeignKey(User, limit_choices_to={'is_active':True},null=True, blank=True, related_name="accept" ,on_delete=models.SET_NULL )
    assigned_by=models.ForeignKey(User,limit_choices_to={'is_active':True},null=True, blank=True,related_name="assign" , on_delete=models.SET_NULL )
    assigned_date = models.DateTimeField( auto_now_add=False, verbose_name="Assigned date", null=True, blank= True)
    assigned_to=models.ForeignKey(User,limit_choices_to={'is_active':True,'roles':3},null=True, blank=True,related_name="reject" , on_delete=models.SET_NULL )
    assigned_count=models.PositiveIntegerField( blank=True, default =0)
    rejected_by=models.ManyToManyField(User,blank=True, related_name="rejected" )
    closed_date=models.DateTimeField(  verbose_name="Closed_date", null=True,blank=True,)


    def __str__(self):
        return str(self.ticket_no)+self.name

#___________________________________________________ Peer group session request table____________________________________________________________
class peergrouptickettbl(models.Model):
    ONETICKET_STATUS_CHOICES= (
        ('requested', 'requested'),
        ('assigned', 'assigned'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('closed', 'closed'),
        ('halfassigned', 'halfassigned'),
        )

    session = models.ForeignKey(sessiontbl,null=True, blank=True, on_delete=models.PROTECT )
    other = models.BooleanField(default=False,verbose_name="Need a new session other than the listed sessions?")
    other_desc = models.TextField(max_length=500, null=True, blank=True,verbose_name="The new session description")
    
    name = models.CharField(('Name'), max_length=30, null=False, validators =[validate_name])
    facultyemail =models.EmailField(('email address'), null=False)
    mobile = models.CharField( max_length=10, null=False)

    course=models.ForeignKey(coursetbl,null=True, on_delete=models.PROTECT)
    dept=models.ForeignKey(depttbl,null=True, on_delete=models.PROTECT)
    campus=models.ForeignKey(campustbl,null=True, on_delete=models.PROTECT)
    sessiondate = models.DateField(auto_now_add=False, verbose_name="Request_date",validators =[validate_seven_days])
    sessiontime = models.TimeField(auto_now_add=False, verbose_name="Request_time")

    hours=models.PositiveIntegerField( blank=True, default =1)
    ticket_no=models.CharField(max_length=10, null=True, blank=True)
    ticket_status=models.CharField(max_length=50, choices=ONETICKET_STATUS_CHOICES, verbose_name="Status")
    request_datetime=models.DateTimeField( auto_now_add=True, verbose_name="Request_datetime")
    
    v_feedback=models.TextField(max_length=500, null=True, blank=True, verbose_name="Volunteer Feedback")
    s_feedback=models.TextField(max_length=500, null=True, blank=True, verbose_name="Student Feedback")
    feedback_otp = models.CharField(max_length=6, null=True, blank=True, verbose_name="Feedback OTP")
    accepted_date=models.DateTimeField( auto_now_add=False, verbose_name="Accepted_date", null=True, blank= True)

    assigned_date = models.DateTimeField( auto_now_add=False, verbose_name="Assigned date", null=True, blank= True)

    accepted_by = models.ManyToManyField(User,blank=True,limit_choices_to={'is_active':True}, related_name="grp_accepted" )
    # accepted_by=models.ForeignKey(User, limit_choices_to={'is_active':True},null=True, blank=True, related_name="accept" ,on_delete=models.SET_NULL )
    assigned_by=models.ForeignKey(User,null=True, blank=True,related_name="grp_assign" , on_delete=models.SET_NULL )
    assigned_to=models.ManyToManyField(User,blank=True,limit_choices_to={'is_active':True,'roles':3}, related_name="grp_assigned" )
    assigned_count=models.PositiveIntegerField( blank=True, default =0)
    accepted_count=models.PositiveIntegerField( blank=True, default =0)

    rejected_by=models.ManyToManyField(User, blank=True, related_name="grp_rejected" )
    closed_date=models.DateTimeField(  verbose_name="Closed_date", null=True,blank=True,)

    def __str__(self):
        return str(self.ticket_no)
