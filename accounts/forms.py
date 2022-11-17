from dataclasses import fields
from pyexpat import model
from django.forms import forms,ModelForm
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import depttbl,coursetbl,campustbl,  rolestbl, User, stuhead_vol_profiletbl
from .models import onetoonetickettbl,sessiontbl,peergrouptickettbl

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ dept  form ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class deptaddform(ModelForm):
    class Meta:
        model = depttbl
        fields = '__all__'

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ dept  form ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class courseaddform(ModelForm):
    class Meta:
        model =coursetbl
        fields = '__all__'


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^campus  form ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class campusaddform(ModelForm):
    class Meta:
        model =campustbl
        fields = '__all__'

#------------------------------------------------------------------------
class UserAddForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserAddForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = [ 'email','first_name', 'last_name', 'mobile', 'password1', 'password2','campus']

        widgets = {
            'email' : forms.EmailInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Email address'}),
            'first_name' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'First name'}),
            'last_name' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'last name'}),
            'mobile' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Mobile'}),
            'password1' : forms.TextInput(attrs={'class': 'form-control', 'type': 'password', 'placeholder':'your password'}),
            'password2' : forms.TextInput(attrs={'class': 'form-control', 'type': 'password', 'placeholder':'your password again'}),
            'campus' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'campus' ,'aria-label':"Default select example"}),
        }

    # def save(self, commit=True):
    #     # Save the provided password in hashed format
    #     user = super(UserCreationForm, self).save(commit=False)
    #     user.set_password(self.cleaned_data["password"])
    #     if commit:
    #         user.save()
    #     return user

# this form is used for both volunteer add and student head add form
class VolunteerAddForm(ModelForm):
    class Meta:
        model = stuhead_vol_profiletbl
        fields = [ 'course', 'class_sec', 'wing', 'regno', 'passout']

        widgets = {
            
            'course' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'course'}),
            'wing' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'wing'}),
            'class_sec' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Class and section'}),   
            'regno' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Regno'}),
            'passout' : forms.NumberInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Passout'}),
        }

class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile','campus',]

        widgets = {
            'first_name' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'First name'}),
            'last_name' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'last name'}),
            'mobile' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Mobile'}),
            'campus' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'campus' ,'aria-label':"Default select example"}),
        }

class VolunteerEditForm(ModelForm):

    class Meta:
        model = stuhead_vol_profiletbl
        fields = [ 'course', 'class_sec', 'wing', 'regno', 'passout']

        widgets = {
            'course' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'course'}),
            'wing' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'wing'}),
            'class_sec' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Class and section'}),   
            'regno' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Regno'}),
            'passout' : forms.NumberInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Passout'}),
        }


# class MentorAddForm(ModelForm):
#     class Meta:
#         model = mentortbl
#         fields = ['campus']

#         widgets = {
#             'campus' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'campus' ,'aria-label':"Default select example"}), 
#         }

# ---------------------------------------------------------- session tables
    
class sessionaddform(ModelForm):
    class Meta:
        model =sessiontbl
        fields = '__all__'


class OtoAssignForm(forms.ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = ['assigned_to']


class OtoVolFeedbackForm(forms.ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = ['v_feedback','hours']

        widgets = {
            'v_feedback' : forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Volunteer feedback'}),
            'hours' : forms.NumberInput(attrs={'class': 'form-control', 'type': 'textarea', 'placeholder':'Hours of session'}),
        }

class OtoFeedbackForm1(forms.ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = '__all__'


class OtoAssignForm(forms.ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = ['assigned_to']


class OtoBookingForm(forms.ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = ['session','other','other_desc', 'name', 'stuemail', 'mobile', 'course', 'dept', 'campus', 'regno']

        widgets = {
            'session' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'session name'}),
            'other' : forms.CheckboxInput(attrs={ 'type': 'checkbox'}),
            'other_desc' : forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Description of the new session'}),
            'name' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'your Name'}),
            'stuemail' : forms.TextInput(attrs={'class': 'form-control', 'type': 'email', 'placeholder':'your christ-email id'}),
            'mobile' : forms.NumberInput(attrs={'class': 'form-control', 'type': 'text', 'pattern':"^[6-9]{1}[0-9]{9}$",'placeholder':'your mobile number'}),
            'course' : forms.Select(attrs={'class': 'form-control', 'type': 'text'}),
            'dept' : forms.Select(attrs={'class': 'form-control', 'type': 'text'}),
            'campus' : forms.Select(attrs={'class': 'form-control', 'type': 'text'}),
            'regno' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'your register number'}),
        }

# ------------------------- peer group session forms -------------------------------------------------------------
class GrpBookingForm(forms.ModelForm):
    class Meta:
        model = peergrouptickettbl
        fields = ['session','other','other_desc', 'name', 'facultyemail', 'mobile', 'course', 'dept', 'campus', 'sessiondate', 'sessiontime']

        widgets = {
            'sessiondate': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'sessiontime': forms.TimeInput(attrs={'class': 'form-control', 'type':'time'}),
        
            'session' : forms.Select(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'session name'}),
            'other' : forms.CheckboxInput(attrs={ 'type': 'checkbox'}),
            'other_desc' : forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Description of the new session'}),
            'name' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'your Name'}),
            'facultyemail' : forms.TextInput(attrs={'class': 'form-control', 'type': 'email', 'placeholder':'your christ-email id'}),
            'mobile' : forms.NumberInput(attrs={'class': 'form-control', 'type': 'text', 'pattern':"^[6-9]{1}[0-9]{9}$",'placeholder':'your mobile number'}),
            'course' : forms.Select(attrs={'class': 'form-control', 'type': 'text'}),
            'dept' : forms.Select(attrs={'class': 'form-control', 'type': 'text'}),
            'campus' : forms.Select(attrs={'class': 'form-control', 'type': 'text'}),
            'regno' : forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'your register number'}),
        }

class GroupVolFeedbackForm(forms.ModelForm):
    class Meta:
        model = peergrouptickettbl
        fields = ['v_feedback', 'hours']



# form to assign volunteers to group sessions
class GroupAssignForm(forms.ModelForm):
    class Meta:
        model = peergrouptickettbl
        fields = ['assigned_to']

class GroupAssignForm2(forms.Form):
    vol1 = forms.ChoiceField(widget=forms.TextInput(attrs={'type':'text', 'class':'form-control'}),)
    vol2 = forms.ChoiceField(widget=forms.TextInput(attrs={'type':'text', 'class':'form-control'}),)
    vol3 = forms.ChoiceField(widget=forms.TextInput(attrs={'type':'text', 'class':'form-control'}),)
    vol4 = forms.ChoiceField(widget=forms.TextInput(attrs={'type':'text', 'class':'form-control'}),)

    widgets = {
        'vol1':forms.Select(attrs={'id':'v1id','type':'text'}),
        'vol2':forms.Select(attrs={'id':'v2id'}),
        'vol3':forms.Select(attrs={'id':'v3id'}),
        'vol4':forms.Select(attrs={'id':'v4id'})
    }


# ----------------------- Feedbac forms
class VerificationForm(forms.Form):

    WING_CHOICES= (
    ('One-to-One', 'One-To-One'),
    ('group', 'group'),
    )

    ticket_no = forms.CharField(max_length=10,widget=forms.TextInput(attrs={'id':'v1id','type':'text', 'class':'form-control'}),)
    email_id = forms.CharField(max_length=50,widget = forms.TextInput(attrs={'id':'v1id','type':'email', 'class':'form-control'}),)
    session_type = forms.ChoiceField(choices=WING_CHOICES, widget =forms.Select(attrs={'id':'v1id','type':'text', 'class':'form-control'}),)

    # widgets = {
    #     'ticket_no':forms.TextInput(attrs={'type':'text', 'class':'form-control'}),
    #     'email_id':forms.EmailField(attrs={'type':'email', 'class':'form-control'}),
    #     'session_type':forms.Select(attrs={'type':'text', 'class':'form-control'}),
    # }

class OtpForm(forms.Form):
    otp = forms.CharField(max_length=7,widget=forms.TextInput(attrs={'id':'v1id','type':'text', 'class':'form-control'}),)

class FeedbackForm(forms.Form):
    feedback = forms.CharField(max_length=500),
    widgets = {
        'feedback':forms.Textarea(attrs={'id':'v1id','type':'text', 'class':'form-control'}),
    }

class OtoFeedbackForm(forms.ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = ['s_feedback']

    widgets = {
        's_feedback' : forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Student feedback'}),
    }

class GroupFeedbackForm(forms.ModelForm):
    class Meta:
        model = peergrouptickettbl
        fields = ['s_feedback']

    widgets = {
        's_feedback' : forms.Textarea(attrs={'class': 'form-control', 'type': 'text', 'placeholder':'Student feedback'}),
    }


class OtoReportForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type':'date'})),
    to_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type':'date'})),


class profileaddform(ModelForm):
    class Meta:
        model = onetoonetickettbl
        fields = '__all__'

# ---------- Search form for user report generation function---------------
class UserSearchForm(forms.Form):
    search_key = forms.CharField(max_length=25,widget=forms.TextInput(attrs={'id':'searchkeyid','type':'text', 'class':'form-control'}),)
